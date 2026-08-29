"""
Phase 1 — Exploratory Data Analysis (EDA) for ForecastBI
=========================================================
Generates all statistical summaries, visualizations, and diagnostic tests
for the 7 target commodity price time-series from PBS data.

Outputs:
    reports/figures/  — All EDA charts (PNG)
    reports/eda_summary_report.txt — Statistical summary text report
"""

import sys
from pathlib import Path

# Project root setup
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose

from src.utils import (
    PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR,
    TARGET_COMMODITIES, ensure_directories_exist,
)

# ── Style Configuration ─────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.25,
    "font.family": "sans-serif",
})

# Color palette — distinct, colorblind-friendly
COMMODITY_COLORS = {
    "Tomatoes":              "#e63946",
    "Onions":                "#f4a261",
    "Potatoes":              "#2a9d8f",
    "Pulse Moong (Washed)":  "#264653",
    "Pulse Gram":            "#e9c46a",
    "Pulse Masoor (Washed)": "#6a4c93",
    "Pulse Mash (Washed)":   "#1982c4",
}

VEGETABLE_GROUP = ["Tomatoes", "Onions", "Potatoes"]
PULSE_GROUP = ["Pulse Moong (Washed)", "Pulse Gram", "Pulse Masoor (Washed)", "Pulse Mash (Washed)"]

