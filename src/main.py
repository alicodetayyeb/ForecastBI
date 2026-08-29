"""
Main orchestrator for Phase 3: Modeling & Evaluation.
Runs Prophet and XGBoost on all commodities, evaluates them, and generates final forecasts.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, TARGET_COMMODITIES
from src.evaluate import evaluate_forecast, compile_accuracy_report
from src.prophet_model import backtest_prophet, predict_future_prophet
from src.xgboost_model import backtest_xgboost, predict_future_xgboost

def run_phase_3():
    feature_matrix_path = PROCESSED_DATA_DIR / "feature_matrix_all_commodities.csv"
    if not feature_matrix_path.exists():
        print(f"Error: {feature_matrix_path} not found. Run Phase 2 first.")
        sys.exit(1)
        
    df_features = pd.read_csv(feature_matrix_path)
    df_features['ds'] = pd.to_datetime(df_features['ds'])
    
    accuracy_results = []
    future_forecasts = []
    
    test_months = 6
    forecast_periods = 12
    
    print("============================================================")
    print(" ForecastBI - Phase 3: Modeling & Evaluation")
    print("============================================================")
    
    for comm in TARGET_COMMODITIES:
        print(f"\nProcessing {comm}...")
        df_comm = df_features[df_features['commodity'] == comm].copy()
        
        # --- Backtesting (6-month test set) ---
        print("  - Running Prophet backtest...")
        p_y_true, p_y_pred, _ = backtest_prophet(df_comm, comm, test_months)
        p_metrics = evaluate_forecast(p_y_true, p_y_pred)
        
        print("  - Running XGBoost backtest...")
        x_y_true, x_y_pred, _ = backtest_xgboost(df_comm, test_months)
        x_metrics = evaluate_forecast(x_y_true, x_y_pred)
        
        # Record metrics
        accuracy_results.append({
            "Commodity": comm,
            "Model": "Prophet",
            "MAPE_%": p_metrics["MAPE_%"],
            "RMSE": p_metrics["RMSE"],
            "MAE": p_metrics["MAE"]
        })
        accuracy_results.append({
            "Commodity": comm,
            "Model": "XGBoost",
            "MAPE_%": x_metrics["MAPE_%"],
            "RMSE": x_metrics["RMSE"],
            "MAE": x_metrics["MAE"]
        })
        
        # Calculate historical minimum price for this commodity to use as a floor
        historical_min = df_comm['y'].min()
        
        # --- Production Forecasting (12 months ahead) ---
        print("  - Generating 12-month Prophet forecast...")
        p_forecast = predict_future_prophet(df_comm, comm, forecast_periods)
        
        # Apply the historical minimum floor to Prophet predictions
        p_forecast['yhat'] = p_forecast['yhat'].clip(lower=historical_min)
        p_forecast['yhat_lower'] = p_forecast['yhat_lower'].clip(lower=historical_min)
        p_forecast['yhat_upper'] = p_forecast['yhat_upper'].clip(lower=historical_min)
        
        # Enforce strict logical ordering in case original bounds were flipped by floor
        p_forecast['yhat_upper'] = p_forecast[['yhat', 'yhat_upper']].max(axis=1)
        p_forecast['yhat_lower'] = p_forecast[['yhat', 'yhat_lower']].min(axis=1)
        
        future_forecasts.append(p_forecast)
        
        print("  - Generating 12-month XGBoost forecast...")
        x_forecast = predict_future_xgboost(df_comm, comm, forecast_periods)
        
        # Apply the historical minimum floor to XGBoost predictions
        x_forecast['yhat'] = x_forecast['yhat'].clip(lower=historical_min)
        future_forecasts.append(x_forecast)
        
    print("\n============================================================")
    print(" Compilation and Output Generation")
    print("============================================================")
    
    # Save Accuracy Report
    df_accuracy = compile_accuracy_report(accuracy_results)
    acc_path = OUTPUT_DATA_DIR / "model_accuracy.csv"
    df_accuracy.to_csv(acc_path, index=False)
    print(f"[OK] Model accuracy saved to: {acc_path}")
    
    # Save Future Forecasts
    df_future = pd.concat(future_forecasts, ignore_index=True)
    # Reorder columns nicely
    cols = ['commodity', 'model', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']
    df_future = df_future[cols]
    
    forecast_path = OUTPUT_DATA_DIR / "forecasts_next_year.csv"
    df_future.to_csv(forecast_path, index=False)
    print(f"[OK] 12-month future forecasts saved to: {forecast_path}")
    
    print("\nPhase 3 execution complete!")

if __name__ == "__main__":
    run_phase_3()
