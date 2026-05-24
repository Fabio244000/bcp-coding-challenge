from typing import Any, Optional
from pydantic import BaseModel, Field


class LoanOperationRequest(BaseModel):
    product: str
    currency: str
    amount: float = Field(gt=0)
    term_months: int = Field(gt=0)
    target_roa: float = Field(gt=0)


class OptimizationData(BaseModel):
    tea: float
    unit_clv: float
    optimization_error: float


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    detail: Optional[str] = None