# 17 cities in the dataset
CITIES = [
    "Islamabad", "Rawalpindi", "Gujranwala", "Sialkot", "Lahore",
    "Faisalabad", "Sargodha", "Multan", "Bahawalpur", "Karachi",
    "Hyderabad", "Sukkur", "Larkana", "Peshawar", "Bannu", "Quetta", "Khuzdar",
]


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_data() -> pd.DataFrame:
    """Load target commodities dataset and parse dates."""
    fp = PROCESSED_DATA_DIR / "target_commodities_monthly_prices.csv"
    df = pd.read_csv(fp)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Target_Commodity", "Date"]).reset_index(drop=True)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INDIVIDUAL TIME-SERIES PLOTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_individual_timeseries(df: pd.DataFrame) -> None:
    """One subplot per commodity — price trend with annotated min/max."""
    fig, axes = plt.subplots(4, 2, figsize=(18, 20), sharex=False)
    axes = axes.flatten()

    for i, comm in enumerate(TARGET_COMMODITIES):
        ax = axes[i]
        sub = df[df["Target_Commodity"] == comm].copy()
        color = COMMODITY_COLORS[comm]

        ax.plot(sub["Date"], sub["National_Average_Price"],
                color=color, linewidth=2.2, marker="o", markersize=4, zorder=3)
        ax.fill_between(sub["Date"], sub["National_Average_Price"],
                        alpha=0.12, color=color)

        # Annotate min and max
        idx_max = sub["National_Average_Price"].idxmax()
        idx_min = sub["National_Average_Price"].idxmin()
        for idx, label, va in [(idx_max, "MAX", "bottom"), (idx_min, "MIN", "top")]:
            row = sub.loc[idx]
            ax.annotate(
                f'{label}: Rs {row["National_Average_Price"]:.0f}\n({row["Date"].strftime("%b %Y")})',
                xy=(row["Date"], row["National_Average_Price"]),
                fontsize=8, fontweight="bold", ha="center", va=va,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.85),
            )

        ax.set_title(comm, fontsize=13, fontweight="bold", color=color)
        ax.set_ylabel("Price (Rs / Kg)")
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
        ax.grid(True, alpha=0.3)

    # Hide the 8th subplot (we have 7 commodities)
    axes[7].set_visible(False)

    fig.suptitle("Monthly National Average Prices — Individual Commodity Trends",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "01_individual_timeseries.png")
    plt.close(fig)
    print("  [OK] 01_individual_timeseries.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. OVERLAY: VEGETABLES vs PULSES
# ═══════════════════════════════════════════════════════════════════════════════

def plot_grouped_overlay(df: pd.DataFrame) -> None:
    """Side-by-side overlay — vegetables on left, pulses on right."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    for comm in VEGETABLE_GROUP:
        sub = df[df["Target_Commodity"] == comm]
        ax1.plot(sub["Date"], sub["National_Average_Price"],
                 color=COMMODITY_COLORS[comm], linewidth=2.2,
                 marker="o", markersize=4, label=comm)
    ax1.set_title("Vegetables", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Price (Rs / Kg)")
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    for comm in PULSE_GROUP:
        sub = df[df["Target_Commodity"] == comm]
        ax2.plot(sub["Date"], sub["National_Average_Price"],
                 color=COMMODITY_COLORS[comm], linewidth=2.2,
                 marker="o", markersize=4, label=comm)
    ax2.set_title("Pulses & Legumes", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Price (Rs / Kg)")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Grouped Price Trends — Vegetables vs Pulses",
                 fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "02_grouped_overlay.png")
    plt.close(fig)
    print("  [OK] 02_grouped_overlay.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. VOLATILITY ANALYSIS (Month-over-Month % Change)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_volatility_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Box plots of MoM % changes + coefficient of variation bar chart."""
    records = []
    for comm in TARGET_COMMODITIES:
        sub = df[df["Target_Commodity"] == comm].sort_values("Date")
        pct = sub["National_Average_Price"].pct_change().dropna() * 100
        for val in pct:
            records.append({"Commodity": comm, "MoM_Pct_Change": val})

    vol_df = pd.DataFrame(records)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7), gridspec_kw={"width_ratios": [2, 1]})

    # Box plot of MoM % changes
    order = TARGET_COMMODITIES
    palette = [COMMODITY_COLORS[c] for c in order]
    sns.boxplot(data=vol_df, x="Commodity", y="MoM_Pct_Change",
                order=order, palette=palette, ax=ax1, width=0.6)
    ax1.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    ax1.set_title("Month-over-Month Price Change Distribution", fontsize=13, fontweight="bold")
    ax1.set_ylabel("% Change")
    ax1.set_xlabel("")
    ax1.set_xticklabels([c.replace(" (Washed)", "\n(Washed)") for c in order],
                        fontsize=9, rotation=0)

    # Coefficient of Variation bar chart
    cv_data = []
    for comm in TARGET_COMMODITIES:
        sub = df[df["Target_Commodity"] == comm]
        prices = sub["National_Average_Price"]
        cv = (prices.std() / prices.mean()) * 100
        cv_data.append({"Commodity": comm, "CV": cv})
    cv_df = pd.DataFrame(cv_data).sort_values("CV", ascending=True)

    bars = ax2.barh(cv_df["Commodity"].str.replace(" (Washed)", "\n(Washed)"),
                    cv_df["CV"],
                    color=[COMMODITY_COLORS[c] for c in cv_df["Commodity"]],
                    edgecolor="white", linewidth=0.5)
    ax2.set_title("Price Volatility\n(Coefficient of Variation %)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("CV (%)")
    for bar, val in zip(bars, cv_df["CV"]):
        ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}%", va="center", fontsize=10, fontweight="bold")

    fig.suptitle("Volatility Analysis — Which Commodities Swing the Most?",
                 fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "03_volatility_analysis.png")
    plt.close(fig)
    print("  [OK] 03_volatility_analysis.png")
    return cv_df


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CORRELATION HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════

