"""
Economics Service
Service layer for authoritative Stage 8C techno-economic summary, attribution, and scenarios.
"""

from app.services.result_repository import result_repository
from app.schemas.economics import (
    EconomicScenariosResponse,
    EconomicSummaryResponse,
    ValueDecompositionResponse,
)


class EconomicsService:
    def __init__(self, repo=None):
        self.repo = repo or result_repository

    def get_summary(self) -> EconomicSummaryResponse:
        return self.repo.get_economic_summary()

    def get_value_decomposition(self) -> ValueDecompositionResponse:
        return self.repo.get_value_decomposition()

    def get_scenarios(self) -> EconomicScenariosResponse:
        return self.repo.get_scenarios()


economics_service = EconomicsService()
