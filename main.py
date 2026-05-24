import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.adapters.csv.csv_parameters_adapter import CSVParametersAdapter
from app.domain.services.operation_validator import OperationValidator
from app.domain.services.amortization_calculator import AmortizationCalculator
from app.domain.services.clv_calculator import CLVCalculator
from app.domain.services.rate_optimizer_service import RateOptimizerService
from app.adapters.api.routes import router
from fastapi.exceptions import RequestValidationError
from app.adapters.api.exception_handler import (
    handle_product_not_found, handle_invalid_operation,
    handle_optimization_error, handle_parameters_unavailable,
    handle_generic_error, handle_request_validation
)
from app.domain.exceptions import (
    ProductNotFoundError, InvalidOperationError, OptimizationError, ParametersNotFoundError
)
from app.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    try:
        parameters = CSVParametersAdapter(settings)
        validator = OperationValidator()
        amortization = AmortizationCalculator()
        clv_calculator = CLVCalculator(amortization, settings)
        app.state.service = RateOptimizerService(parameters, validator, clv_calculator, settings)
        logger.info('Service initialized successfully')
    except Exception as e:
        logger.error('Failed to initialize service: %s', str(e))
        app.state.service = None
    yield


app = FastAPI(
    title='CLV Rate Optimizer API',
    description='Optimal interest rate (TEA) calculation based on Customer Lifetime Value model',
    version='1.0.0',
    lifespan=lifespan
)

app.add_exception_handler(RequestValidationError, handle_request_validation)
app.add_exception_handler(ProductNotFoundError, handle_product_not_found)
app.add_exception_handler(InvalidOperationError, handle_invalid_operation)
app.add_exception_handler(OptimizationError, handle_optimization_error)
app.add_exception_handler(ParametersNotFoundError, handle_parameters_unavailable)
app.add_exception_handler(Exception, handle_generic_error)

app.include_router(router)
