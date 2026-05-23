import os
import logging
import pandas as pd
import numpy as np
from app.domain.ports.market_parameters_port import MarketParametersPort
from app.domain.exceptions import ParametersNotFoundError, ProductNotFoundError
from app.adapters.csv.constants import (
    COSTS_FILE, RATES_FILE, PD_FILE, COSTS_COLUMNS, RATES_COLUMNS, PD_COLUMNS
)

logger = logging.getLogger(__name__)


class CSVParametersAdapter(MarketParametersPort):
    def __init__(self, data_path: str):
        self._costs = self._load_csv(data_path, COSTS_FILE, COSTS_COLUMNS)
        self._rates = self._load_csv(data_path, RATES_FILE, RATES_COLUMNS)
        self._pd = self._load_csv(data_path, PD_FILE, PD_COLUMNS)
        logger.info('CSV parameters loaded successfully from %s', data_path)

    def _load_csv(self, data_path: str, filename: str, columns: dict) -> pd.DataFrame:
        path = os.path.join(data_path, filename)
        try:
            return pd.read_csv(path).rename(columns=columns)
        except Exception as e:
            logger.error('Failed to load CSV %s: %s', filename, str(e))
            raise ParametersNotFoundError(f'Could not load {filename}') from e

    def get_costs(self, product: str, currency: str) -> tuple[float, float]:
        row = self._costs.loc[
            (self._costs['product'] == product) &
            (self._costs['currency'] == currency)
        ]

        if row.empty:
            raise ProductNotFoundError(f'{product}/{currency}')

        return (
            float(row['origination_cost'].values[0]),
            float(row['maintenance_cost'].values[0])
        )

    def get_funding_rate(self, product: str, currency: str, term_days: int) -> float:
        filtered = self._rates.loc[
            (self._rates['product'] == product) &
            (self._rates['currency'] == currency)
        ].sort_values('term_days')

        if filtered.empty:
            raise ProductNotFoundError(f'{product}/{currency}')

        return float(np.interp(term_days, filtered['term_days'].values, filtered['annual_rate'].values))

    def get_default_probability(self, product: str, months: int) -> np.ndarray:
        filtered = self._pd.loc[
            self._pd['product'] == product
        ].sort_values('month').head(months)

        if filtered.empty:
            raise ProductNotFoundError(product)
        return filtered['marginal_pd'].values


