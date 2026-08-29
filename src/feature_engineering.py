"""
Feature Engineering for time series ML models (lags, rolling stats, seasonality indicators).
Generates the feature matrix required for XGBoost.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path for direct script execution
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import PROCESSED_DATA_DIR, TARGET_COMMODITIES
from src.data_cleaning import load_compiled_target_data, get_commodity_timeseries


def create_calendar_features(df: pd.DataFrame, date_col: str = "ds") -> pd.DataFrame:
    """
    Extract calendar components: month, quarter, year, cyclical sin/cos transforms.
    """
    df = df.copy()
    df["month"] = df[date_col].dt.month
    df["quarter"] = df[date_col].dt.quarter
    
    # Cyclical encoding for month
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)
    
    return df


def create_lag_features(df: pd.DataFrame, target_col: str = "y", lags=(1, 2, 3, 6, 12)) -> pd.DataFrame:
    """
    Generate historical lag features for the target price column.
    """
    df = df.copy()
    for lag in lags:
        df[f"price_lag_{lag}"] = df[target_col].shift(lag)
    return df


def create_rolling_window_features(df: pd.DataFrame, target_col: str = "y", windows=(3, 6)) -> pd.DataFrame:
    """
    Calculate rolling mean and standard deviation over given windows.
    """
    df = df.copy()
    for window in windows:
        # We shift by 1 before rolling to avoid data leakage (using current month's price to predict current month)
        shifted = df[target_col].shift(1)
        df[f"rolling_mean_{window}"] = shifted.rolling(window=window).mean()
        df[f"rolling_std_{window}"] = shifted.rolling(window=window).std()
    return df


def create_momentum_features(df: pd.DataFrame, target_col: str = "y") -> pd.DataFrame:
    """
    Calculate lagged month-over-month % change and first difference to avoid data leakage.
    These features represent the momentum of the previous month.
    """
    df = df.copy()
    lag_1 = df[target_col].shift(1)
    lag_2 = df[target_col].shift(2)
    df["price_diff_1"] = lag_1 - lag_2
    df["mom_pct_change_1"] = (lag_1 - lag_2) / lag_2 * 100
    return df


def build_ml_feature_matrix() -> pd.DataFrame:
    """
    Combine all feature engineering steps for all commodities.
    Saves and returns the final feature matrix.
    """
    df_raw = load_compiled_target_data()
    all_features = []
    
    for comm in TARGET_COMMODITIES:
        # Extract time series for this commodity
        ts_df = get_commodity_timeseries(df_raw, comm)
        
        # Apply feature engineering
        ts_df = create_calendar_features(ts_df, date_col="ds")
        ts_df = create_lag_features(ts_df, target_col="y", lags=(1, 2, 3, 6, 12))
        ts_df = create_rolling_window_features(ts_df, target_col="y", windows=(3, 6))
        ts_df = create_momentum_features(ts_df, target_col="y")
        
        all_features.append(ts_df)
    
    # Combine all commodities
    final_df = pd.concat(all_features, ignore_index=True)
    
    # Drop rows with NaN values (these are the first 12 months due to lag_12)
    final_df = final_df.dropna().reset_index(drop=True)
    
    # Save to processed data directory
    output_path = PROCESSED_DATA_DIR / "feature_matrix_all_commodities.csv"
    final_df.to_csv(output_path, index=False)
    
    return final_df


if __name__ == "__main__":
    print("=" * 60)
    print(" ForecastBI - Phase 2: Feature Engineering")
    print("=" * 60)
    
    print("Building feature matrix for 7 commodities...")
    feature_matrix = build_ml_feature_matrix()
    
    print(f"\nFeature Matrix Shape: {feature_matrix.shape}")
    print(f"Total columns: {len(feature_matrix.columns)}")
    print("\nColumns generated:")
    for col in feature_matrix.columns:
        print(f"  - {col}")
        
    print("\nChecking for missing values:")
    missing = feature_matrix.isnull().sum().sum()
    print(f"  Total NaN values: {missing}")
    
    print("\nRecords per commodity:")
    print(feature_matrix["commodity"].value_counts().to_string())
    
    output_file = PROCESSED_DATA_DIR / "feature_matrix_all_commodities.csv"
    print(f"\nFeature matrix saved successfully to: {output_file}")
    print("=" * 60)
