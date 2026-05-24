from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class LoanOperationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={'example': {
        'product': 'Credito', 'currency': 'PEN',
        'amount': 10000.0, 'term_months': 12, 'target_roa': 0.05,
    }})
    product: str
    currency: str
    amount: float = Field(gt=0)
    term_months: int = Field(gt=0)
    target_roa: float = Field(gt=0)


class CurveRow(BaseModel):
    month: int
    balance: float
    payment: float
    marginal_pd: float
    survival: float
    funding_cost: float
    maintenance_cost: float
    net_flow: float
    discount_factor: float
    present_value: float


class OptimizationData(BaseModel):
    model_config = ConfigDict(json_schema_extra={'example': {
        'tea': 0.2145, 'unit_clv': 0.05, 'optimization_error': 0.000001,
        'curves': [
            {'month': 0, 'balance': 10000.0, 'payment': 0.0, 'marginal_pd': 0.0,
             'survival': 1.0, 'funding_cost': 0.0, 'maintenance_cost': 0.0,
             'net_flow': -10200.0, 'discount_factor': 1.0, 'present_value': -10200.0},
            {'month': 1, 'balance': 9126.45, 'payment': 945.33, 'marginal_pd': 0.005,
             'survival': 0.995, 'funding_cost': 38.02, 'maintenance_cost': 3.80,
             'net_flow': 901.80, 'discount_factor': 0.9965, 'present_value': 898.63},
        ],
    }})
    tea: float
    unit_clv: float
    optimization_error: float
    curves: list[CurveRow]


class BatchOptimizationData(BaseModel):
    model_config = ConfigDict(json_schema_extra={'example': {
        'tea': 0.2145, 'unit_clv': 0.05, 'optimization_error': 0.000001,
    }})
    tea: float
    unit_clv: float
    optimization_error: float


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    detail: Optional[str] = None