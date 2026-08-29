from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from domain_intelligence.models import (
    BenchmarkEvent,
    InformationNugget,
    Observation,
    ReplayCell,
    ReplayInput,
    ReplayReport,
    SourceEvaluation,
    SourceProfile,
)


def _flatten_nuggets(events: tuple[BenchmarkEvent, ...]) -> dict[str, InformationNugget]:
    return {str(nugget.id): nugget for event in events for nugget in event.nuggets}


def _visible_observations(
    observations: tuple[Observation, ...],
    cutoff: datetime,
) -> tuple[Observation, ...]:
    return tuple(observation for observation in observations if observation.available_at <= cutoff)


def _build_cells(
    inputs: ReplayInput,
    cutoffs: tuple[datetime, ...],
) -> tuple[ReplayCell, ...]:
    cells: list[ReplayCell] = []
    for cutoff in cutoffs:
        visible = _visible_observations(inputs.benchmark.observations, cutoff)
        by_nugget: dict[str, list[Observation]] = defaultdict(list)
        for observation in visible:
            if observation.nugget_id is not None:
                by_nugget[str(observation.nugget_id)].append(observation)
        for event in inputs.benchmark.events:
            for nugget in event.nuggets:
                eligible = nugget.available_at <= cutoff
                observations = by_nugget[str(nugget.id)] if eligible else []
                observations.sort(key=lambda item: (item.available_at, str(item.source_id)))
                source_ids = tuple(
                    dict.fromkeys(observation.source_id for observation in observations)
                )
                cells.append(
                    ReplayCell(
                        cutoff=cutoff,
                        event_id=event.id,
                        nugget_id=nugget.id,
                        eligible=eligible,
                        visible_source_ids=source_ids,
                        first_source_id=source_ids[0] if source_ids else None,
                    ),
                )
    return tuple(cells)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _source_evaluation(
    source: SourceProfile,
    benchmark: ReplayInput,
    nuggets: dict[str, InformationNugget],
    final_cutoff: datetime,
) -> SourceEvaluation:
    visible = _visible_observations(benchmark.benchmark.observations, final_cutoff)
    relevant = tuple(
        observation
        for observation in visible
        if observation.source_id == source.id
        and observation.nugget_id is not None
        and str(observation.nugget_id) in nuggets
        and nuggets[str(observation.nugget_id)].available_at <= final_cutoff
    )
    covered = tuple(
        sorted(
            {observation.nugget_id for observation in relevant if observation.nugget_id is not None}
        )
    )
    eligible = tuple(nugget for nugget in nuggets.values() if nugget.available_at <= final_cutoff)
    eligible_events = {str(nugget.event_id) for nugget in eligible}
    covered_events = {str(nuggets[str(nugget_id)].event_id) for nugget_id in covered}
    lead_times = [
        max(
            0.0,
            (
                nuggets[str(observation.nugget_id)].authoritative_at - observation.available_at
            ).total_seconds()
            / 3600,
        )
        for observation in relevant
        if observation.nugget_id is not None
    ]
    all_source_observations = tuple(
        observation for observation in visible if observation.source_id == source.id
    )
    precision = _mean(
        [1.0 if observation.is_confirmed else 0.0 for observation in all_source_observations]
    )
    corroborating_roles: dict[str, set[str]] = defaultdict(set)
    source_by_id = {candidate.id: candidate for candidate in benchmark.benchmark.sources}
    for observation in visible:
        if observation.nugget_id is None or str(observation.nugget_id) not in nuggets:
            continue
        role = observation.role or source_by_id[observation.source_id].role
        corroborating_roles[str(observation.nugget_id)].add(role.value)
    cross_role = _mean(
        [1.0 if len(corroborating_roles[str(nugget_id)]) > 1 else 0.0 for nugget_id in covered],
    )
    acquisition_reliability = (
        0.4 * source.reliability + 0.3 * source.stability + 0.3 * source.accessibility
    ) * (1.0 if source.acquisition.stable else 0.5)
    return SourceEvaluation(
        source_id=source.id,
        event_recall=len(covered_events) / len(eligible_events) if eligible_events else 0.0,
        nugget_recall=len(covered) / len(eligible) if eligible else 0.0,
        lead_time_hours=round(_mean(lead_times), 6),
        precision=round(precision, 6),
        false_alarm_burden=round(1.0 - precision, 6),
        originality=round(_mean([float(observation.is_original) for observation in relevant]), 6),
        credibility=round(_mean([float(observation.is_confirmed) for observation in relevant]), 6),
        explanatory_depth=round(
            _mean([observation.explanation_depth for observation in relevant]), 6
        ),
        cross_role_confirmation=round(cross_role, 6),
        acquisition_reliability=round(acquisition_reliability, 6),
        decision_utility=round(
            _mean([observation.decision_utility for observation in relevant]), 6
        ),
        covered_nugget_ids=covered,
    )


def replay_benchmark(inputs: ReplayInput) -> ReplayReport:
    cutoffs = tuple(sorted(set(inputs.benchmark.cutoffs)))
    nuggets = _flatten_nuggets(inputs.benchmark.events)
    cells = _build_cells(inputs, cutoffs)
    final_cutoff = cutoffs[-1]
    metrics = tuple(
        _source_evaluation(source, inputs, nuggets, final_cutoff)
        for source in sorted(inputs.benchmark.sources, key=lambda item: item.id)
    )
    return ReplayReport(cutoffs=cutoffs, cells=cells, source_metrics=metrics)
