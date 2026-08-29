"""
Model evaluation, performance metrics computation (MAPE, RMSE, MAE, R2), and comparison.
"""

from typing import Dict
import pandas as pd
import numpy as np


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error in percentage (0-100%)."""
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def evaluate_models_comparison(y_true: pd.Series, y_pred_prophet: pd.Series, y_pred_xgboost: pd.Series) -> pd.DataFrame:
    """
    Compute metrics table comparing Prophet vs XGBoost.
    """
    # TODO: Build comparison table per commodity
    pass


def generate_accuracy_report(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format and export final accuracy comparison CSV for Power BI.
    """
    # TODO: Export accuracy CSV
    pass
