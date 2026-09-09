"""
Policy Service
Service layer for Stage 8C policy benchmarking (Cases A through F).
"""

from app.services.result_repository import result_repository
from app.schemas.policies import PolicyComparisonResponse


class PolicyService:
    def __init__(self, repo=None):
        self.repo = repo or result_repository

    def get_policies(self) -> PolicyComparisonResponse:
        return self.repo.get_policies()


policy_service = PolicyService()
