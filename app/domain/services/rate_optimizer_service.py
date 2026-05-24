import logging
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from app.domain.ports.rate_calculator_port import RateCalculatorPort
from app.domain.ports.market_parameters_port import MarketParametersPort
from app.domain.entities.loan_operation import LoanOperation, OptimizationResult
from app.domain.exceptions import OptimizationError, InvalidOperationError

logger = logging.getLogger(__name__)

TEA_MIN = 0.01
TEA_MAX = 2.0
TOLERANCE = 1e-6
MAX_ITERATIONS = 100
DAYS_PER_MONTH = 30


class RateOptimizerService(RateCalculatorPort):
    """Finds the optimal TEA for a loan operation using the CLV model and Brent's root-finding method."""

    def __init__(self, parameters: MarketParametersPort):
        self._parameters = parameters

    def calculate(self, operation: LoanOperation) -> OptimizationResult:
        self._validate(operation)
        logger.info('Calculating TEA: amount=%.2f, term=%d', operation.amount, operation.term_months)
        orig_cost, maint_cost = self._parameters.get_costs(operation.product.value, operation.currency.value)
        pd_array = self._parameters.get_default_probability(operation.product.value, operation.term_months)
        months = np.arange(1, operation.term_months + 1)
        funding_rates = self._get_funding_rates(operation, months)
        survival = np.cumprod(1 - pd_array)
        tea = self._find_optimal_tea(operation, orig_cost, maint_cost, months, funding_rates, survival)
        clv, curves = self._compute_clv_with_curves(tea, operation, orig_cost, maint_cost, pd_array, months, funding_rates, survival)
        logger.info('TEA found: %.6f, CLV: %.6f', tea, clv)
        return OptimizationResult(tea=tea, unit_clv=clv, optimization_error=abs(clv - operation.target_roa), curves=curves)

    def calculate_batch(self, operations: list[LoanOperation]) -> list[OptimizationResult]:
        return [self.calculate(op) for op in operations]

    def _validate(self, operation: LoanOperation) -> None:
        if operation.amount <= 0:
            raise InvalidOperationError('Amount must be positive')
        if operation.term_months <= 0:
            raise InvalidOperationError('Term must be positive')
        if operation.target_roa <= 0:
            raise InvalidOperationError('Target ROA must be positive')

    def _find_optimal_tea(self, operation: LoanOperation, orig_cost: float, maint_cost: float,
                          months: np.ndarray, funding_rates: np.ndarray, survival: np.ndarray) -> float:
        """Returns the TEA where CLV equals target ROA, solved via Brent's method."""
        def objective(tea: float) -> float:
            return self._compute_clv(tea, operation, orig_cost, maint_cost, months, funding_rates, survival) - operation.target_roa
        try:
            return brentq(objective, TEA_MIN, TEA_MAX, xtol=TOLERANCE, maxiter=MAX_ITERATIONS)
        except ValueError:
            logger.warning('TEA did not converge: amount=%.2f', operation.amount)
            raise OptimizationError('Could not find optimal TEA within range')

    def _compute_clv(self, tea: float, operation: LoanOperation, orig_cost: float, maint_cost: float,
                     months: np.ndarray, funding_rates: np.ndarray, survival: np.ndarray) -> float:
        """Computes unit CLV as NPV of survival-weighted net flows discounted by funding rates, normalized by amount."""
        tem = (1 + tea) ** (1 / 12) - 1
        payment = self._calculate_payment(operation.amount, tem, operation.term_months)
        balances = self._calculate_balances(operation.amount, tem, operation.term_months, months)
        net_flows = (payment - balances * funding_rates / 12 - balances * maint_cost / 12) * survival
        discount_factors = 1 / (1 + funding_rates / 12) ** months
        return (-operation.amount - orig_cost * operation.amount + np.sum(net_flows * discount_factors)) / operation.amount

    def _compute_clv_with_curves(self, tea: float, operation: LoanOperation, orig_cost: float, maint_cost: float,
                                  pd_array: np.ndarray, months: np.ndarray,
                                  funding_rates: np.ndarray, survival: np.ndarray) -> tuple[float, pd.DataFrame]:
        """Computes unit CLV and the per-month amortization curve in a single vectorized pass."""
        tem = (1 + tea) ** (1 / 12) - 1
        payment = self._calculate_payment(operation.amount, tem, operation.term_months)
        balances = self._calculate_balances(operation.amount, tem, operation.term_months, months)
        funding_costs = balances * funding_rates / 12
        maintenance_costs = balances * maint_cost / 12
        net_flows = (payment - funding_costs - maintenance_costs) * survival
        discount_factors = 1 / (1 + funding_rates / 12) ** months
        pv_flows = net_flows * discount_factors
        clv = (-operation.amount - orig_cost * operation.amount + np.sum(pv_flows)) / operation.amount
        return clv, self._build_curves(operation, months, balances, payment, pd_array, survival, funding_costs, maintenance_costs, net_flows, discount_factors, pv_flows, orig_cost)

    def _calculate_payment(self, amount: float, tem: float, n: int) -> float:
        if tem <= 0:
            return amount / n
        return amount * tem * (1 + tem) ** n / ((1 + tem) ** n - 1)

    def _calculate_balances(self, amount: float, tem: float, n: int, months: np.ndarray) -> np.ndarray:
        if tem <= 0:
            return amount * (1 - (months - 1) / n)
        return amount * ((1 + tem) ** n - (1 + tem) ** (months - 1)) / ((1 + tem) ** n - 1)

    def _get_funding_rates(self, operation: LoanOperation, months: np.ndarray) -> np.ndarray:
        return np.array([
            self._parameters.get_funding_rate(
                operation.product.value, operation.currency.value, int(m * DAYS_PER_MONTH)
            ) for m in months
        ])

    def _build_curves(self, operation: LoanOperation, months: np.ndarray, balances: np.ndarray,
                      payment: float, pd_array: np.ndarray, survival: np.ndarray,
                      funding_costs: np.ndarray, maintenance_costs: np.ndarray,
                      net_flows: np.ndarray, discount_factors: np.ndarray,
                      pv_flows: np.ndarray, orig_cost: float) -> pd.DataFrame:
        return pd.concat([
            self._build_row_zero(operation, orig_cost),
            self._build_monthly_rows(months, balances, payment, pd_array, survival, funding_costs, maintenance_costs, net_flows, discount_factors, pv_flows)
        ], ignore_index=True)

    def _build_row_zero(self, operation: LoanOperation, orig_cost: float) -> pd.DataFrame:
        initial_flow = -operation.amount - orig_cost * operation.amount
        return pd.DataFrame([{
            'month': 0, 'balance': operation.amount, 'payment': 0.0,
            'marginal_pd': 0.0, 'survival': 1.0, 'funding_cost': 0.0,
            'maintenance_cost': 0.0, 'net_flow': initial_flow,
            'discount_factor': 1.0, 'present_value': initial_flow
        }])

    def _build_monthly_rows(self, months: np.ndarray, balances: np.ndarray, payment: float,
                            pd_array: np.ndarray, survival: np.ndarray, funding_costs: np.ndarray,
                            maintenance_costs: np.ndarray, net_flows: np.ndarray,
                            discount_factors: np.ndarray, pv_flows: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame({
            'month': months.astype(int), 'balance': balances, 'payment': payment,
            'marginal_pd': pd_array, 'survival': survival, 'funding_cost': funding_costs,
            'maintenance_cost': maintenance_costs, 'net_flow': net_flows,
            'discount_factor': discount_factors, 'present_value': pv_flows
        })
