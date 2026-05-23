import pytest
import numpy as np
from app.adapters.csv.csv_parameters_adapter import CSVParametersAdapter
from app.domain.exceptions import ProductNotFoundError, ParametersNotFoundError
from app.domain.entities.loan_operation import ProductType, Currency


class TestCSVParametersAdapter:

    def setup_method(self):
        self.adapter = CSVParametersAdapter(data_path='.')

    def test_get_costs_returns_valid_tuple(self):
        origination, maintenance = self.adapter.get_costs(ProductType.CREDIT, Currency.PEN)
        assert origination == 0.02
        assert maintenance == 0.015

    def test_get_costs_raises_when_not_found(self):
        with pytest.raises(ProductNotFoundError):
            self.adapter.get_costs('Invalid', Currency.PEN)

    def test_get_funding_rate_interpolates(self):
        rate = self.adapter.get_funding_rate(ProductType.CREDIT, Currency.PEN, 180)
        assert 0.040 <= rate <= 0.050

    def test_get_funding_rate_raises_when_not_found(self):
        with pytest.raises(ProductNotFoundError):
            self.adapter.get_funding_rate('Invalid', Currency.PEN, 360)

    def test_get_default_probability_returns_correct_array(self):
        pd_array = self.adapter.get_default_probability(ProductType.CREDIT, 12)
        assert len(pd_array) == 12
        assert isinstance(pd_array, np.ndarray)

    def test_get_default_probability_raises_when_not_found(self):
        with pytest.raises(ProductNotFoundError):
            self.adapter.get_default_probability('Invalid', 12)

    def test_raises_when_invalid_data_path(self):
        with pytest.raises(ParametersNotFoundError):
            CSVParametersAdapter(data_path='/invalid/path')
