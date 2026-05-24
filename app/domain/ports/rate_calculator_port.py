from abc import ABC, abstractmethod
from app.domain.entities.loan_operation import LoanOperation, OptimizationResult

class RateCalculatorPort(ABC):
    """Port defining the contract for optimal TEA calculation."""

    @abstractmethod
    def calculate(self, operation: LoanOperation) -> OptimizationResult:
        pass

    @abstractmethod
    def calculate_batch(self, operations: list[LoanOperation]) -> list[OptimizationResult]:
        pass
