# Power BI Dashboard Design & Connection Guide

This guide describes how to connect Power BI Desktop to the generated CSV files in `data/output/` and structure the 4 dashboard pages.

---

## 1. Data Connection Steps in Power BI
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Import the 4 CSV files from `data/output/`:
   - `historical_prices.csv`
   - `forecasts_next_year.csv`
   - `model_accuracy.csv`
   - `monthly_summary.csv`
4. In **Power Query Editor**, ensure:
   - `date` columns are formatted as **Date**.
   - Price columns are formatted as **Decimal Number**.
   - Commodity and category columns are formatted as **Text**.

---

## 2. Dashboard Pages Overview

### Page 1: Overview & KPI Dashboard
- **Cards**: Current average price, YoY % change, highest volatility commodity.
- **Slicers**: Commodity selector, category filter (Vegetables vs Pulses).
- **Line Chart**: 5-year historical price trend for all commodities.
- **Bar Chart**: Current price comparison across all 7 commodities.

### Page 2: 12-Month Price Forecast (Core Page)
- **Line & Area Combo Chart**:
  - Actual Historical Price (Solid line)
  - Forecast Price (Dashed line)
  - Lower & Upper Confidence Bands (Shaded area)
- **Date Slicer** / **Forecast Horizon Selector**.
- **Table**: Next 12 months forecasted price breakdown with upper and lower bound.

### Page 3: ML Model Accuracy & Benchmark
- **Grouped Bar Chart**: Prophet vs XGBoost MAPE (%) per commodity.
- **Card**: Best performing model indicator.
- **Metrics Table**: MAE, RMSE, MAPE, and R² scores.

### Page 4: Commodity Deep-Dive
- **Drill-through page** for individual commodity analysis.
- Seasonality patterns, monthly change heatmaps, and volatility metrics.
