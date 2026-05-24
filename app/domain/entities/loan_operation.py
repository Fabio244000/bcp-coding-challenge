from dataclasses import dataclass
from enum import Enum
import pandas as pd


class Currency(str, Enum):
    PEN = 'PEN'
    USD = 'USD'


class ProductType(str, Enum):
    CREDIT = 'Credito'
    LEASING = 'Leasing'
    CARD = 'Tarjeta'


@dataclass(frozen=True)
class LoanOperation:
    product: ProductType
    currency: Currency
    amount: float
    term_months: int
    target_roa: float


@dataclass
class OptimizationResult:
    tea: float
    unit_clv: float
    optimization_error: float
    curves: pd.DataFrame