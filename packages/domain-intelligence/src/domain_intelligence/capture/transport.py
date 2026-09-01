from __future__ import annotations

import hashlib
import logging
import socket
import time
from datetime import datetime
from urllib.parse import urlparse

import anyio
import httpx2

from domain_intelligence.capture.archive import (
    content_id,
    failure,
    normalize_content_text,
    write_capture_files,
)
from domain_intelligence.capture.contracts import (
    CaptureContext,
    CapturedDocument,
    CaptureOutcome,
    CaptureTarget,
)
from domain_intelligence.capture_parser import parse_document
from domain_intelligence.feed_discovery import FeedParseError, discover_feed_items
from domain_intelligence.models import (
    AcquisitionMethod,
    ContentArtifact,
    ContentCaptureStatus,
    DailySignal,
    EvidenceRecord,
    SourceRole,
)

LOGGER = logging.getLogger(__name__)
LIMITS = httpx2.Limits(
    max_connections=200,
    max_keepalive_connections=40,
    keepalive_expiry=30.0,
)
TIMEOUT = httpx2.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0)
SOCKET_OPTIONS: list[tuple[int, int, int]] = [
    (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
]


async def _request_started(request: httpx2.Request) -> None:
    request.extensions["capture_started_at"] = time.perf_counter()


async def _response_received(response: httpx2.Response) -> None:
    started = response.request.extensions.get("capture_started_at")
    elapsed = time.perf_counter() - started if isinstance(started, float) else 0.0
    LOGGER.info(
        "captured %s %s -> %s in %.2fs (%s)",
        response.request.method,
        response.request.url,
        response.status_code,
        elapsed,
        response.http_version,
    )


def _create_client() -> httpx2.AsyncClient:
    transport = httpx2.AsyncHTTPTransport(
        http2=True,
        retries=3,
        limits=LIMITS,
        socket_options=SOCKET_OPTIONS,
    )
    return httpx2.AsyncClient(
        transport=transport,
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={
            "User-Agent": "PrivateIntelligenceObservatory/0.1 public-capture",
            "Accept": "text/html,application/json,application/xml;q=0.9,*/*;q=0.1",
        },
        event_hooks={"request": [_request_started], "response": [_response_received]},
    )


def _content_type(response: httpx2.Response) -> str:
    return response.headers.get("content-type", "application/octet-stream").split(";", 1)[0]


def _is_feed_endpoint(target: CaptureTarget) -> bool:
    return (
        target.feed_item is None
        and target.source.acquisition.method in {AcquisitionMethod.RSS, AcquisitionMethod.ATOM}
        and target.url == target.source.acquisition.endpoint
    )


def _feed_signal(target: CaptureTarget) -> DailySignal | None:
    item = target.feed_item
    if item is None or item.published_at is None:
        return None
    return DailySignal(
        id="feed-"
        + hashlib.sha256(
            f"{target.source.id}|{item.identity}|{item.url}".encode(),
        ).hexdigest()[:16],
        source_id=target.source.id,
        title=item.title,
        url=item.url,
        published_at=item.published_at,
        available_at=item.published_at,
        topic_ids=target.source.topic_ids,
        importance=target.source.authority,
        summary=item.summary,
        originality=0.8 if target.source.role is SourceRole.OFFICIAL_PRIMARY else 0.6,
    )


def _effective_signal(target: CaptureTarget) -> DailySignal | None:
    if target.feed_item is not None:
        return _feed_signal(target)
    if _is_feed_endpoint(target):
        return None
    return target.signal


def _evidence_from_capture(
    target: CaptureTarget,
    document: CapturedDocument,
    as_of: datetime,
) -> EvidenceRecord | None:
    signal = _effective_signal(target)
    if signal is None or not document.text.strip() or signal.available_at > as_of:
        return None
    summary = signal.summary or document.text[:400]
    return EvidenceRecord(
        id=signal.id,
        source_id=signal.source_id,
        title=signal.title,
        url=signal.url,
        summary=summary,
        published_at=signal.published_at,
        available_at=signal.available_at,
        retrieved_at=as_of,
        content_hash=document.content_hash,
        topic_ids=signal.topic_ids,
        element_ids=(
            target.evidence_template.element_ids
            if target.evidence_template
            else target.source.element_ids
        ),
        event_type=signal.event_type,
        importance=signal.importance,
        originality=signal.originality,
        confirmed=signal.confirmed,
        event_id=signal.event_id,
        content_ref=document.relative_path,
        content_type=document.content_type,
        content_char_count=len(document.text),
    )


async def fetch_one(
    client: httpx2.AsyncClient,
    limiter: anyio.CapacityLimiter,
    target: CaptureTarget,
    context: CaptureContext,
) -> CaptureOutcome:
    async with limiter:
        parsed_url = urlparse(target.url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return failure(
                target,
                context.as_of,
                ContentCaptureStatus.BLOCKED,
                "INVALID_PUBLIC_URL",
            )
        try:
            response = await client.get(target.url)
            response.raise_for_status()
            body = response.content
            content_type = _content_type(response)
            if len(body) > context.max_body_bytes:
                return failure(
                    target,
                    context.as_of,
                    ContentCaptureStatus.FAILED,
                    "RESPONSE_TOO_LARGE",
                    content_type,
                )
            encoding = response.encoding or "utf-8"
            raw_text = body.decode(encoding, errors="replace")
            feed_items = ()
            discovery_error_code = None
            if _is_feed_endpoint(target):
                try:
                    feed_items = discover_feed_items(
                        raw_text,
                        target.source.acquisition.method,
                        target.url,
                    )
                except FeedParseError as error:
                    discovery_error_code = error.error_code
            parsed = parse_document(raw_text, content_type, body)
            parsed_text = raw_text.strip() if not parsed.text else parsed.text
            archived_text = normalize_content_text(parsed_text)
            content_hash = f"sha256:{hashlib.sha256(archived_text.encode()).hexdigest()}"
            relative_path, raw_relative_path = write_capture_files(
                context.capture_root,
                target,
                body,
                archived_text,
                content_type,
            )
            document = CapturedDocument(archived_text, content_type, content_hash, relative_path)
            evidence = _evidence_from_capture(target, document, context.as_of)
            feed_published_at = target.feed_item.published_at if target.feed_item else None
            signal = _effective_signal(target)
            title = (
                target.feed_item.title
                if target.feed_item is not None
                else signal.title
                if signal is not None
                else parsed.title
            ) or target.source.name
            artifact = ContentArtifact(
                id=content_id(target),
                source_id=target.source.id,
                evidence_id=evidence.id if evidence else None,
                title=title,
                url=target.url,
                published_at=feed_published_at or parsed.published_at,
                captured_at=context.as_of,
                content_type=content_type,
                relative_path=relative_path,
                raw_relative_path=raw_relative_path,
                content_hash=content_hash,
                character_count=len(archived_text),
                status=ContentCaptureStatus.CAPTURED,
            )
            return CaptureOutcome(
                artifact=artifact,
                evidence=evidence,
                feed_items=feed_items,
                discovery_error_code=discovery_error_code,
            )
        except httpx2.HTTPStatusError as error:
            return failure(
                target,
                context.as_of,
                ContentCaptureStatus.FAILED,
                f"HTTP_{error.response.status_code}",
            )
        except httpx2.RequestError:
            return failure(target, context.as_of, ContentCaptureStatus.FAILED, "REQUEST_ERROR")
        except (OSError, UnicodeError, ValueError):
            return failure(
                target,
                context.as_of,
                ContentCaptureStatus.FAILED,
                "CONTENT_PARSE_ERROR",
            )


async def fetch_targets(
    targets: tuple[CaptureTarget, ...],
    context: CaptureContext,
) -> tuple[CaptureOutcome, ...]:
    limiter = anyio.CapacityLimiter(12)
    async with _create_client() as client, anyio.create_task_group() as task_group:
        handles = [
            task_group.create_task(fetch_one(client, limiter, target, context))
            for target in targets
        ]
        return tuple([await handle for handle in handles])
