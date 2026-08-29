"""
Data loading, cleaning, standardization, and compilation for PBS Excel and PDF datasets.
"""

import sys
from pathlib import Path
from typing import Optional
import pandas as pd

# Add project root to sys.path for direct script execution
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, TARGET_COMMODITIES


def load_compiled_target_data(processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """
    Load the compiled target commodities monthly price dataset.
    """
    target_file = processed_dir / "target_commodities_monthly_prices.csv"
    if not target_file.exists():
        from compile_pbs_data import main as run_compiler
        run_compiler()
        
    df = pd.read_csv(target_file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def load_compiled_master_data(processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """
    Load all 51 commodities compiled dataset.
    """
    master_file = processed_dir / "master_all_commodities_monthly_prices.csv"
    if not master_file.exists():
        from compile_pbs_data import main as run_compiler
        run_compiler()
        
    df = pd.read_csv(master_file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def get_commodity_timeseries(df: pd.DataFrame, commodity_name: str) -> pd.DataFrame:
    """
    Extract a single commodity's time-series formatted for Prophet/XGBoost (ds, y).
    """
    sub = df[df["Target_Commodity"] == commodity_name].sort_values("Date").copy()
    ts_df = pd.DataFrame({
        "ds": sub["Date"],
        "y": sub["National_Average_Price"],
        "commodity": commodity_name,
        "unit": sub["Unit"].iloc[0] if len(sub) > 0 else "1 Kg"
    })
    return ts_df.reset_index(drop=True)


if __name__ == "__main__":
    print("Running Data Cleaning & Ingestion Pipeline...")
    df_target = load_compiled_target_data()
    print(f"Target Commodities Data Loaded: {len(df_target)} records spanning {df_target['Date'].min().date()} to {df_target['Date'].max().date()}")
    for comm in TARGET_COMMODITIES:
        ts = get_commodity_timeseries(df_target, comm)
        print(f"  * {comm:15s}: {len(ts)} observations | Latest price: Rs {ts['y'].iloc[-1]:.2f}")
