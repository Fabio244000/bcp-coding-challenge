import logging
from fastapi import APIRouter, Depends, Request
from app.domain.ports.rate_calculator_port import RateCalculatorPort
from app.domain.entities.loan_operation import LoanOperation, ProductType, Currency
from app.domain.exceptions import InvalidOperationError, ParametersNotFoundError
from app.adapters.api.schemas import (
    LoanOperationRequest, OptimizationData, BatchOptimizationData, CurveRow, ApiResponse
)
from app.adapters.api.constants import (
    MSG_HEALTH_OK, ERR_PRODUCT_NOT_FOUND, ERR_INVALID_OPERATION,
    ERR_INTERNAL, ERR_PARAMETERS_UNAVAILABLE
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _error_example(message: str) -> dict:
    return {'application/json': {'example': {'success': False, 'message': message, 'detail': 'string'}}}


_ERROR_RESPONSES = {
    404: {'model': ApiResponse, 'description': ERR_PRODUCT_NOT_FOUND, 'content': _error_example(ERR_PRODUCT_NOT_FOUND)},
    422: {'model': ApiResponse, 'description': ERR_INVALID_OPERATION, 'content': _error_example(ERR_INVALID_OPERATION)},
    500: {'model': ApiResponse, 'description': ERR_INTERNAL, 'content': _error_example(ERR_INTERNAL)},
    503: {'model': ApiResponse, 'description': ERR_PARAMETERS_UNAVAILABLE, 'content': _error_example(ERR_PARAMETERS_UNAVAILABLE)},
}


def get_service(request: Request) -> RateCalculatorPort:
    service = getattr(request.app.state, 'service', None)
    if service is None:
        raise ParametersNotFoundError('Service not initialized')
    return service


def get_operation(body: LoanOperationRequest) -> LoanOperation:
    try:
        return LoanOperation(
            product=ProductType(body.product), currency=Currency(body.currency),
            amount=body.amount, term_months=body.term_months, target_roa=body.target_roa
        )
    except ValueError as e:
        raise InvalidOperationError(str(e))


def get_operations(body: list[LoanOperationRequest]) -> list[LoanOperation]:
    try:
        return [
            LoanOperation(
                product=ProductType(b.product), currency=Currency(b.currency),
                amount=b.amount, term_months=b.term_months, target_roa=b.target_roa
            ) for b in body
        ]
    except ValueError as e:
        raise InvalidOperationError(str(e))


@router.get('/health', response_model=ApiResponse[dict])
def health(service: RateCalculatorPort = Depends(get_service)):
    return ApiResponse(success=True, data={'status': 'ok', 'message': MSG_HEALTH_OK})


@router.post('/calcular', response_model=ApiResponse[OptimizationData], responses=_ERROR_RESPONSES)
def calculate(
    operation: LoanOperation = Depends(get_operation),
    service: RateCalculatorPort = Depends(get_service),
):
    logger.info('POST /calcular: product=%s, currency=%s', operation.product, operation.currency)
    result = service.calculate(operation)
    logger.info('POST /calcular result: tea=%.6f', result.tea)
    curves = [CurveRow(**row) for row in result.curves.to_dict(orient='records')]
    return ApiResponse(success=True, data=OptimizationData(
        tea=result.tea, unit_clv=result.unit_clv,
        optimization_error=result.optimization_error, curves=curves
    ))


@router.post('/calcular/lote', response_model=ApiResponse[list[BatchOptimizationData]], responses=_ERROR_RESPONSES)
def calculate_batch(
    operations: list[LoanOperation] = Depends(get_operations),
    service: RateCalculatorPort = Depends(get_service),
):
    logger.info('POST /calcular/lote: count=%d', len(operations))
    results = service.calculate_batch(operations)
    data = [BatchOptimizationData(tea=r.tea, unit_clv=r.unit_clv, optimization_error=r.optimization_error) for r in results]
    return ApiResponse(success=True, data=data)
