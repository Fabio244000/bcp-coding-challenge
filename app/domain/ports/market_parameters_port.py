from abc import ABC, abstractmethod
import numpy as np

class MarketParametersPort(ABC):

    @abstractmethod
    def get_costs(self, product: str, currency: str) -> tuple[float, float]:
        pass

    @abstractmethod
    def get_funding_rate(self, product: str, currency: str, term_days: int) -> float:
        pass

    @abstractmethod
    def get_default_probability(self, product: str, months: int) -> np.ndarray:
        pass
