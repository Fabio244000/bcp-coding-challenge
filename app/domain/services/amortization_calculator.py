import numpy as np


class AmortizationCalculator:
    """Computes French amortization payment and outstanding balances."""

    def payment(self, amount: float, tem: float, n: int) -> float:
        if tem <= 0:
            return amount / n
        return amount * tem * (1 + tem) ** n / ((1 + tem) ** n - 1)

    def balances(self, amount: float, tem: float, n: int, months: np.ndarray) -> np.ndarray:
        if tem <= 0:
            return amount * (1 - (months - 1) / n)
        return amount * ((1 + tem) ** n - (1 + tem) ** (months - 1)) / ((1 + tem) ** n - 1)
