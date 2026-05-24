import pytest
import numpy as np
from unittest.mock import MagicMock
from app.domain.services.rate_optimizer_service import RateOptimizerService
from app.domain.entities.loan_operation import LoanOperation, ProductType, Currency
from app.domain.exceptions import InvalidOperationError

class TestOptimizerService:
    def setup_method(self):
        self.mock_parameters = MagicMock()
        self.mock_parameters.get_costs.return_value = (0.02, 0.005)
        self.mock_parameters.get_default_probability.return_value = np.full(12, 0.005)
        self.mock_parameters.get_funding_rate.return_value = 0.05
        self.service = RateOptimizerService(self.mock_parameters)
        self.operation = LoanOperation(
            product=ProductType.CREDIT,
            currency=Currency.PEN,
            amount=10000.0,
            term_months=12,
            target_roa=0.05,
        )

    def test_calculate_returns_valid_tea(self):
        result = self.service.calculate(self.operation)
        assert 0.01 <= result.tea <= 2.0

    def test_calculate_clv_close_to_target_roa(self):
        result = self.service.calculate(self.operation)
        assert abs(result.unit_clv - self.operation.target_roa) <= 0.01

    def test_calculate_curves_has_correct_rows(self):
        result = self.service.calculate(self.operation)
        assert len(result.curves) == self.operation.term_months + 1

    def test_calculate_curves_month_zero_balance_equals_amount(self):
        result = self.service.calculate(self.operation)
        assert result.curves.iloc[0]['balance'] == self.operation.amount

    def test_calculate_batch_returns_correct_count(self):
        results = self.service.calculate_batch([self.operation, self.operation])
        assert len(results) == 2

    def test_validate_raises_for_negative_amount(self):
        op = LoanOperation(
            product=ProductType.CREDIT,
            currency=Currency.PEN,
            amount=-1.0,
            term_months=12,
            target_roa=0.05,
        )
        with pytest.raises(InvalidOperationError):
            self.service.calculate(op)

    def test_validate_raise_for_zero_term(self):
        op = LoanOperation(
            product=ProductType.CREDIT,
            currency=Currency.PEN,
            amount=10000.0,
            term_months=0,
            target_roa=0.05,
        )

        with pytest.raises(InvalidOperationError):
            self.service.calculate(op)