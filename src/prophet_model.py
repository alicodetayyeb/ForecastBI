"""
Prophet time-series forecasting model for commodity price prediction.
"""

from typing import Dict, Any, Tuple
import pandas as pd


def prepare_prophet_dataframe(df: pd.DataFrame, commodity_name: str) -> pd.DataFrame:
    """
    Format commodity price series to Prophet's required columns: ['ds', 'y'].
    """
    # TODO: Filter by commodity and rename columns to ds and y
    pass


def train_prophet_model(df_prophet: pd.DataFrame, yearly_seasonality: bool = True) -> Any:
    """
    Instantiate and fit Facebook Prophet model with seasonal parameters.
    """
    # TODO: Fit Prophet model
    pass


def generate_prophet_forecast(model: Any, periods: int = 12, freq: str = "M") -> pd.DataFrame:
    """
    Generate next `periods` forecast with uncertainty upper/lower bounds.
    """
    # TODO: make_future_dataframe and predict
    pass


def run_all_prophet_forecasts(df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """
    Loop across all 7 target commodities and produce consolidated forecasts table.
    """
    # TODO: Run across all commodities
    pass
