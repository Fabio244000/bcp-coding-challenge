import logging
import numpy as np
from app.domain.ports.rate_calculator_port import RateCalculatorPort
from app.domain.ports.market_parameters_port import MarketParametersPort
from app.domain.entities.loan_operation import LoanOperation, OptimizationResult
from app.domain.services.operation_validator import OperationValidator
from app.domain.services.clv_calculator import CLVCalculator
from app.config import Settings

logger = logging.getLogger(__name__)


class RateOptimizerService(RateCalculatorPort):
    """Orchestrates TEA optimization by delegating to specialized components."""

    def __init__(self, parameters: MarketParametersPort, validator: OperationValidator,
                 clv_calculator: CLVCalculator, settings: Settings):
        self._parameters = parameters
        self._validator = validator
        self._clv_calculator = clv_calculator
        self._settings = settings

    def calculate(self, operation: LoanOperation) -> OptimizationResult:
        self._validator.validate(operation)
        logger.info('Calculating TEA: amount=%.2f, term=%d', operation.amount, operation.term_months)
        orig_cost, maint_cost = self._parameters.get_costs(operation.product.value, operation.currency.value)
        pd_array = self._parameters.get_default_probability(operation.product.value, operation.term_months)
        months = np.arange(1, operation.term_months + 1)
        funding_rates = self._get_funding_rates(operation, months)
        survival = np.cumprod(1 - pd_array)
        tea = self._clv_calculator.find_optimal_tea(operation, orig_cost, maint_cost, months, funding_rates, survival)
        clv, curves = self._clv_calculator.compute_with_curves(tea, operation, orig_cost, maint_cost, pd_array, months, funding_rates, survival)
        logger.info('TEA found: %.6f, CLV: %.6f', tea, clv)
        return OptimizationResult(tea=tea, unit_clv=clv, optimization_error=abs(clv - operation.target_roa), curves=curves)

    def calculate_batch(self, operations: list[LoanOperation]) -> list[OptimizationResult]:
        return [self.calculate(op) for op in operations]

    def _get_funding_rates(self, operation: LoanOperation, months: np.ndarray) -> np.ndarray:
        return np.array([
            self._parameters.get_funding_rate(
                operation.product.value, operation.currency.value,
                int(m * self._settings.days_per_month)
            ) for m in months
        ])
