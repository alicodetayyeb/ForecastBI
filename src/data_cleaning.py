"""
Data loading, cleaning, standardization, and missing value imputation for PBS data.
"""

from pathlib import Path
from typing import Optional
import pandas as pd

from src.utils import RAW_DATA_DIR, PROCESSED_DATA_DIR, TARGET_COMMODITIES


def load_raw_pbs_files(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """
    Load raw PBS excel/csv files from raw data folder and combine them.
    """
    # TODO: Implement multi-file reader (Excel/CSV/SPI tables)
    pass


def clean_commodity_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter for target 7 commodities, standardize column names,
    handle missing values, and structure dates.
    """
    # TODO: Implement commodity filtering and cleaning
    pass


def resample_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate weekly prices to monthly averages for smooth forecasting.
    """
    # TODO: Implement resampling to monthly average
    pass


def save_processed_data(df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """
    Save cleaned dataset to data/processed directory.
    """
    # TODO: Implement save logic
    pass


if __name__ == "__main__":
    print("Running Data Cleaning Pipeline...")
