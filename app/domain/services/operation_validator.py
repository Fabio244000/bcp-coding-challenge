from app.domain.entities.loan_operation import LoanOperation
from app.domain.exceptions import InvalidOperationError


class OperationValidator:
    """Validates that a LoanOperation has acceptable input parameters."""

    def validate(self, operation: LoanOperation) -> None:
        if operation.amount <= 0:
            raise InvalidOperationError('Amount must be positive')
        if operation.term_months <= 0:
            raise InvalidOperationError('Term must be positive')
        if operation.target_roa <= 0:
            raise InvalidOperationError('Target ROA must be positive')
