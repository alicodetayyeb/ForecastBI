"""
Model evaluation, performance metrics computation (MAPE, RMSE, MAE), and comparison.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error in percentage (0-100%)."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    non_zero = y_true != 0
    return float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100)


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def evaluate_forecast(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate all standard metrics for a forecast."""
    return {
        "MAPE_%": round(calculate_mape(y_true, y_pred), 2),
        "RMSE": round(calculate_rmse(y_true, y_pred), 2),
        "MAE": round(calculate_mae(y_true, y_pred), 2)
    }


def compile_accuracy_report(results_list: list) -> pd.DataFrame:
    """
    Format and compile accuracy metrics for all models and commodities.
    results_list should be a list of dictionaries.
    """
    df = pd.DataFrame(results_list)
    return df