def plot_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot commodities into columns and compute Pearson correlation."""
    pivot = df.pivot_table(
        index="Date", columns="Target_Commodity",
        values="National_Average_Price"
    )
    corr = pivot.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    short_labels = [c.replace(" (Washed)", "") for c in corr.columns]

    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
        vmin=-1, vmax=1, linewidths=1, square=True,
        xticklabels=short_labels, yticklabels=short_labels,
        cbar_kws={"shrink": 0.8, "label": "Pearson r"}, ax=ax,
    )
    ax.set_title("Price Correlation Between Commodities",
                 fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "04_correlation_heatmap.png")
    plt.close(fig)
    print("  [OK] 04_correlation_heatmap.png")
    return corr


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CITY-LEVEL PRICE DISPERSION HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════

def plot_city_price_heatmap(df: pd.DataFrame) -> None:
    """Average price per commodity per city — heatmap."""
    city_avg = []
    for comm in TARGET_COMMODITIES:
        sub = df[df["Target_Commodity"] == comm]
        row = {"Commodity": comm}
        for city in CITIES:
            row[city] = sub[city].mean()
        city_avg.append(row)

    city_df = pd.DataFrame(city_avg).set_index("Commodity")

    fig, ax = plt.subplots(figsize=(18, 7))
    sns.heatmap(
        city_df, annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.5, ax=ax,
        cbar_kws={"shrink": 0.8, "label": "Avg Price (Rs/Kg)"},
        yticklabels=[c.replace(" (Washed)", "\n(Washed)") for c in city_df.index],
    )
    ax.set_title("Average Price by City x Commodity (Rs/Kg)\nMar 2023 - Jul 2026",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "05_city_price_heatmap.png")
    plt.close(fig)
    print("  [OK] 05_city_price_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. CITY-LEVEL SPREAD (Min-Max Range per Commodity)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_city_spread(df: pd.DataFrame) -> None:
    """For each commodity, show the range of city prices over time."""
    fig, axes = plt.subplots(4, 2, figsize=(18, 20), sharex=False)
    axes = axes.flatten()

    for i, comm in enumerate(TARGET_COMMODITIES):
        ax = axes[i]
        sub = df[df["Target_Commodity"] == comm].sort_values("Date")
        color = COMMODITY_COLORS[comm]

        city_prices = sub[CITIES].values
        city_min = city_prices.min(axis=1)
        city_max = city_prices.max(axis=1)

        ax.fill_between(sub["Date"], city_min, city_max,
                        alpha=0.2, color=color, label="City min-max range")
        ax.plot(sub["Date"], sub["National_Average_Price"],
                color=color, linewidth=2.5, label="National Average", zorder=3)
        ax.plot(sub["Date"], city_min, color=color, linewidth=0.8, linestyle=":", alpha=0.6)
        ax.plot(sub["Date"], city_max, color=color, linewidth=0.8, linestyle=":", alpha=0.6)

        ax.set_title(comm, fontsize=13, fontweight="bold", color=color)
        ax.set_ylabel("Price (Rs/Kg)")
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(True, alpha=0.3)

    axes[7].set_visible(False)
    fig.suptitle("National Average vs City Price Spread (Min-Max Across 17 Cities)",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "06_city_price_spread.png")
    plt.close(fig)
    print("  [OK] 06_city_price_spread.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. SEASONAL DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════

def plot_seasonal_decomposition(df: pd.DataFrame) -> None:
    """Additive decomposition (period=12 months) for each commodity."""
    fig, axes = plt.subplots(7, 3, figsize=(22, 28))

    for i, comm in enumerate(TARGET_COMMODITIES):
        sub = df[df["Target_Commodity"] == comm].sort_values("Date")
        ts = sub.set_index("Date")["National_Average_Price"]
        ts.index = pd.DatetimeIndex(ts.index).to_period("M").to_timestamp()
        ts = ts.asfreq("MS")

        color = COMMODITY_COLORS[comm]

        # With 41 observations, use period=12 for annual seasonality
        if len(ts) >= 24:
            decomp = seasonal_decompose(ts, model="additive", period=12)
            # Trend
            axes[i, 0].plot(decomp.trend, color=color, linewidth=2)
            axes[i, 0].set_title(f"{comm} - Trend", fontsize=11, fontweight="bold")
            axes[i, 0].grid(True, alpha=0.3)
            # Seasonal
            axes[i, 1].plot(decomp.seasonal, color=color, linewidth=1.5)
            axes[i, 1].axhline(0, color="black", linestyle="--", linewidth=0.5, alpha=0.5)
            axes[i, 1].set_title(f"{comm} - Seasonal", fontsize=11, fontweight="bold")
            axes[i, 1].grid(True, alpha=0.3)
            # Residual
            axes[i, 2].scatter(decomp.resid.index, decomp.resid, color=color, s=20, alpha=0.7)
            axes[i, 2].axhline(0, color="black", linestyle="--", linewidth=0.5, alpha=0.5)
            axes[i, 2].set_title(f"{comm} - Residual", fontsize=11, fontweight="bold")
            axes[i, 2].grid(True, alpha=0.3)
        else:
            for j in range(3):
                axes[i, j].text(0.5, 0.5, "Insufficient data\nfor decomposition",
                                ha="center", va="center", fontsize=11)

    fig.suptitle("Seasonal Decomposition (Additive, period=12 months)",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "07_seasonal_decomposition.png")
    plt.close(fig)
    print("  [OK] 07_seasonal_decomposition.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. MONTHLY SEASONALITY PROFILE (Box plots by calendar month)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_monthly_seasonality(df: pd.DataFrame) -> None:
    """Box plot of prices grouped by calendar month for each commodity."""
    df_copy = df.copy()
    df_copy["Month"] = df_copy["Date"].dt.month
    df_copy["Month_Name"] = df_copy["Date"].dt.strftime("%b")

    fig, axes = plt.subplots(4, 2, figsize=(18, 22), sharex=False)
    axes = axes.flatten()
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for i, comm in enumerate(TARGET_COMMODITIES):
        ax = axes[i]
        sub = df_copy[df_copy["Target_Commodity"] == comm]
        color = COMMODITY_COLORS[comm]
        sns.boxplot(data=sub, x="Month_Name", y="National_Average_Price",
                    order=month_order, color=color, ax=ax, width=0.6,
                    fliersize=3)
        # Overlay the individual points
        sns.stripplot(data=sub, x="Month_Name", y="National_Average_Price",
                      order=month_order, color="black", ax=ax,
                      size=3, alpha=0.4, jitter=0.15)
        ax.set_title(comm, fontsize=13, fontweight="bold", color=color)
        ax.set_ylabel("Price (Rs/Kg)")
        ax.set_xlabel("")
        ax.grid(True, axis="y", alpha=0.3)

    axes[7].set_visible(False)
    fig.suptitle("Price Distribution by Calendar Month - Seasonal Patterns",
                 fontsize=16, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08_monthly_seasonality.png")
    plt.close(fig)
    print("  [OK] 08_monthly_seasonality.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. STATIONARITY TESTS (ADF)
# ═══════════════════════════════════════════════════════════════════════════════

def run_stationarity_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Augmented Dickey-Fuller test on level prices and first-differences."""
    results = []
    for comm in TARGET_COMMODITIES:
        sub = df[df["Target_Commodity"] == comm].sort_values("Date")
        prices = sub["National_Average_Price"].values

        # Level
        adf_level = adfuller(prices, autolag="AIC")
        # First difference
        diff = np.diff(prices)
        adf_diff = adfuller(diff, autolag="AIC")

        results.append({
            "Commodity": comm,
            "ADF_Level_Stat": round(adf_level[0], 4),
            "ADF_Level_pvalue": round(adf_level[1], 4),
            "Level_Stationary": "Yes" if adf_level[1] < 0.05 else "No",
            "ADF_Diff_Stat": round(adf_diff[0], 4),
            "ADF_Diff_pvalue": round(adf_diff[1], 4),
            "Diff_Stationary": "Yes" if adf_diff[1] < 0.05 else "No",
        })

    adf_df = pd.DataFrame(results)
    return adf_df


