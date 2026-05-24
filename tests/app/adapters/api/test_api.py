import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from app.adapters.api.routes import get_service
from app.domain.ports.rate_calculator_port import RateCalculatorPort
from app.domain.entities.loan_operation import OptimizationResult
from app.domain.exceptions import (
    ProductNotFoundError, InvalidOperationError,
    OptimizationError, ParametersNotFoundError
)


_CURVE_COLUMNS = [
    'month', 'balance', 'payment', 'marginal_pd', 'survival',
    'funding_cost', 'maintenance_cost', 'net_flow', 'discount_factor', 'present_value',
]
_MOCK_CURVES = pd.DataFrame(
    [[0, 10000.0, 0.0, 0.0, 1.0, 0.0, 0.0, -10000.0, 1.0, -10000.0]],
    columns=_CURVE_COLUMNS,
)

MOCK_RESULT = OptimizationResult(
    tea=0.25, unit_clv=0.05, optimization_error=0.0, curves=_MOCK_CURVES,
)

VALID_PAYLOAD = {
    'product': 'Credito', 'currency': 'PEN',
    'amount': 10000.0, 'term_months': 12, 'target_roa': 0.05,
}

@pytest.fixture
def mock_service():
    service = MagicMock(spec=RateCalculatorPort)
    service.calculate.return_value = MOCK_RESULT
    service.calculate_batch.return_value = [MOCK_RESULT, MOCK_RESULT]
    return service

@pytest.fixture
def client(mock_service):
    app.state.service = mock_service
    app.dependency_overrides[get_service] = lambda: mock_service
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def error_client(mock_service):
    app.state.service = mock_service
    app.dependency_overrides[get_service] = lambda: mock_service
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Prueba el endpoint GET /health y su respuesta según la disponibilidad del servicio."""

    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_health_returns_503_when_service_unavailable(self, client):
        app.state.service = None
        response = client.get('/health')
        assert response.status_code == 503
        assert response.json()['success'] is False


class TestCalculateEndpoint:
    """Prueba el endpoint POST /calcular con casos de éxito y manejo de errores."""

    def test_calculate_returns_200(self, client):
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_calculate_response_contains_tea(self, client):
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert 'tea' in response.json()['data']

    def test_calculate_response_contains_curves(self, client):
        response = client.post('/calcular', json=VALID_PAYLOAD)
        data = response.json()['data']
        assert 'curves' in data
        assert isinstance(data['curves'], list)
        assert len(data['curves']) > 0
        assert 'month' in data['curves'][0]
        assert 'present_value' in data['curves'][0]

    def test_calculate_returns_404_when_product_not_found(self, client, mock_service):
        mock_service.calculate.side_effect = ProductNotFoundError('Credito/PEN')
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 404
        assert response.json()['success'] is False

    def test_calculate_returns_422_when_invalid_operation(self, client, mock_service):
        mock_service.calculate.side_effect = InvalidOperationError('Amount must be positive')
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 422
        assert response.json()['success'] is False

    def test_calculate_returns_422_on_invalid_input(self, client):
        payload = {**VALID_PAYLOAD, 'amount': -100.0}
        response = client.post('/calcular', json=payload)
        assert response.status_code == 422
        assert response.json()['success'] is False

    def test_calculate_returns_422_on_invalid_product(self, client):
        payload = {**VALID_PAYLOAD, 'product': 'INVALID'}
        response = client.post('/calcular', json=payload)
        assert response.status_code == 422
        assert response.json()['success'] is False

    def test_calculate_returns_500_on_optimization_error(self, client, mock_service):
        mock_service.calculate.side_effect = OptimizationError('Could not converge')
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 500
        assert response.json()['success'] is False

    def test_calculate_returns_500_on_unexpected_error(self, error_client, mock_service):
        mock_service.calculate.side_effect = Exception('Unexpected')
        response = error_client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 500
        assert response.json()['success'] is False

    def test_calculate_returns_503_on_parameters_unavailable(self, client, mock_service):
        mock_service.calculate.side_effect = ParametersNotFoundError('CSV unavailable')
        response = client.post('/calcular', json=VALID_PAYLOAD)
        assert response.status_code == 503
        assert response.json()['success'] is False


class TestCalculateBatchEndpoint:
    """Prueba el endpoint POST /calcular/lote con casos de éxito y manejo de errores."""

    def test_calculate_batch_returns_200(self, client):
        response = client.post('/calcular/lote', json=[VALID_PAYLOAD, VALID_PAYLOAD])
        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_calculate_batch_returns_correct_count(self, client):
        response = client.post('/calcular/lote', json=[VALID_PAYLOAD, VALID_PAYLOAD])
        assert len(response.json()['data']) == 2

    def test_calculate_batch_returns_422_on_invalid_input(self, client):
        payload = {**VALID_PAYLOAD, 'amount': -100.0}
        response = client.post('/calcular/lote', json=[payload])
        assert response.status_code == 422
        assert response.json()['success'] is False

    def test_calculate_batch_returns_500_on_unexpected_error(self, error_client, mock_service):
        mock_service.calculate_batch.side_effect = Exception('Unexpected')
        response = error_client.post('/calcular/lote', json=[VALID_PAYLOAD])
        assert response.status_code == 500
        assert response.json()['success'] is False
