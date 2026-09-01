from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import anyio

from domain_intelligence.capture.archive import write_capture_inventory, write_source_snapshots
from domain_intelligence.capture.contracts import (
    MAX_BODY_BYTES,
    CaptureContext,
    CaptureOutcome,
    CaptureTarget,
    source_signals,
)
from domain_intelligence.capture.planning import (
    blocked_outcome,
    source_blocker,
    source_run,
    targets_for_source,
)
from domain_intelligence.capture.transport import fetch_targets
from domain_intelligence.daily import canonical_url
from domain_intelligence.models import (
    AcquisitionBatch,
    AcquisitionMethod,
    BootstrapInput,
    ContentCaptureStatus,
    DailySignal,
    SourceProfile,
)


def _feed_targets(
    source: SourceProfile,
    outcomes: tuple[CaptureOutcome, ...],
    signals: tuple[DailySignal, ...],
    window_start: datetime,
    as_of: datetime,
) -> tuple[CaptureTarget, ...]:
    if source.acquisition.method not in {AcquisitionMethod.RSS, AcquisitionMethod.ATOM}:
        return ()
    explicit_urls = {canonical_url(signal.url) for signal in signals}
    endpoint = source.acquisition.endpoint
    seen_urls = explicit_urls | ({canonical_url(endpoint)} if endpoint else set())
    result: list[CaptureTarget] = []
    for outcome in outcomes:
        if outcome.artifact.status is not ContentCaptureStatus.CAPTURED:
            continue
        for item in outcome.feed_items:
            if item.published_at is None:
                continue
            if not window_start <= item.published_at <= as_of:
                continue
            item_url = canonical_url(item.url)
            if item_url in seen_urls:
                continue
            seen_urls.add(item_url)
            result.append(CaptureTarget(source, item.url, None, None, item))
    return tuple(result)


def _append_outcomes(
    outcomes_by_source: dict[str, list[CaptureOutcome]],
    source_ids: list[str],
    outcomes: tuple[CaptureOutcome, ...],
) -> None:
    for source_id, outcome in zip(source_ids, outcomes, strict=True):
        outcomes_by_source.setdefault(source_id, []).append(outcome)


def _initial_capture(
    inputs: BootstrapInput,
) -> tuple[dict[str, list[CaptureOutcome]], tuple[CaptureTarget, ...], list[str]]:
    evidence_by_id = {record.id: record for record in inputs.evidence}
    signals_by_source = source_signals(inputs)
    outcomes_by_source: dict[str, list[CaptureOutcome]] = {}
    targets: list[CaptureTarget] = []
    source_ids: list[str] = []
    for source in inputs.attention_graph.sources:
        blocker = source_blocker(source)
        if blocker is not None:
            blocked = blocked_outcome(source, blocker, inputs.as_of)
            outcomes_by_source[str(source.id)] = [blocked] if blocked else []
            continue
        source_targets = targets_for_source(
            source,
            signals_by_source.get(str(source.id), ()),
            evidence_by_id,
        )
        targets.extend(source_targets)
        source_ids.extend(str(source.id) for _ in source_targets)
    return outcomes_by_source, tuple(targets), source_ids


def _tuple_outcomes(
    outcomes_by_source: dict[str, list[CaptureOutcome]],
) -> dict[str, tuple[CaptureOutcome, ...]]:
    return {source_id: tuple(outcomes) for source_id, outcomes in outcomes_by_source.items()}


def capture_public_sources(
    inputs: BootstrapInput,
    capture_root: Path,
    *,
    max_body_bytes: int = MAX_BODY_BYTES,
) -> AcquisitionBatch:
    capture_root.mkdir(parents=True, exist_ok=True)
    outcomes_by_source, initial_targets, initial_source_ids = _initial_capture(inputs)
    context = CaptureContext(capture_root, inputs.as_of, max_body_bytes)
    initial_outcomes = anyio.run(fetch_targets, initial_targets, context)
    _append_outcomes(outcomes_by_source, initial_source_ids, initial_outcomes)

    sources = tuple(sorted(inputs.attention_graph.sources, key=lambda item: str(item.id)))
    signals_by_source = source_signals(inputs)
    window_start = inputs.as_of - timedelta(hours=inputs.window_hours)
    feed_targets: list[CaptureTarget] = []
    feed_source_ids: list[str] = []
    current_outcomes = _tuple_outcomes(outcomes_by_source)
    for source in sources:
        selected = _feed_targets(
            source,
            current_outcomes.get(str(source.id), ()),
            signals_by_source.get(str(source.id), ()),
            window_start,
            inputs.as_of,
        )
        feed_targets.extend(selected)
        feed_source_ids.extend(str(source.id) for _ in selected)
    feed_outcomes = anyio.run(fetch_targets, tuple(feed_targets), context)
    _append_outcomes(outcomes_by_source, feed_source_ids, feed_outcomes)
    final_outcomes = _tuple_outcomes(outcomes_by_source)
    write_source_snapshots(capture_root, sources, final_outcomes)
    artifacts = tuple(
        outcome.artifact for source in sources for outcome in final_outcomes.get(str(source.id), ())
    )
    evidence = tuple(
        outcome.evidence
        for source in sources
        for outcome in final_outcomes.get(str(source.id), ())
        if outcome.evidence is not None
    )
    write_capture_inventory(capture_root, inputs.as_of, artifacts)
    return AcquisitionBatch(
        runs=tuple(
            source_run(source, final_outcomes.get(str(source.id), ()), inputs.as_of)
            for source in sources
        ),
        evidence=evidence,
        contents=artifacts,
    )
