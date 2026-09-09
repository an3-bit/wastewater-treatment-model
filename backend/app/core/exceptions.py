"""
Custom Exception Classes for WaterTwin AI API
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class WaterTwinException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        )


class DomainConstraintViolationException(WaterTwinException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="DOMAIN_CONSTRAINT_VIOLATION",
            message=message,
            details=details,
        )


class SimulationFailedException(WaterTwinException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="SIMULATION_ERROR",
            message=message,
            details=details,
        )


class ResultNotFoundException(WaterTwinException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESULT_NOT_FOUND",
            message=message,
            details=details,
        )
