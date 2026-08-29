from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from domain_intelligence.models import (
    DailyBrief,
    DailyBriefInput,
    DailySignal,
    DailyStory,
    DomainProfile,
    SourceProfile,
    SourceRole,
)

TITLE_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+", re.IGNORECASE)
TITLE_SIMILARITY_THRESHOLD = 0.65
FIRST_PARTY_ORIGINALITY_THRESHOLD = 0.8
ROLE_RANKS = {
    SourceRole.OFFICIAL_PRIMARY: 1.0,
    SourceRole.EXPERT_INTERPRETER: 0.9,
    SourceRole.FRONTIER_SENSOR: 0.85,
    SourceRole.BROAD_COVERAGE: 0.6,
    SourceRole.COMMUNITY: 0.55,
    SourceRole.OTHER: 0.5,
}


def canonical_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    query = tuple(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid", "ref"}
    )
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            urlencode(sorted(query)),
            "",
        )
    )


def _tokens(title: str) -> set[str]:
    return {token.lower() for token in TITLE_TOKEN_RE.findall(title)}


def _similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def _same_story(left: DailySignal, right: DailySignal) -> bool:
    if canonical_url(left.url) == canonical_url(right.url):
        return True
    if left.event_id is not None and right.event_id is not None:
        return left.event_id == right.event_id
    return (
        left.event_type == right.event_type
        and _similarity(left.title, right.title) >= TITLE_SIMILARITY_THRESHOLD
    )


def _cluster(signals: tuple[DailySignal, ...]) -> tuple[tuple[DailySignal, ...], ...]:
    clusters: list[list[DailySignal]] = []
    for signal in signals:
        match = next((cluster for cluster in clusters if _same_story(signal, cluster[0])), None)
        if match is None:
            clusters.append([signal])
        else:
            match.append(signal)
    return tuple(tuple(cluster) for cluster in clusters)


def _topic_relevance(profile: DomainProfile, signal: DailySignal) -> float:
    weights = {item.topic_id: item.weight for item in profile.topic_weights}
    if not weights:
        return 0.5
    return max((weights.get(topic_id, 0.0) for topic_id in signal.topic_ids), default=0.0)


def _priority(profile: DomainProfile, event_type: str) -> float:
    priorities = {item.event_type: item.weight for item in profile.event_priorities}
    return priorities.get(event_type, 0.35)


def _primary_signal(
    cluster: tuple[DailySignal, ...], sources: dict[str, SourceProfile]
) -> DailySignal:
    return max(
        cluster,
        key=lambda signal: (
            signal.originality,
            ROLE_RANKS[sources[str(signal.source_id)].role],
            sources[str(signal.source_id)].authority,
            signal.published_at,
        ),
    )


def _story(
    profile: DomainProfile,
    cluster: tuple[DailySignal, ...],
    sources: dict[str, SourceProfile],
    as_of: datetime,
) -> DailyStory:
    primary = _primary_signal(cluster, sources)
    source_ids = tuple(
        dict.fromkeys(
            signal.source_id
            for signal in sorted(
                cluster,
                key=lambda signal: (
                    -ROLE_RANKS[sources[str(signal.source_id)].role],
                    -sources[str(signal.source_id)].authority,
                    -signal.originality,
                ),
            )
        ),
    )
    signal_ids = tuple(signal.id for signal in cluster)
    topic_ids = tuple(sorted({topic_id for signal in cluster for topic_id in signal.topic_ids}))
    source_quality = max(
        (
            0.5 * sources[str(signal.source_id)].authority
            + 0.5 * sources[str(signal.source_id)].reliability
            for signal in cluster
        ),
        default=0.0,
    )
    corroboration = min(1.0, len(source_ids) / 3)
    originality = max((signal.originality for signal in cluster), default=0.0)
    age_hours = max(
        0.0, (as_of - max(signal.published_at for signal in cluster)).total_seconds() / 3600
    )
    freshness = max(0.0, 1.0 - age_hours / 24)
    score = (
        0.2 * _priority(profile, primary.event_type)
        + 0.2 * source_quality
        + 0.2 * corroboration
        + 0.15 * originality
        + 0.1 * _topic_relevance(profile, primary)
        + 0.1 * freshness
        + 0.05 * primary.importance
    )
    story_key = "|".join(sorted(canonical_url(signal.url) for signal in cluster))
    story_id = hashlib.sha256(story_key.encode("utf-8")).hexdigest()[:12]
    return DailyStory(
        id=story_id,
        title=primary.title,
        primary_source_id=primary.source_id,
        source_ids=source_ids,
        signal_ids=signal_ids,
        topic_ids=topic_ids,
        event_type=primary.event_type,
        score=round(min(1.0, score), 6),
        corroboration=round(corroboration, 6),
        first_party=any(
            sources[str(signal.source_id)].role is SourceRole.OFFICIAL_PRIMARY
            or signal.originality >= FIRST_PARTY_ORIGINALITY_THRESHOLD
            for signal in cluster
        ),
        evidence_urls=tuple(dict.fromkeys(signal.url for signal in cluster)),
    )


def build_daily_brief(inputs: DailyBriefInput) -> DailyBrief:
    window_start = inputs.as_of - timedelta(hours=inputs.window_hours)
    eligible = tuple(
        signal for signal in inputs.signals if window_start <= signal.available_at <= inputs.as_of
    )
    sources = {str(source.id): source for source in inputs.sources}
    stories = tuple(
        sorted(
            (
                _story(inputs.profile, cluster, sources, inputs.as_of)
                for cluster in _cluster(eligible)
            ),
            key=lambda item: (-item.score, item.id),
        )
    )
    return DailyBrief(
        generated_at=inputs.as_of,
        window_start=window_start,
        domain=inputs.profile.domain,
        stories=stories[: inputs.limit],
    )
