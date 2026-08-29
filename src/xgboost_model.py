"""
XGBoost Regression model for recursive time-series forecasting of commodity prices.
"""

from typing import Dict, Any, Tuple
import pandas as pd


def prepare_train_test_split(df_features: pd.DataFrame, test_size_months: int = 12) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split time series into chronological train and test sets without lookahead bias.
    """
    # TODO: Chronological train-test split
    pass


def train_xgboost_model(X_train: pd.DataFrame, y_train: pd.Series) -> Any:
    """
    Train an XGBoost regressor model.
    """
    # TODO: Instantiate and fit XGBRegressor
    pass


def recursive_multistep_forecast(model: Any, last_known_features: pd.DataFrame, steps: int = 12) -> pd.DataFrame:
    """
    Generate recursive multi-step forecasts for the next 12 months.
    """
    # TODO: Multi-step recursive forecasting
    pass


def run_all_xgboost_forecasts(df: pd.DataFrame, steps: int = 12) -> pd.DataFrame:
    """
    Train and forecast with XGBoost across all 7 commodities.
    """
    # TODO: Loop over commodities and predict
    pass
