"""
Utility functions for paths, logging, configuration, and data formatting.
"""

from pathlib import Path
from typing import List

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR = DATA_DIR / "output"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# 7 Target Commodities (strictly mirroring PBS terminology)
TARGET_COMMODITIES: List[str] = [
    "Tomatoes",
    "Onions",
    "Potatoes",
    "Pulse Moong (Washed)",
    "Pulse Gram",
    "Pulse Masoor (Washed)",
    "Pulse Mash (Washed)"
]

def ensure_directories_exist() -> None:
    """Create all standard project subdirectories if they do not exist."""
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, MODELS_DIR, FIGURES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_directories_exist()
    print("Project directories verified.")
