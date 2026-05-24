import logging
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from app.domain.entities.loan_operation import LoanOperation
from app.domain.exceptions import OptimizationError
from app.domain.services.amortization_calculator import AmortizationCalculator
from app.config import Settings

logger = logging.getLogger(__name__)


class CLVCalculator:
    """Computes unit CLV and builds the per-month amortization curve."""

    def __init__(self, amortization: AmortizationCalculator, settings: Settings):
        self._amortization = amortization
        self._settings = settings

    def find_optimal_tea(self, operation: LoanOperation, orig_cost: float, maint_cost: float,
                         months: np.ndarray, funding_rates: np.ndarray, survival: np.ndarray) -> float:
        """Returns the TEA where CLV equals target ROA, solved via Brent's method."""
        def objective(tea: float) -> float:
            return self.compute(tea, operation, orig_cost, maint_cost, months, funding_rates, survival) - operation.target_roa
        try:
            return brentq(objective, self._settings.tea_min, self._settings.tea_max,
                          xtol=self._settings.tolerance, maxiter=self._settings.max_iterations)
        except ValueError:
            logger.warning('TEA did not converge: amount=%.2f', operation.amount)
            raise OptimizationError('Could not find optimal TEA within range')

    def compute(self, tea: float, operation: LoanOperation, orig_cost: float, maint_cost: float,
                months: np.ndarray, funding_rates: np.ndarray, survival: np.ndarray) -> float:
        """Computes unit CLV as NPV of survival-weighted net flows discounted by funding rates, normalized by amount."""
        tem = (1 + tea) ** (1 / 12) - 1
        payment = self._amortization.payment(operation.amount, tem, operation.term_months)
        balances = self._amortization.balances(operation.amount, tem, operation.term_months, months)
        net_flows = (payment - balances * funding_rates / 12 - balances * maint_cost / 12) * survival
        discount_factors = 1 / (1 + funding_rates / 12) ** months
        return (-operation.amount - orig_cost * operation.amount + np.sum(net_flows * discount_factors)) / operation.amount

    def compute_with_curves(self, tea: float, operation: LoanOperation, orig_cost: float, maint_cost: float,
                            pd_array: np.ndarray, months: np.ndarray,
                            funding_rates: np.ndarray, survival: np.ndarray) -> tuple[float, pd.DataFrame]:
        """Computes unit CLV and the per-month amortization curve in a single vectorized pass."""
        tem = (1 + tea) ** (1 / 12) - 1
        payment = self._amortization.payment(operation.amount, tem, operation.term_months)
        balances = self._amortization.balances(operation.amount, tem, operation.term_months, months)
        funding_costs = balances * funding_rates / 12
        maintenance_costs = balances * maint_cost / 12
        net_flows = (payment - funding_costs - maintenance_costs) * survival
        discount_factors = 1 / (1 + funding_rates / 12) ** months
        pv_flows = net_flows * discount_factors
        clv = (-operation.amount - orig_cost * operation.amount + np.sum(pv_flows)) / operation.amount
        return clv, self._build_curves(operation, months, balances, payment, pd_array, survival,
                                       funding_costs, maintenance_costs, net_flows, discount_factors,
                                       pv_flows, orig_cost)

    def _build_curves(self, operation: LoanOperation, months: np.ndarray, balances: np.ndarray,
                      payment: float, pd_array: np.ndarray, survival: np.ndarray,
                      funding_costs: np.ndarray, maintenance_costs: np.ndarray,
                      net_flows: np.ndarray, discount_factors: np.ndarray,
                      pv_flows: np.ndarray, orig_cost: float) -> pd.DataFrame:
        initial_flow = -operation.amount - orig_cost * operation.amount
        row_zero = pd.DataFrame([{
            'month': 0, 'balance': operation.amount, 'payment': 0.0,
            'marginal_pd': 0.0, 'survival': 1.0, 'funding_cost': 0.0,
            'maintenance_cost': 0.0, 'net_flow': initial_flow,
            'discount_factor': 1.0, 'present_value': initial_flow
        }])
        monthly_rows = pd.DataFrame({
            'month': months.astype(int), 'balance': balances, 'payment': payment,
            'marginal_pd': pd_array, 'survival': survival, 'funding_cost': funding_costs,
            'maintenance_cost': maintenance_costs, 'net_flow': net_flows,
            'discount_factor': discount_factors, 'present_value': pv_flows
        })
        return pd.concat([row_zero, monthly_rows], ignore_index=True)
