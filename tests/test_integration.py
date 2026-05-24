import pytest
import time
import numpy as np
import pandas as pd
from app.adapters.csv.csv_parameters_adapter import CSVParametersAdapter
from app.domain.services.rate_optimizer_service import RateOptimizerService
from app.domain.entities.loan_operation import LoanOperation, ProductType, Currency

DATA_PATH = '.'
TOLERANCE = 0.01
MAX_EXECUTION_SECONDS = 60

EXPECTED_CURVE_COLUMNS = [
    'month', 'balance', 'payment', 'marginal_pd', 'survival',
    'funding_cost', 'maintenance_cost', 'net_flow', 'discount_factor', 'present_value'
]

OPERATIONS = [
    LoanOperation(ProductType.CREDIT, Currency.PEN, 10000.0, 12, 0.05),
    LoanOperation(ProductType.CREDIT, Currency.USD, 5000.0, 12, 0.04),
    LoanOperation(ProductType.LEASING, Currency.PEN, 50000.0, 24, 0.06),
    LoanOperation(ProductType.LEASING, Currency.USD, 30000.0, 24, 0.055),
    LoanOperation(ProductType.CARD, Currency.PEN, 3000.0, 6, 0.08),
    LoanOperation(ProductType.CARD, Currency.USD, 2000.0, 6, 0.07),
    LoanOperation(ProductType.CREDIT, Currency.PEN, 15000.0, 36, 0.045),
    LoanOperation(ProductType.CREDIT, Currency.USD, 8000.0, 36, 0.04),
    LoanOperation(ProductType.LEASING, Currency.PEN, 20000.0, 12, 0.065),
    LoanOperation(ProductType.CARD, Currency.PEN, 5000.0, 24, 0.075),
]


@pytest.fixture(scope='module')
def parameters():
    return CSVParametersAdapter(DATA_PATH)


@pytest.fixture(scope='module')
def service(parameters):
    return RateOptimizerService(parameters)


@pytest.fixture(scope='module')
def batch_results(service):
    return service.calculate_batch(OPERATIONS)


class TestCSVLoading:
    def test_parameters_adapter_loads_successfully(self, parameters):
        origination, maintenance = parameters.get_costs(ProductType.CREDIT.value, Currency.PEN.value)
        assert origination > 0
        assert maintenance > 0

    def test_parameters_file_has_ten_operations(self):
        df = pd.read_csv(f'{DATA_PATH}/parametros final.csv')
        assert len(df) == 10

    def test_costs_file_has_six_entries(self):
        df = pd.read_csv(f'{DATA_PATH}/costos final_1.csv')
        assert len(df) == 6


class TestBatchResults:
    def test_batch_returns_ten_results(self, batch_results):
        assert len(batch_results) == 10

    def test_tea_not_null(self, batch_results):
        for result in batch_results:
            assert isinstance(result.tea, float)
            assert not np.isnan(result.tea)

    def test_tea_within_reasonable_range(self, batch_results):
        for i, result in enumerate(batch_results):
            assert 0.01 <= result.tea <= 0.99, f'TEA out of range for op {i}: {result.tea}'

    def test_tea_above_base_funding_rate(self, batch_results, parameters):
        for i, (result, op) in enumerate(zip(batch_results, OPERATIONS)):
            base_rate = parameters.get_funding_rate(op.product.value, op.currency.value, 30)
            assert result.tea >= base_rate, f'TEA {result.tea} < base rate {base_rate} for op {i}'

    def test_clv_close_to_target_roa(self, batch_results):
        for i, (result, op) in enumerate(zip(batch_results, OPERATIONS)):
            diff = abs(result.unit_clv - op.target_roa)
            assert diff <= TOLERANCE, f'CLV={result.unit_clv}, ROA={op.target_roa}, diff={diff} for op {i}'

    def test_optimization_error_within_tolerance(self, batch_results):
        for i, result in enumerate(batch_results):
            assert result.optimization_error <= TOLERANCE, f'Error {result.optimization_error} > {TOLERANCE} for op {i}'

    def test_curves_exist_for_each_result(self, batch_results):
        for i, result in enumerate(batch_results):
            assert result.curves is not None
            assert len(result.curves) > 0, f'Empty curves for op {i}'

    def test_curves_has_expected_columns(self, batch_results):
        for i, result in enumerate(batch_results):
            for col in EXPECTED_CURVE_COLUMNS:
                assert col in result.curves.columns, f'Missing column {col} for op {i}'

    def test_curves_has_term_plus_one_rows(self, batch_results):
        for i, (result, op) in enumerate(zip(batch_results, OPERATIONS)):
            expected = op.term_months + 1
            assert len(result.curves) == expected, f'Rows: expected {expected}, got {len(result.curves)} for op {i}'

    def test_curves_month_zero_balance_equals_amount(self, batch_results):
        for i, (result, op) in enumerate(zip(batch_results, OPERATIONS)):
            month_zero = result.curves[result.curves['month'] == 0]
            balance = month_zero['balance'].values[0]
            assert abs(balance - op.amount) <= TOLERANCE, f'Balance {balance} != amount {op.amount} for op {i}'

    def test_survival_between_zero_and_one(self, batch_results):
        for i, result in enumerate(batch_results):
            monthly = result.curves[result.curves['month'] > 0]
            assert (monthly['survival'] >= 0.0).all(), f'Negative survival in op {i}'
            assert (monthly['survival'] <= 1.0).all(), f'Survival > 1 in op {i}'


class TestPerformance:
    def test_batch_executes_within_time_limit(self, service):
        start = time.time()
        service.calculate_batch(OPERATIONS)
        elapsed = time.time() - start
        assert elapsed < MAX_EXECUTION_SECONDS, f'Took {elapsed:.2f}s, limit is {MAX_EXECUTION_SECONDS}s'
