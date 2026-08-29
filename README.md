# 🇵🇰 ForecastBI - Commodity Price Forecasting & Power BI Analytics

An end-to-end Machine Learning and Business Intelligence project for forecasting retail and wholesale prices of 7 essential food commodities in Pakistan using Pakistan Bureau of Statistics (PBS) data.

---

## 🎯 Target Commodities
1. **Tomatoes**
2. **Onions**
3. **Potatoes**
4. **Pulse Moong (Washed)**
5. **Pulse Gram**
6. **Pulse Masoor (Washed)**
7. **Pulse Mash (Washed)**

---

## 🏗️ Project Architecture & Workflow
```
PBS SPI/CPI Data (5 Years)
       │
       ▼
Data Cleaning & Monthly Aggregation (`src/data_cleaning.py`)
       │
       ▼
Feature Engineering (Lags, Rolling Stats, Seasonality) (`src/feature_engineering.py`)
       │
       ├──► Facebook Prophet Forecasting (`src/prophet_model.py`)
       └──► XGBoost Multi-step Regression (`src/xgboost_model.py`)
       │
       ▼
Model Evaluation & Benchmark (MAPE / RMSE) (`src/evaluate.py`)
       │
       ▼
Power BI Interactive Dashboard (`reports/ForecastBI.pbix`)
```

---

## 📁 Repository Structure
```
ForecastBI/
├── README.md                           # Project documentation
├── requirements.txt                    # Dependencies
├── .gitignore                          # Git configuration
│
├── data/
│   ├── raw/                            # Raw PBS downloads (Excel / CSV)
│   ├── processed/                      # Cleaned time-series data
│   │   ├── master_all_commodities_monthly_prices.csv
│   │   └── target_commodities_monthly_prices.csv
│   └── output/                         # Power BI ready CSV files
│       ├── historical_commodity_prices.csv
│       ├── forecasts_next_year.csv
│       ├── model_accuracy.csv
│       └── monthly_summary.csv
│
├── notebooks/
│   ├── 01_data_collection.ipynb        # Data ingestion & cleaning walkthrough
│   ├── 02_eda.ipynb                    # Exploratory Data Analysis & visual insights
│   └── 03_modeling.ipynb               # ML training, evaluation & prediction
│
├── src/
│   ├── __init__.py
│   ├── utils.py                        # Constants, paths & helpers
│   ├── data_cleaning.py                # Preprocessing functions
│   ├── feature_engineering.py          # Lag & rolling feature generators
│   ├── prophet_model.py                # Prophet forecaster
│   ├── xgboost_model.py                # XGBoost regressor
│   ├── evaluate.py                     # Performance metric calculations
│   └── main.py                         # Master execution script
│
├── reports/
│   ├── figures/                        # Generated EDA & model plots
│   └── PowerBI_Setup_Guide.md          # Visual dashboard documentation
│
└── models/                             # Serialized model artifacts
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Master Pipeline
```bash
python -m src.main
```

### 3. Open in Power BI
Open Power BI Desktop and load the generated files from `data/output/` following [`PowerBI_Setup_Guide.md`](reports/PowerBI_Setup_Guide.md).
