from __future__ import annotations

from datetime import datetime

from domain_intelligence.models import (
    AcquisitionMethod,
    AcquisitionPlan,
    AcquisitionPlanItem,
    AcquisitionPlanStatus,
    SourceProfile,
)


def build_acquisition_plan(
    sources: tuple[SourceProfile, ...],
    generated_at: datetime,
) -> AcquisitionPlan:
    items = tuple(_plan_item(source) for source in sorted(sources, key=lambda item: str(item.id)))
    return AcquisitionPlan(generated_at=generated_at, source_count=len(items), items=items)


def _plan_item(source: SourceProfile) -> AcquisitionPlanItem:
    method = source.acquisition.method
    endpoint = source.acquisition.endpoint
    if not source.approved:
        status = AcquisitionPlanStatus.BLOCKED
        reason = "source is not approved"
    elif not source.acquisition.stable:
        status = AcquisitionPlanStatus.BLOCKED
        reason = "acquisition endpoint is not marked stable"
    elif not endpoint:
        status = AcquisitionPlanStatus.BLOCKED
        reason = "source has no acquisition endpoint"
    elif method in {
        AcquisitionMethod.BROWSER,
        AcquisitionMethod.MANUAL,
        AcquisitionMethod.UNKNOWN,
    }:
        status = AcquisitionPlanStatus.BLOCKED
        reason = f"acquisition method {method.value} needs an external adapter"
    else:
        status = AcquisitionPlanStatus.READY
        reason = "configured endpoint and supported adapter boundary"
    return AcquisitionPlanItem(
        source_id=source.id,
        method=method,
        endpoint=endpoint,
        status=status,
        reason=reason,
    )
