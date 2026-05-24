import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.domain.ports.rate_calculator_port import RateCalculatorPort
from app.domain.entities.loan_operation import LoanOperation, ProductType, Currency
from app.domain.exceptions import InvalidOperationError
from app.adapters.api.schemas import LoanOperationRequest, OptimizationData, ApiResponse
from app.adapters.api.constants import (
    MSG_HEALTH_OK, MSG_HEALTH_FAIL,
    ERR_PRODUCT_NOT_FOUND, ERR_INVALID_OPERATION,
    ERR_INTERNAL, ERR_PARAMETERS_UNAVAILABLE
)

def _error_example(message: str) -> dict:
    return {'application/json': {'example': {'success': False, 'message': message, 'detail': 'string'}}}


_ERROR_RESPONSES = {
    404: {'model': ApiResponse, 'description': ERR_PRODUCT_NOT_FOUND, 'content': _error_example(ERR_PRODUCT_NOT_FOUND)},
    422: {'model': ApiResponse, 'description': ERR_INVALID_OPERATION, 'content': _error_example(ERR_INVALID_OPERATION)},
    500: {'model': ApiResponse, 'description': ERR_INTERNAL, 'content': _error_example(ERR_INTERNAL)},
    503: {'model': ApiResponse, 'description': ERR_PARAMETERS_UNAVAILABLE, 'content': _error_example(ERR_PARAMETERS_UNAVAILABLE)},
}

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(request: Request) -> RateCalculatorPort:
    return request.app.state.service


def _to_operation(body: LoanOperationRequest) -> LoanOperation:
    try:
        return LoanOperation(
            product=ProductType(body.product), currency=Currency(body.currency),
            amount=body.amount, term_months=body.term_months, target_roa=body.target_roa
        )
    except ValueError as e:
        raise InvalidOperationError(str(e))


@router.get('/health', response_model=ApiResponse)
def health(request: Request):
    if not hasattr(request.app.state, 'service') or request.app.state.service is None:
        return JSONResponse(status_code=503, content={'success': False, 'message': MSG_HEALTH_FAIL})
    return ApiResponse(success=True, data={'status': 'ok', 'message': MSG_HEALTH_OK})


@router.post('/calcular', response_model=ApiResponse, responses=_ERROR_RESPONSES)
def calculate(body: LoanOperationRequest, service: RateCalculatorPort = Depends(get_service)):
    logger.info('POST /calcular: product=%s, currency=%s', body.product, body.currency)
    result = service.calculate(_to_operation(body))
    logger.info('POST /calcular result: tea=%.6f', result.tea)
    return ApiResponse(success=True, data=OptimizationData(
        tea=result.tea, unit_clv=result.unit_clv, optimization_error=result.optimization_error
    ))


@router.post('/calcular/lote', response_model=ApiResponse, responses=_ERROR_RESPONSES)
def calculate_batch(body: list[LoanOperationRequest], service: RateCalculatorPort = Depends(get_service)):
    logger.info('POST /calcular/lote: count=%d', len(body))
    results = service.calculate_batch([_to_operation(r) for r in body])
    data = [OptimizationData(tea=r.tea, unit_clv=r.unit_clv, optimization_error=r.optimization_error) for r in results]
    return ApiResponse(success=True, data=data)
