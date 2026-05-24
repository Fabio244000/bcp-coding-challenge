import pandas as pd
from app.domain.entities.loan_operation import LoanOperation, OptimizationResult, Currency, ProductType


class TestLoanOperation:
    """Prueba la creación y almacenamiento correcto de los campos de LoanOperation."""
    def test_create_valid_operations(self):
        operation = LoanOperation(
            product=ProductType.CREDIT,
            currency=Currency.PEN,
            amount=10000.0,
            term_months=12,
            target_roa=0.05,
        )
        assert operation.product == ProductType.CREDIT
        assert operation.currency == Currency.PEN
        assert operation.amount == 10000.0
        assert operation.term_months == 12
        assert operation.target_roa == 0.05

    def test_fields_are_stored_correctly(self):
        operation = LoanOperation(
            product=ProductType.LEASING,
            currency=Currency.USD,
            amount=50000.0,
            term_months=24,
            target_roa=0.06,
        )

        assert operation.product == ProductType.LEASING
        assert operation.currency == Currency.USD



class TestOptimizationResult:
    """Prueba la creación de OptimizationResult y que el DataFrame de curvas se almacena correctamente."""

    def setup_method(self):
        self.curves = pd.DataFrame({'month': [0, 1], 'balance': [10000.0, 9000.0]})
        self.result = OptimizationResult(
            tea=0.18,
            unit_clv=0.05,
            optimization_error=0.001,
            curves=self.curves,
        )

    def test_create_valid_result(self):
        assert self.result.tea == 0.18
        assert self.result.unit_clv == 0.05
        assert self.result.optimization_error == 0.001
        assert isinstance(self.result.curves, pd.DataFrame)

    def test_curves_has_expected_columns(self):
        assert 'month' in self.result.curves.columns
        assert 'balance' in self.result.curves.columns

