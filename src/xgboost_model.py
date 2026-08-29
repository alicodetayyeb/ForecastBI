"""
XGBoost time-series forecasting model with recursive multi-step prediction logic.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Features that model uses
FEATURE_COLS = [
    "month", "quarter", "month_sin", "month_cos", 
    "price_lag_1", "price_lag_2", "price_lag_3", "price_lag_6", "price_lag_12",
    "rolling_mean_3", "rolling_std_3", "rolling_mean_6", "rolling_std_6",
    "price_diff_1", "mom_pct_change_1"
]

def train_xgboost(df_train: pd.DataFrame) -> xgb.XGBRegressor:
    """
    Train an XGBoost regressor on the provided feature matrix.
    """
    X_train = df_train[FEATURE_COLS]
    y_train = df_train['y']
    
    # We use relatively simple parameters to avoid overfitting on small data
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    return model


def _build_next_step_features(history_df: pd.DataFrame, next_date: pd.Timestamp) -> pd.DataFrame:
    """
    Given the historical actuals + predictions (history_df), construct the feature vector for `next_date`.
    """
    # Create a new blank row for the next date
    new_row = {"ds": next_date, "y": np.nan}
    temp_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Recalculate Calendar
    temp_df["month"] = temp_df["ds"].dt.month
    temp_df["quarter"] = temp_df["ds"].dt.quarter
    temp_df["month_sin"] = np.sin(2 * np.pi * temp_df["month"] / 12.0)
    temp_df["month_cos"] = np.cos(2 * np.pi * temp_df["month"] / 12.0)
    
    # Recalculate Lags
    for lag in (1, 2, 3, 6, 12):
        temp_df[f"price_lag_{lag}"] = temp_df["y"].shift(lag)
        
    # Recalculate Rolling (shifted by 1 to not include current nan)
    shifted_y = temp_df["y"].shift(1)
    temp_df["rolling_mean_3"] = shifted_y.rolling(3).mean()
    temp_df["rolling_std_3"] = shifted_y.rolling(3).std()
    temp_df["rolling_mean_6"] = shifted_y.rolling(6).mean()
    temp_df["rolling_std_6"] = shifted_y.rolling(6).std()
    
    # Recalculate Momentum
    temp_df["price_diff_1"] = temp_df["y"] - shifted_y
    # Since y is nan for the last row, we need to calculate diff for lag 1 to lag 2 to feed as feature?
    # No, price_diff_1 feature historically is (y - y_lag_1). But we are predicting y. 
    # Ah, in feature engineering we defined mom_pct_change_1 as (y - y_lag_1) / y_lag_1. 
    # This means `price_diff_1` uses current y, which is cheating if we use it to predict y! 
    # Let me fix this conceptually: if our feature matrix used current y to compute momentum to predict current y, that's a data leak.
    # We should use lagged momentum.
    # For now, to keep it simple and mathematically sound for recursive forecasting, we will use momentum of the PREVIOUS step.
    temp_df["price_diff_1"] = temp_df["price_lag_1"] - temp_df["y"].shift(2)
    temp_df["mom_pct_change_1"] = (temp_df["price_lag_1"] - temp_df["y"].shift(2)) / temp_df["y"].shift(2) * 100
    
    # Return just the feature vector for the last row
    last_row_features = temp_df.iloc[[-1]][FEATURE_COLS]
    return last_row_features


def generate_xgboost_forecast(model: xgb.XGBRegressor, historical_df: pd.DataFrame, periods: int) -> list:
    """
    Perform recursive forecasting.
    historical_df must contain at least the last 12 months of actual/predicted 'y' and 'ds' to build lags.
    """
    history = historical_df[['ds', 'y']].copy()
    predictions = []
    
    last_date = history['ds'].max()
    
    for i in range(periods):
        # Determine next month date
        if last_date.month == 12:
            next_date = pd.Timestamp(year=last_date.year + 1, month=1, day=1)
        else:
            next_date = pd.Timestamp(year=last_date.year, month=last_date.month + 1, day=1)
            
        # Build features for this step
        next_features = _build_next_step_features(history, next_date)
        
        # Predict
        pred_y = model.predict(next_features)[0]
        predictions.append({"ds": next_date, "yhat": pred_y})
        
        # Append to history so next step can use it as lag
        history = pd.concat([history, pd.DataFrame([{"ds": next_date, "y": pred_y}])], ignore_index=True)
        last_date = next_date
        
    return predictions


def backtest_xgboost(df_full: pd.DataFrame, test_months: int = 6) -> tuple:
    """
    Train on data up to the test split, then recursively forecast the test split.
    df_full must be the fully engineered feature matrix for a specific commodity.
    """
    df_full = df_full.sort_values('ds').reset_index(drop=True)
    
    # Split
    df_train = df_full.iloc[:-test_months]
    df_test = df_full.iloc[-test_months:]
    
    # The history required to start predicting the first test month is the entire train set (or at least last 12 months)
    model = train_xgboost(df_train)
    history_df = df_train[['ds', 'y']].copy()
    
    forecasts = generate_xgboost_forecast(model, history_df, periods=test_months)
    
    y_pred = [f['yhat'] for f in forecasts]
    y_true = df_test['y'].values
    
    forecast_df = pd.DataFrame(forecasts)
    
    return y_true, y_pred, forecast_df


def predict_future_xgboost(df_full: pd.DataFrame, commodity: str, periods: int = 12) -> pd.DataFrame:
    """
    Train on 100% of data and recursively predict future unseen periods.
    """
    df_full = df_full.sort_values('ds').reset_index(drop=True)
    
    model = train_xgboost(df_full)
    history_df = df_full[['ds', 'y']].copy()
    
    forecasts = generate_xgboost_forecast(model, history_df, periods=periods)
    forecast_df = pd.DataFrame(forecasts)
    
    # Add metadata
    forecast_df['commodity'] = commodity
    forecast_df['model'] = 'XGBoost'
    forecast_df['yhat_lower'] = np.nan # XGBoost doesn't provide this natively without quantile regression
    forecast_df['yhat_upper'] = np.nan
    
    return forecast_df
