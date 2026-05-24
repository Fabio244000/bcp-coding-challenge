import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.domain.exceptions import (
    ProductNotFoundError, InvalidOperationError,
    OptimizationError, ParametersNotFoundError
)
from app.adapters.api.constants import (
    ERR_PRODUCT_NOT_FOUND, ERR_INVALID_OPERATION,
    ERR_OPTIMIZATION_FAILED, ERR_PARAMETERS_UNAVAILABLE, ERR_INTERNAL
)

logger = logging.getLogger(__name__)


def _error_response(message: str, detail: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={'success': False, 'message': message, 'detail': detail}
    )


async def handle_product_not_found(request: Request, exc: ProductNotFoundError) -> JSONResponse:
    logger.error('Product not found: %s', str(exc))
    return _error_response(ERR_PRODUCT_NOT_FOUND, str(exc), 404)


async def handle_invalid_operation(request: Request, exc: InvalidOperationError) -> JSONResponse:
    return _error_response(ERR_INVALID_OPERATION, str(exc), 422)


async def handle_optimization_error(request: Request, exc: OptimizationError) -> JSONResponse:
    logger.error('Optimization failed: %s', str(exc))
    return _error_response(ERR_OPTIMIZATION_FAILED, str(exc), 500)


async def handle_parameters_unavailable(request: Request, exc: ParametersNotFoundError) -> JSONResponse:
    logger.error('Parameters unavailable: %s', str(exc))
    return _error_response(ERR_PARAMETERS_UNAVAILABLE, str(exc), 503)


async def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error('Unexpected error: %s', str(exc))
    return _error_response(ERR_INTERNAL, str(exc), 500)


async def handle_request_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(ERR_INVALID_OPERATION, str(exc.errors()), 422)
