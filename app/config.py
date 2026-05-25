from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tea_min: float = 0.01
    tea_max: float = 0.8
    tolerance: float = 1e-6
    max_iterations: int = 100
    days_per_month: int = 30
    data_path: str = 'data'
    costs_file: str = 'costos final_1.csv'
    rates_file: str = 'transferencia final_final.csv'
    pd_file: str = 'pd final_final_2.csv'
    log_level: str = 'INFO'

    model_config = {'env_file': '.env'}


@lru_cache
def get_settings() -> Settings:
    return Settings()
