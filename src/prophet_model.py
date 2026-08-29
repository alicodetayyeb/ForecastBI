"""
Prophet time-series forecasting model for commodity price prediction.
"""

import sys
from pathlib import Path
import pandas as pd
from prophet import Prophet
import logging

# Add project root to sys.path for direct script execution
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Suppress Prophet logs
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
import warnings
warnings.filterwarnings('ignore')


def train_prophet_model(df_train: pd.DataFrame, is_vegetable: bool) -> Prophet:
    """
    Instantiate and fit Facebook Prophet model.
    Vegetables get higher seasonality flexibility due to volatility.
    """
    if is_vegetable:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative', # Vegetables fluctuate more when base price is higher
            changepoint_prior_scale=0.1
        )
    else:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',
            changepoint_prior_scale=0.05
        )
        
    model.fit(df_train[['ds', 'y']])
    return model


def generate_prophet_forecast(model: Prophet, periods: int = 12) -> pd.DataFrame:
    """
    Generate future forecast with uncertainty bounds.
    """
    future = model.make_future_dataframe(periods=periods, freq='MS') # Month Start
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)


def backtest_prophet(df_full: pd.DataFrame, commodity: str, test_months: int = 6) -> tuple:
    """
    Train on historical data, predict on the last `test_months`.
    """
    # Sort chronologically
    df_full = df_full.sort_values('ds').reset_index(drop=True)
    
    # Split
    df_train = df_full.iloc[:-test_months]
    df_test = df_full.iloc[-test_months:]
    
    is_veg = commodity in ["Tomatoes", "Onions", "Potatoes"]
    
    model = train_prophet_model(df_train, is_vegetable=is_veg)
    forecast = generate_prophet_forecast(model, periods=test_months)
    
    # Align forecast dates with test dates just to be safe
    y_pred = forecast['yhat'].values
    y_true = df_test['y'].values
    
    return y_true, y_pred, forecast


def predict_future_prophet(df_full: pd.DataFrame, commodity: str, periods: int = 12) -> pd.DataFrame:
    """
    Train on 100% of data and predict the future unseen `periods`.
    """
    df_full = df_full.sort_values('ds').reset_index(drop=True)
    is_veg = commodity in ["Tomatoes", "Onions", "Potatoes"]
    
    model = train_prophet_model(df_full, is_vegetable=is_veg)
    forecast = generate_prophet_forecast(model, periods=periods)
    
    # Add metadata
    forecast['commodity'] = commodity
    forecast['model'] = 'Prophet'
    
    return forecast
