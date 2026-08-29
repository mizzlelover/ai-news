from __future__ import annotations

from datetime import UTC, datetime, timedelta

from domain_intelligence.backtest import replay_benchmark
from domain_intelligence.coverage import audit_coverage
from domain_intelligence.daily import build_daily_brief
from domain_intelligence.graph import rank_attention_sources
from domain_intelligence.models import (
    AcquisitionCapability,
    AcquisitionMethod,
    AttentionEdge,
    AttentionGraph,
    AttentionQuery,
    BenchmarkEvent,
    CoverageInput,
    DailyBriefInput,
    DailySignal,
    DomainProfile,
    EssentialInformationElement,
    EventPriority,
    ExpertProfile,
    IntelligenceRequirement,
    Observation,
    PortfolioInput,
    ReplayInput,
    SourceBundle,
    SourceEvaluation,
    SourceProfile,
    SourceRole,
    StopRules,
    TemporalBenchmark,
)
from domain_intelligence.portfolio import optimize_portfolio

AS_OF = datetime(2026, 8, 30, 8, tzinfo=UTC)


def source(
    source_id: str,
    role: SourceRole,
    topics: tuple[str, ...],
    elements: tuple[str, ...] = (),
    cost: float = 1.0,
    authority: float = 0.7,
) -> SourceProfile:
    return SourceProfile(
        id=source_id,
        name=source_id,
        role=role,
        topic_ids=topics,
        element_ids=elements,
        cost=cost,
        authority=authority,
        reliability=0.8,
        accessibility=0.8,
        acquisition=AcquisitionCapability(
            method=AcquisitionMethod.RSS,
            endpoint=f"https://example.com/{source_id}.xml",
            stable=True,
        ),
    )


def test_attention_graph_prefers_cross_cluster_signal_over_popularity() -> None:
    graph = AttentionGraph(
        experts=(
            ExpertProfile(id="researcher", name="Researcher", community="research"),
            ExpertProfile(id="builder", name="Builder", community="builders"),
        ),
        sources=(
            source("hub", SourceRole.BROAD_COVERAGE, ("agents",), authority=0.95),
            source("niche", SourceRole.FRONTIER_SENSOR, ("agents",), authority=0.7),
        ),
        edges=(
            AttentionEdge(
                from_node_id="researcher",
                to_node_id="hub",
                relation="follows",
                observed_at=AS_OF - timedelta(days=1),
            ),
            AttentionEdge(
                from_node_id="builder",
                to_node_id="niche",
                relation="explicitly_recommends",
                observed_at=AS_OF - timedelta(days=1),
            ),
            AttentionEdge(
                from_node_id="researcher",
                to_node_id="niche",
                relation="cites",
                observed_at=AS_OF - timedelta(days=1),
            ),
        ),
    )

    result = rank_attention_sources(
        graph,
        AttentionQuery(
            seed_expert_ids=("researcher", "builder"), topic_ids=("agents",), as_of=AS_OF
        ),
    )

    assert result[0].source_id == "niche"
    assert result[0].cross_cluster_support == 1.0


def test_replay_honors_availability_time_at_each_cutoff() -> None:
    early = AS_OF - timedelta(days=2)
    late = AS_OF - timedelta(days=1)
    event = BenchmarkEvent(
        id="e1",
        title="Model release",
        nuggets=(
            {
                "id": "n1",
                "event_id": "e1",
                "label": "Official release",
                "importance": 1.0,
                "available_at": early,
                "authoritative_at": AS_OF,
            },
        ),
    )
    benchmark = TemporalBenchmark(
        events=(event,),
        sources=(source("official", SourceRole.OFFICIAL_PRIMARY, ("models",)),),
        observations=(
            Observation(
                id="o1",
                source_id="official",
                event_id="e1",
                nugget_id="n1",
                available_at=late,
                publication_at=late,
                is_original=True,
                is_confirmed=True,
                decision_utility=0.8,
            ),
        ),
        cutoffs=(early, late),
    )

    result = replay_benchmark(ReplayInput(benchmark=benchmark))

    early_cell = next(cell for cell in result.cells if cell.cutoff == early)
    late_cell = next(cell for cell in result.cells if cell.cutoff == late)
    assert early_cell.visible_source_ids == ()
    assert late_cell.visible_source_ids == ("official",)
    assert result.source_metrics[0].lead_time_hours == 24.0


