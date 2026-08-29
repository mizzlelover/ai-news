from __future__ import annotations

from dataclasses import dataclass

from domain_intelligence.models import (
    PortfolioInput,
    PortfolioResult,
    SourceEvaluation,
    SourceId,
    SourceProfile,
)


@dataclass(frozen=True, slots=True)
class _Option:
    option_id: str
    source_ids: tuple[SourceId, ...]
    bundle: bool
    synergy: float


@dataclass(frozen=True, slots=True)
class _SelectionContext:
    sources: dict[SourceId, SourceProfile]
    evaluations: dict[SourceId, SourceEvaluation]
    covered: frozenset[str]
    selected_roles: frozenset[str]
    total_nuggets: int


def _quality(evaluation: SourceEvaluation) -> float:
    return (
        0.35 * evaluation.nugget_recall
        + 0.15 * evaluation.precision
        + 0.15 * evaluation.originality
        + 0.15 * evaluation.credibility
        + 0.1 * evaluation.cross_role_confirmation
        + 0.1 * evaluation.acquisition_reliability
    )


def _options(inputs: PortfolioInput) -> tuple[_Option, ...]:
    source_ids = {source.id for source in inputs.sources}
    singles = tuple(
        _Option(option_id=str(source.id), source_ids=(source.id,), bundle=False, synergy=0)
        for source in inputs.sources
    )
    bundles = tuple(
        _Option(
            option_id=bundle.id,
            source_ids=bundle.source_ids,
            bundle=True,
            synergy=bundle.synergy_bonus,
        )
        for bundle in inputs.bundles
        if all(source_id in source_ids for source_id in bundle.source_ids)
    )
    return singles + bundles


def _option_value(
    option: _Option,
    context: _SelectionContext,
) -> tuple[float, float]:
    option_evaluations = tuple(
        context.evaluations[source_id]
        for source_id in option.source_ids
        if source_id in context.evaluations
    )
    covered_by_option = {
        nugget_id
        for evaluation in option_evaluations
        for nugget_id in evaluation.covered_nugget_ids
    }
    new_coverage = covered_by_option - context.covered
    coverage_gain = len(new_coverage) / context.total_nuggets if context.total_nuggets else 0.0
    quality = (
        sum(_quality(evaluation) for evaluation in option_evaluations) / len(option_evaluations)
        if option_evaluations
        else 0.0
    )
    new_roles = {
        context.sources[source_id].role.value
        for source_id in option.source_ids
        if source_id in context.sources
    } - context.selected_roles
    role_gain = min(1.0, len(new_roles) / 2)
    value = 0.55 * coverage_gain + 0.2 * quality + 0.15 * role_gain + 0.25 * option.synergy
    return value, coverage_gain


def optimize_portfolio(inputs: PortfolioInput) -> PortfolioResult:
    sources = {source.id: source for source in inputs.sources}
    evaluations = {evaluation.source_id: evaluation for evaluation in inputs.evaluations}
    selected: list[SourceId] = []
    selected_bundles: list[str] = []
    covered: set[str] = set()
    selected_roles: set[str] = set()
    total_cost = 0.0
    score = 0.0
    contributions: list[str] = []
    context = _SelectionContext(
        sources=sources,
        evaluations=evaluations,
        covered=frozenset(),
        selected_roles=frozenset(),
        total_nuggets=inputs.total_nuggets,
    )
    for _ in range(inputs.max_sources):
        candidates: list[tuple[float, float, float, str, _Option]] = []
        for option in _options(inputs):
            if any(source_id in selected for source_id in option.source_ids):
                continue
            option_cost = sum(sources[source_id].cost for source_id in option.source_ids)
            if (
                len(selected) + len(option.source_ids) > inputs.max_sources
                or total_cost + option_cost > inputs.budget
            ):
                continue
            value, coverage_gain = _option_value(option, context)
            if value <= 0:
                continue
            candidates.append((value, coverage_gain, -option_cost, option.option_id, option))
        if not candidates:
            break
        chosen_value, _, _, _, chosen = max(candidates, key=lambda item: item[:4])
        chosen_cost = sum(sources[source_id].cost for source_id in chosen.source_ids)
        chosen_coverage = {
            nugget_id
            for source_id in chosen.source_ids
            for nugget_id in evaluations.get(
                source_id, SourceEvaluation(source_id=source_id)
            ).covered_nugget_ids
        }
        selected.extend(chosen.source_ids)
        covered.update(chosen_coverage)
        selected_roles.update(sources[source_id].role.value for source_id in chosen.source_ids)
        total_cost += chosen_cost
        score += chosen_value
        contributions.append(f"{chosen.option_id}:{chosen_value:.6f}")
        context = _SelectionContext(
            sources=sources,
            evaluations=evaluations,
            covered=frozenset(covered),
            selected_roles=frozenset(selected_roles),
            total_nuggets=inputs.total_nuggets,
        )
        if chosen.bundle:
            selected_bundles.append(chosen.option_id)
    return PortfolioResult(
        selected_source_ids=tuple(selected),
        selected_bundle_ids=tuple(selected_bundles),
        total_cost=round(total_cost, 6),
        covered_nugget_ids=tuple(sorted(covered)),
        score=round(score, 6),
        marginal_contributions=tuple(contributions),
    )
