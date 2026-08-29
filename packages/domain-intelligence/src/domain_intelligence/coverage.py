from __future__ import annotations

from domain_intelligence.models import (
    AcquisitionMethod,
    CoverageInput,
    CoverageReport,
    CoverageRow,
    EssentialInformationElement,
    GapReason,
    SourceEvaluation,
    SourceProfile,
)


def _has_acquisition_path(source: SourceProfile) -> bool:
    blocked = {AcquisitionMethod.UNKNOWN, AcquisitionMethod.MANUAL}
    return source.acquisition.method not in blocked and bool(source.acquisition.endpoint)


def _evaluation_by_source(
    evaluations: tuple[SourceEvaluation, ...],
) -> dict[str, SourceEvaluation]:
    return {str(evaluation.source_id): evaluation for evaluation in evaluations}


def _row_for_element(
    element: EssentialInformationElement,
    inputs: CoverageInput,
    evaluations: dict[str, SourceEvaluation],
) -> CoverageRow:
    capable = tuple(
        source
        for source in inputs.sources
        if element.id in source.element_ids or element.topic_id in source.topic_ids
    )
    if not capable:
        return CoverageRow(
            element_id=element.id, coverage_ratio=0, gap_reasons=(GapReason.NO_CAPABLE_SOURCE,)
        )
    approved = tuple(source for source in capable if source.approved)
    if not approved:
        return CoverageRow(
            element_id=element.id, coverage_ratio=0, gap_reasons=(GapReason.NO_APPROVED_SOURCE,)
        )
    ready = tuple(source for source in approved if _has_acquisition_path(source))
    if not ready:
        return CoverageRow(
            element_id=element.id, coverage_ratio=0, gap_reasons=(GapReason.NO_ACQUISITION_PATH,)
        )
    required = max(
        element.required_source_count,
        inputs.profile.stop_rules.minimum_sources_per_element,
    )
    ratio = min(1.0, len(ready) / required)
    reasons: list[GapReason] = []
    if ratio < 1:
        reasons.append(GapReason.INSUFFICIENT_SOURCE_COUNT)
    if len({source.role for source in ready}) < min(required, 2):
        reasons.append(GapReason.INSUFFICIENT_ROLE_DIVERSITY)
    if inputs.evaluations and not any(
        evaluation is not None and evaluation.nugget_recall > 0
        for source in ready
        for evaluation in (evaluations.get(str(source.id)),)
    ):
        reasons.append(GapReason.NO_HISTORICAL_EVIDENCE)
    return CoverageRow(
        element_id=element.id,
        coverage_ratio=round(ratio, 6),
        source_ids=tuple(source.id for source in ready),
        gap_reasons=tuple(dict.fromkeys(reasons)),
    )


def audit_coverage(inputs: CoverageInput) -> CoverageReport:
    evaluations = _evaluation_by_source(inputs.evaluations)
    rows = tuple(
        _row_for_element(element, inputs, evaluations) for element in inputs.profile.elements
    )
    total_weight = sum(element.weight for element in inputs.profile.elements)
    weighted_coverage = (
        sum(
            row.coverage_ratio * element.weight
            for row, element in zip(rows, inputs.profile.elements, strict=True)
        )
        / total_weight
        if total_weight
        else 0.0
    )
    return CoverageReport(
        total_elements=len(rows),
        covered_elements=sum(row.coverage_ratio >= 1 for row in rows),
        weighted_coverage=round(weighted_coverage, 6),
        rows=rows,
    )
