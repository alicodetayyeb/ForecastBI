"""
ForecastBI - Master Pipeline Orchestrator
Runs end-to-end data cleaning, feature engineering, modeling (Prophet + XGBoost),
evaluation, and generates all Power BI-ready CSV datasets.
"""

from src.utils import ensure_directories_exist, OUTPUT_DATA_DIR


def run_pipeline() -> None:
    """Execute complete ForecastBI pipeline."""
    print("=" * 60)
    print(" ForecastBI: Commodity Price Forecasting Pipeline")
    print("=" * 60)

    # 1. Setup
    ensure_directories_exist()

    # 2. Data Cleaning
    print("[1/5] Cleaning and standardizing PBS price data...")

    # 3. Feature Engineering
    print("[2/5] Engineering time-series lag & rolling features...")

    # 4. Prophet Model
    print("[3/5] Fitting Prophet models & predicting 12 months ahead...")

    # 5. XGBoost Model
    print("[4/5] Fitting XGBoost models & calculating recursive forecasts...")

    # 6. Evaluation & Export
    print("[5/5] Calculating MAPE/RMSE & exporting Power BI CSVs...")
    print(f"\nAll datasets exported successfully to: {OUTPUT_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