def test_portfolio_can_select_a_complementary_bundle() -> None:
    hub = source("hub", SourceRole.BROAD_COVERAGE, ("t",), cost=1.0)
    first = source("first", SourceRole.OFFICIAL_PRIMARY, ("t",), cost=1.0)
    second = source("second", SourceRole.EXPERT_INTERPRETER, ("t",), cost=1.0)
    evaluations = (
        SourceEvaluation(source_id="hub", nugget_recall=0.95, covered_nugget_ids=("n1", "n2")),
        SourceEvaluation(source_id="first", nugget_recall=0.4, covered_nugget_ids=("n1",)),
        SourceEvaluation(source_id="second", nugget_recall=0.4, covered_nugget_ids=("n2",)),
    )

    result = optimize_portfolio(
        PortfolioInput(
            sources=(hub, first, second),
            evaluations=evaluations,
            bundles=(SourceBundle(id="pair", source_ids=("first", "second"), synergy_bonus=0.8),),
            budget=2.0,
            max_sources=2,
            total_nuggets=2,
        ),
    )

    assert result.selected_source_ids == ("first", "second")
    assert result.selected_bundle_ids == ("pair",)


def test_coverage_uses_declared_information_elements_as_denominator() -> None:
    profile = DomainProfile(
        domain="data-elements",
        decision_context="track policy and market movement",
        requirements=(
            IntelligenceRequirement(
                id="r1", question="What changed?", element_ids=("e1", "e2", "e3")
            ),
        ),
        elements=(
            EssentialInformationElement(id="e1", label="Policy", topic_id="policy"),
            EssentialInformationElement(id="e2", label="Market", topic_id="market"),
            EssentialInformationElement(id="e3", label="Overseas", topic_id="overseas"),
        ),
        event_priorities=(EventPriority(event_type="policy_change", weight=1.0),),
    )
    inputs = CoverageInput(
        profile=profile,
        sources=(
            source("policy", SourceRole.OFFICIAL_PRIMARY, ("policy",), ("e1",)),
            source("market", SourceRole.EXPERT_INTERPRETER, ("market",), ("e2",)),
        ),
        evaluations=(),
    )

    result = audit_coverage(inputs)

    assert result.total_elements == 3
    assert result.covered_elements == 2
    missing = next(row for row in result.rows if row.element_id == "e3")
    assert missing.gap_reasons == ("no_capable_source",)


def test_coverage_marks_insufficient_source_count() -> None:
    profile = DomainProfile(
        domain="agents",
        decision_context="track market movement",
        elements=(
            EssentialInformationElement(
                id="e1",
                label="Market",
                topic_id="market",
                required_source_count=2,
            ),
        ),
        stop_rules=StopRules(minimum_sources_per_element=1),
    )
    result = audit_coverage(
        CoverageInput(
            profile=profile,
            sources=(source("market", SourceRole.BROAD_COVERAGE, ("market",), ("e1",)),),
        ),
    )

    assert result.rows[0].coverage_ratio == 0.5
    assert "insufficient_source_count" in result.rows[0].gap_reasons


def test_daily_brief_deduplicates_and_applies_event_priority() -> None:
    profile = DomainProfile(
        domain="agents",
        decision_context="track material product changes",
        requirements=(),
        elements=(),
        event_priorities=(EventPriority(event_type="product_release", weight=1.0),),
    )
    signals = (
        DailySignal(
            id="s1",
            source_id="official",
            title="Agent 2 released",
            url="https://example.com/release?utm_source=x",
            published_at=AS_OF - timedelta(hours=1),
            available_at=AS_OF - timedelta(hours=1),
            topic_ids=("agents",),
            event_type="product_release",
            importance=0.8,
            originality=1.0,
        ),
        DailySignal(
            id="s2",
            source_id="expert",
            title="Agent 2 released today",
            url="https://another.example.com/agent-2",
            published_at=AS_OF - timedelta(minutes=30),
            available_at=AS_OF - timedelta(minutes=30),
            topic_ids=("agents",),
            event_type="product_release",
            importance=0.6,
        ),
    )

    result = build_daily_brief(
        DailyBriefInput(
            profile=profile,
            signals=signals,
            sources=(
                source("official", SourceRole.OFFICIAL_PRIMARY, ("agents",)),
                source("expert", SourceRole.EXPERT_INTERPRETER, ("agents",)),
            ),
            as_of=AS_OF,
            window_hours=24,
        ),
    )

    assert len(result.stories) == 1
    assert result.stories[0].primary_source_id == "official"
    assert result.stories[0].source_ids == ("official", "expert")
