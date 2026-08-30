from __future__ import annotations

from enum import StrEnum
from typing import NewType

SourceId = NewType("SourceId", str)
ExpertId = NewType("ExpertId", str)
TopicId = NewType("TopicId", str)
ElementId = NewType("ElementId", str)
EventId = NewType("EventId", str)
NuggetId = NewType("NuggetId", str)
SignalId = NewType("SignalId", str)


class IntelligenceMode(StrEnum):
    DOMAIN_FOUNDATION = "domain_foundation"
    FOCUSED_WATCH = "focused_watch"


class SourceRole(StrEnum):
    OFFICIAL_PRIMARY = "official_primary"
    EXPERT_INTERPRETER = "expert_interpreter"
    FRONTIER_SENSOR = "frontier_sensor"
    BROAD_COVERAGE = "broad_coverage"
    COMMUNITY = "community"
    OTHER = "other"


class AcquisitionMethod(StrEnum):
    RSS = "rss"
    ATOM = "atom"
    JSON = "json"
    SITEMAP = "sitemap"
    STATIC_HTML = "static_html"
    API = "api"
    OPML = "opml"
    BROWSER = "browser"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class RelationType(StrEnum):
    EXPLICITLY_RECOMMENDS = "explicitly_recommends"
    CITES = "cites"
    FOLLOWS = "follows"
    STARS = "stars"
    LINKS_TO = "links_to"
    APPEARS_WITH = "appears_with"


class GapReason(StrEnum):
    NO_CAPABLE_SOURCE = "no_capable_source"
    INSUFFICIENT_SOURCE_COUNT = "insufficient_source_count"
    NO_APPROVED_SOURCE = "no_approved_source"
    NO_HISTORICAL_EVIDENCE = "no_historical_evidence"
    NO_ACQUISITION_PATH = "no_acquisition_path"
    INSUFFICIENT_ROLE_DIVERSITY = "insufficient_role_diversity"
