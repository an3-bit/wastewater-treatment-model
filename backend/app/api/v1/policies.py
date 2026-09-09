"""
Policies API Endpoints
Provides Stage 8C policy comparison table (Cases A through F).
"""

from fastapi import APIRouter, Depends
from app.schemas.policies import PolicyComparisonResponse
from app.services.policy_service import PolicyService, policy_service

router = APIRouter()


@router.get(
    "",
    response_model=PolicyComparisonResponse,
    summary="Supervisory Policy Benchmarks",
    description="Returns full policy comparison matrix across Case A (Baseline), Case B (Static), Case C (Condition), Case D (Predictive), Case E (Integrated), and Case F (Oracle).",
)
async def get_policies(
    service: PolicyService = Depends(lambda: policy_service),
) -> PolicyComparisonResponse:
    return service.get_policies()