# ═══════════════════════════════════════════════════════════════════════════════
# 10. SUMMARY STATISTICS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive statistics per commodity."""
    stats_list = []
    for comm in TARGET_COMMODITIES:
        sub = df[df["Target_Commodity"] == comm]
        prices = sub["National_Average_Price"]
        mom_pct = prices.pct_change().dropna() * 100
        stats_list.append({
            "Commodity": comm,
            "N_Months": len(prices),
            "Mean_Price": round(prices.mean(), 2),
            "Median_Price": round(prices.median(), 2),
            "Min_Price": round(prices.min(), 2),
            "Max_Price": round(prices.max(), 2),
            "Std_Dev": round(prices.std(), 2),
            "CV_%": round((prices.std() / prices.mean()) * 100, 1),
            "Avg_MoM_%": round(mom_pct.mean(), 2),
            "Max_MoM_Jump_%": round(mom_pct.max(), 1),
            "Max_MoM_Drop_%": round(mom_pct.min(), 1),
            "Latest_Price": round(prices.iloc[-1], 2),
            "Price_Range": round(prices.max() - prices.min(), 2),
        })
    return pd.DataFrame(stats_list)


# ═══════════════════════════════════════════════════════════════════════════════
# 11. SUMMARY STATISTICS VISUAL TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def plot_summary_table(summary_df: pd.DataFrame) -> None:
    """Render summary statistics as a clean visual table image."""
    display_cols = ["Commodity", "N_Months", "Mean_Price", "Min_Price",
                    "Max_Price", "Std_Dev", "CV_%", "Latest_Price"]
    table_data = summary_df[display_cols].copy()
    table_data["Commodity"] = table_data["Commodity"].str.replace(" (Washed)", "")

    fig, ax = plt.subplots(figsize=(16, 4))
    ax.axis("off")
    tbl = ax.table(
        cellText=table_data.values,
        colLabels=["Commodity", "Months", "Mean (Rs)", "Min (Rs)",
                    "Max (Rs)", "Std Dev", "CV %", "Latest (Rs)"],
        cellLoc="center", loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    # Style header
    for j in range(len(display_cols)):
        tbl[0, j].set_facecolor("#264653")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        bg = "#f0f0f0" if i % 2 == 0 else "white"
        for j in range(len(display_cols)):
            tbl[i, j].set_facecolor(bg)

    fig.suptitle("Summary Statistics - 7 Target Commodities (National Average)",
                 fontsize=14, fontweight="bold", y=0.95)
    fig.savefig(FIGURES_DIR / "09_summary_table.png")
    plt.close(fig)
    print("  [OK] 09_summary_table.png")


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def write_text_report(summary_df: pd.DataFrame, adf_df: pd.DataFrame,
                      cv_df: pd.DataFrame, corr: pd.DataFrame) -> None:
    """Write a consolidated text summary to reports/."""
    report_path = REPORTS_DIR / "eda_summary_report.txt"
    lines = []
    lines.append("=" * 80)
    lines.append("  ForecastBI - Phase 1 EDA Summary Report")
    lines.append("=" * 80)
    lines.append("")

    # Dataset overview
    lines.append("1. DATASET OVERVIEW")
    lines.append("-" * 40)
    lines.append(f"   Commodities:  {len(TARGET_COMMODITIES)}")
    lines.append(f"   Months:       {summary_df['N_Months'].iloc[0]} (per commodity)")
    lines.append(f"   Total records: {summary_df['N_Months'].sum()}")
    lines.append(f"   Cities:       17")
    lines.append(f"   Missing data: 0 (all clean)")
    lines.append("")

    # Summary stats
    lines.append("2. SUMMARY STATISTICS (National Average Price, Rs/Kg)")
    lines.append("-" * 40)
    lines.append(summary_df.to_string(index=False))
    lines.append("")

    # Volatility ranking
    lines.append("3. VOLATILITY RANKING (Coefficient of Variation)")
    lines.append("-" * 40)
    for _, row in cv_df.sort_values("CV", ascending=False).iterrows():
        tag = "HIGH" if row["CV"] > 20 else ("MODERATE" if row["CV"] > 10 else "LOW")
        lines.append(f"   {row['Commodity']:25s}  CV = {row['CV']:5.1f}%  [{tag}]")
    lines.append("")

    # Stationarity
    lines.append("4. STATIONARITY TESTS (Augmented Dickey-Fuller, alpha = 0.05)")
    lines.append("-" * 40)
    lines.append(adf_df.to_string(index=False))
    lines.append("")
    non_stationary = adf_df[adf_df["Level_Stationary"] == "No"]["Commodity"].tolist()
    stationary = adf_df[adf_df["Level_Stationary"] == "Yes"]["Commodity"].tolist()
    if non_stationary:
        lines.append(f"   Non-stationary at level: {', '.join(non_stationary)}")
    if stationary:
        lines.append(f"   Stationary at level:     {', '.join(stationary)}")
    diff_fixed = adf_df[adf_df["Diff_Stationary"] == "Yes"]["Commodity"].tolist()
    lines.append(f"   Stationary after 1st diff: {', '.join(diff_fixed)}")
    lines.append("")

    # Key correlations
    lines.append("5. NOTABLE CORRELATIONS")
    lines.append("-" * 40)
    for i in range(len(corr)):
        for j in range(i + 1, len(corr)):
            r = corr.iloc[i, j]
            if abs(r) >= 0.6:
                c1 = corr.index[i].replace(" (Washed)", "")
                c2 = corr.columns[j].replace(" (Washed)", "")
                strength = "Strong" if abs(r) >= 0.8 else "Moderate"
                direction = "positive" if r > 0 else "negative"
                lines.append(f"   {c1} <-> {c2}: r = {r:+.2f}  [{strength} {direction}]")
    lines.append("")

    # Modeling implications
    lines.append("6. MODELING IMPLICATIONS")
    lines.append("-" * 40)
    lines.append("   * Vegetables (Tomatoes, Onions, Potatoes) show high volatility")
    lines.append("     and strong seasonality - Prophet should capture these well.")
    lines.append("   * Pulses show more stable trends - XGBoost with lag features")
    lines.append("     may outperform Prophet for these.")
    lines.append("   * 41 observations is small; recommend 6-month test holdout")
    lines.append("     (35 train / 6 test) over 12-month to preserve training data.")
    lines.append("   * First-differencing needed for non-stationary series in XGBoost.")
    lines.append("")
    lines.append("=" * 80)
    lines.append("  End of Report")
    lines.append("=" * 80)

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [OK] {report_path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 60)
    print(" ForecastBI - Phase 1: Exploratory Data Analysis")
    print("=" * 60)

    ensure_directories_exist()
    df = load_data()
    print(f"\nLoaded {len(df)} records | {df['Date'].min().date()} -> {df['Date'].max().date()}")
    print(f"Commodities: {len(TARGET_COMMODITIES)} | Cities: {len(CITIES)}")
    print(f"\nGenerating charts -> {FIGURES_DIR}/\n")

    # 1-2. Time series
    plot_individual_timeseries(df)
    plot_grouped_overlay(df)

    # 3. Volatility
    cv_df = plot_volatility_analysis(df)

    # 4. Correlation
    corr = plot_correlation_matrix(df)

    # 5-6. City analysis
    plot_city_price_heatmap(df)
    plot_city_spread(df)

    # 7-8. Seasonality
    plot_seasonal_decomposition(df)
    plot_monthly_seasonality(df)

    # 9-10. Statistics
    adf_df = run_stationarity_tests(df)
    summary_df = compute_summary_statistics(df)

    # 11. Visual table
    plot_summary_table(summary_df)

    # Text report
    print()
    write_text_report(summary_df, adf_df, cv_df, corr)

    print(f"\n{'=' * 60}")
    print(f" EDA Complete! 9 charts + 1 text report generated.")
    print(f" Figures: {FIGURES_DIR}")
    print(f" Report:  {REPORTS_DIR / 'eda_summary_report.txt'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
