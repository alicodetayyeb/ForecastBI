"""
Feature Engineering for time series ML models (lags, rolling stats, seasonality indicators).
"""

import pandas as pd


def create_calendar_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Extract calendar components: month, quarter, year, cyclical sin/cos transforms.
    """
    # TODO: Add month, quarter, sin/cos encoding of month
    pass


def create_lag_features(df: pd.DataFrame, target_col: str = "price_pkr", lags=(1, 2, 3, 6, 12)) -> pd.DataFrame:
    """
    Generate historical lag features for the target price column.
    """
    # TODO: Add lag price columns
    pass


def create_rolling_window_features(df: pd.DataFrame, target_col: str = "price_pkr", windows=(3, 6, 12)) -> pd.DataFrame:
    """
    Calculate rolling mean, standard deviation, min, max over given windows.
    """
    # TODO: Add rolling statistics
    pass


def build_ml_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine calendar, lag, and rolling features into a unified dataset for XGBoost.
    """
    # TODO: Combine all feature engineering steps
    pass
