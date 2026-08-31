from __future__ import annotations

from domain_intelligence.activation import build_activation_report
from domain_intelligence.backtest import replay_benchmark
from domain_intelligence.coverage import audit_coverage
from domain_intelligence.daily import build_daily_brief
from domain_intelligence.graph import rank_attention_sources
from domain_intelligence.models import (
    ActivationInput,
    BootstrapInput,
    BootstrapReport,
    CoverageInput,
    DailyBriefInput,
    PortfolioInput,
    ReplayInput,
)
from domain_intelligence.portfolio import optimize_portfolio


def build_bootstrap_report(inputs: BootstrapInput) -> BootstrapReport:
    activation = build_activation_report(
        ActivationInput(
            sources=inputs.attention_graph.sources,
            runs=inputs.acquisition_runs,
            evidence=inputs.evidence,
            as_of=inputs.as_of,
            window_hours=inputs.window_hours,
        ),
    )
    signals_by_id = {str(signal.id): signal for signal in inputs.signals}
    signals_by_id.update({str(signal.id): signal for signal in activation.signals})
    signals = tuple(
        sorted(signals_by_id.values(), key=lambda signal: (signal.available_at, str(signal.id)))
    )
    replay = replay_benchmark(ReplayInput(benchmark=inputs.benchmark))
    evaluations = replay.source_metrics
    coverage = audit_coverage(
        CoverageInput(
            profile=inputs.profile,
            sources=inputs.attention_graph.sources,
            evaluations=evaluations,
        ),
    )
    total_nuggets = sum(len(event.nuggets) for event in inputs.benchmark.events)
    portfolio = optimize_portfolio(
        PortfolioInput(
            sources=inputs.attention_graph.sources,
            evaluations=evaluations,
            bundles=inputs.bundles,
            budget=inputs.budget,
            max_sources=inputs.max_sources,
            total_nuggets=total_nuggets,
        ),
    )
    brief = build_daily_brief(
        DailyBriefInput(
            profile=inputs.profile,
            signals=signals,
            sources=inputs.attention_graph.sources,
            as_of=inputs.as_of,
            window_hours=inputs.window_hours,
            limit=inputs.daily_limit,
        ),
    )
    recommendations = rank_attention_sources(inputs.attention_graph, inputs.attention_query)
    return BootstrapReport(
        generated_at=inputs.as_of,
        domain=inputs.profile.domain,
        activation=activation,
        attention_recommendations=recommendations,
        replay=replay,
        evaluations=evaluations,
        portfolio=portfolio,
        coverage=coverage,
        brief=brief,
    )
