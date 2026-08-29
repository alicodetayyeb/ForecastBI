"""
Prepare Power BI-optimized data tables from existing pipeline outputs.
Creates clean, dashboard-ready CSV files in data/output/powerbi/.
Original Python CSVs in data/output/ are NOT modified.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, TARGET_COMMODITIES

POWERBI_DIR = OUTPUT_DATA_DIR / "powerbi"


def prepare_historical_prices_table():
    """
    Table 1: Historical Prices (wide -> long for Power BI city slicer).
    Columns: Date, Commodity, Category, Unit, City, Price
    Plus a National Average row per commodity-month.
    """
    df = pd.read_csv(PROCESSED_DATA_DIR / "target_commodities_monthly_prices.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    cities = [
        "Islamabad", "Rawalpindi", "Gujranwala", "Sialkot", "Lahore",
        "Faisalabad", "Sargodha", "Multan", "Bahawalpur", "Karachi",
        "Hyderabad", "Sukkur", "Larkana", "Peshawar", "Bannu", "Quetta", "Khuzdar"
    ]

    rows = []

    for _, row in df.iterrows():
        base = {
            "Date": row["Date"],
            "Year_Month": row["Year_Month"],
            "Commodity": row["Target_Commodity"],
            "Category": row["Category"],
            "Unit": row["Unit"],
        }

        # National Average row
        rows.append({**base, "City": "National Average", "Price": row["National_Average_Price"]})

        # Individual city rows
        for city in cities:
            if pd.notna(row.get(city)):
                rows.append({**base, "City": city, "Price": row[city]})

    result = pd.DataFrame(rows)
    result["Date"] = result["Date"].dt.strftime("%Y-%m-%d")
    return result


def prepare_forecast_table():
    """
    Table 2: Future Forecasts with clean column names for Power BI.
    Columns: Date, Commodity, Model, Forecast_Price, Lower_Bound, Upper_Bound
    """
    df = pd.read_csv(OUTPUT_DATA_DIR / "forecasts_next_year.csv")
    df = df.rename(columns={
        "ds": "Date",
        "commodity": "Commodity",
        "model": "Model",
        "yhat": "Forecast_Price",
        "yhat_lower": "Lower_Bound",
        "yhat_upper": "Upper_Bound"
    })
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Fill missing bounds for XGBoost with +/- 10% as a simple heuristic
    mask = df["Model"] == "XGBoost"
    df.loc[mask, "Lower_Bound"] = df.loc[mask, "Forecast_Price"] * 0.90
    df.loc[mask, "Upper_Bound"] = df.loc[mask, "Forecast_Price"] * 1.10

    # Round for cleanliness
    for col in ["Forecast_Price", "Lower_Bound", "Upper_Bound"]:
        df[col] = df[col].round(2)

    return df


def prepare_accuracy_table():
    """
    Table 3: Model accuracy with a Winner flag for each commodity.
    Columns: Commodity, Model, MAPE, RMSE, MAE, Accuracy_Pct, Is_Winner
    """
    df = pd.read_csv(OUTPUT_DATA_DIR / "model_accuracy.csv")
    df = df.rename(columns={"MAPE_%": "MAPE"})

    # Add Accuracy % (100 - MAPE) for intuitive display
    df["Accuracy_Pct"] = (100 - df["MAPE"]).round(2)

    # Determine winner per commodity (lowest MAPE)
    df["Is_Winner"] = False
    for comm in df["Commodity"].unique():
        comm_mask = df["Commodity"] == comm
        min_mape_idx = df.loc[comm_mask, "MAPE"].idxmin()
        df.loc[min_mape_idx, "Is_Winner"] = True

    return df


def prepare_commodity_metadata_table():
    """
    Table 4: Commodity metadata for slicers and context.
    Columns: Commodity, Category, Unit, Volatility_Tier, Avg_Price, Best_Model
    """
    hist_df = pd.read_csv(PROCESSED_DATA_DIR / "target_commodities_monthly_prices.csv")
    acc_df = pd.read_csv(OUTPUT_DATA_DIR / "model_accuracy.csv")

    rows = []
    for comm in TARGET_COMMODITIES:
        comm_data = hist_df[hist_df["Target_Commodity"] == comm]
        avg_price = comm_data["National_Average_Price"].mean()
        cv = (comm_data["National_Average_Price"].std() / avg_price) * 100

        if cv > 25:
            tier = "High"
        elif cv > 12:
            tier = "Moderate"
        else:
            tier = "Low"

        category = comm_data["Category"].iloc[0] if len(comm_data) > 0 else "Unknown"
        unit = comm_data["Unit"].iloc[0] if len(comm_data) > 0 else "1 Kg"

        # Best model
        comm_acc = acc_df[acc_df["Commodity"] == comm]
        best_model = comm_acc.loc[comm_acc["MAPE_%"].idxmin(), "Model"] if len(comm_acc) > 0 else "N/A"

        rows.append({
            "Commodity": comm,
            "Category": category,
            "Unit": unit,
            "Volatility_Tier": tier,
            "Avg_Price_Rs": round(avg_price, 2),
            "CV_Pct": round(cv, 1),
            "Best_Model": best_model
        })

    return pd.DataFrame(rows)


def prepare_combined_timeline():
    """
    Table 5: Combined historical + forecast timeline for seamless Power BI line charts.
    Columns: Date, Commodity, Price, Price_Type (Actual/Forecast), Model, Lower_Bound, Upper_Bound
    """
    # Historical
    hist_df = pd.read_csv(PROCESSED_DATA_DIR / "target_commodities_monthly_prices.csv")
    hist_df["Date"] = pd.to_datetime(hist_df["Date"])

    hist_rows = []
    for _, row in hist_df.iterrows():
        hist_rows.append({
            "Date": row["Date"].strftime("%Y-%m-%d"),
            "Commodity": row["Target_Commodity"],
            "Price": round(row["National_Average_Price"], 2),
            "Price_Type": "Actual",
            "Model": "Historical",
            "Lower_Bound": None,
            "Upper_Bound": None
        })

    # Forecast
    fc_df = pd.read_csv(OUTPUT_DATA_DIR / "forecasts_next_year.csv")
    fc_df["ds"] = pd.to_datetime(fc_df["ds"])

    fc_rows = []
    for _, row in fc_df.iterrows():
        lower = row["yhat_lower"] if pd.notna(row["yhat_lower"]) else row["yhat"] * 0.90
        upper = row["yhat_upper"] if pd.notna(row["yhat_upper"]) else row["yhat"] * 1.10
        
        # Ensure logical bounds
        lower = min(lower, row["yhat"])
        upper = max(upper, row["yhat"])
        
        fc_rows.append({
            "Date": row["ds"].strftime("%Y-%m-%d"),
            "Commodity": row["commodity"],
            "Price": round(row["yhat"], 2),
            "Price_Type": "Forecast",
            "Model": row["model"],
            "Lower_Bound": round(lower, 2),
            "Upper_Bound": round(upper, 2)
        })

    combined = pd.DataFrame(hist_rows + fc_rows)
    return combined


if __name__ == "__main__":
    print("=" * 60)
    print(" ForecastBI - Power BI Data Preparation")
    print("=" * 60)

    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    # Table 1: Historical Prices (long format)
    print("\n[1/5] Preparing Historical Prices (long format)...")
    t1 = prepare_historical_prices_table()
    t1.to_csv(POWERBI_DIR / "pbi_historical_prices.csv", index=False)
    print(f"  [OK] {len(t1)} rows -> pbi_historical_prices.csv")

    # Table 2: Forecast
    print("[2/5] Preparing Forecast Table...")
    t2 = prepare_forecast_table()
    t2.to_csv(POWERBI_DIR / "pbi_forecasts.csv", index=False)
    print(f"  [OK] {len(t2)} rows -> pbi_forecasts.csv")

    # Table 3: Model Accuracy
    print("[3/5] Preparing Model Accuracy Table...")
    t3 = prepare_accuracy_table()
    t3.to_csv(POWERBI_DIR / "pbi_model_accuracy.csv", index=False)
    print(f"  [OK] {len(t3)} rows -> pbi_model_accuracy.csv")

    # Table 4: Commodity Metadata
    print("[4/5] Preparing Commodity Metadata...")
    t4 = prepare_commodity_metadata_table()
    t4.to_csv(POWERBI_DIR / "pbi_commodity_metadata.csv", index=False)
    print(f"  [OK] {len(t4)} rows -> pbi_commodity_metadata.csv")

    # Table 5: Combined Timeline
    print("[5/5] Preparing Combined Timeline (Historical + Forecast)...")
    t5 = prepare_combined_timeline()
    t5.to_csv(POWERBI_DIR / "pbi_combined_timeline.csv", index=False)
    print(f"  [OK] {len(t5)} rows -> pbi_combined_timeline.csv")

    print("\n" + "=" * 60)
    print(f" All Power BI tables saved to: {POWERBI_DIR}")
    print(" Original Python CSVs are untouched.")
    print("=" * 60)
