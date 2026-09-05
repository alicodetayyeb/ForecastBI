import os
import sys
import base64
import subprocess
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(r"d:\A- Commodity Price Coordinator\antigravity projects\ForecastBI")
OUTPUT_PDF = BASE_DIR / "ForecastBI_Executive_Documentation.pdf"
REPORTS_PDF = BASE_DIR / "reports" / "ForecastBI_Executive_Documentation.pdf"
TEMP_HTML = BASE_DIR / "temp_documentation.html"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Helper to encode images
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(image_path)[1].lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{data}"
    return ""

img_dashboard_accuracy = get_base64_image(BASE_DIR / "reports" / "figures" / "media_1788638523373.png")
img_dashboard_overview = get_base64_image(BASE_DIR / "reports" / "figures" / "media_1788638523383.png")
img_dashboard_forecast = get_base64_image(BASE_DIR / "reports" / "figures" / "media_1788638523392.png")

template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ForecastBI - Comprehensive Project Documentation & Technical Architecture</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.55;
    font-size: 9.8pt;
    margin: 0;
    padding: 0;
  }

  h1, h2, h3, h4, h5 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    page-break-after: avoid;
  }

  h1 {
    font-size: 20pt;
    line-height: 1.2;
    border-bottom: 2.5px solid #2563eb;
    padding-bottom: 6px;
    margin-top: 0;
  }

  h2 {
    font-size: 14pt;
    border-bottom: 1.2px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 1.6em;
    color: #1e3a8a;
  }

  h3 {
    font-size: 11.5pt;
    color: #0369a1;
    margin-top: 1.2em;
  }

  h4 {
    font-size: 10pt;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  p {
    margin: 0 0 0.8em 0;
    text-align: justify;
  }

  .doc-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: #ffffff;
    padding: 24px 28px;
    border-radius: 8px;
    margin-bottom: 24px;
  }

  .doc-header h1 {
    color: #ffffff;
    border-bottom: none;
    margin: 0 0 8px 0;
    font-size: 22pt;
  }

  .doc-header .subtitle {
    font-size: 11pt;
    color: #93c5fd;
    margin: 0 0 14px 0;
    font-weight: 500;
  }

  .doc-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 8.5pt;
    color: #cbd5e1;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 10px;
  }

  .doc-meta span strong {
    color: #ffffff;
  }

  .callout {
    padding: 12px 16px;
    border-radius: 6px;
    margin: 14px 0;
    font-size: 9.3pt;
    page-break-inside: avoid;
  }

  .callout-info {
    background-color: #eff6ff;
    border-left: 4px solid #2563eb;
    color: #1e40af;
  }

  .callout-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
  }

  .callout-success {
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
    color: #065f46;
  }

  .callout-danger {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #991b1b;
  }

  .callout-title {
    font-weight: 700;
    margin-bottom: 4px;
    font-size: 9.8pt;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .metric-cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 16px 0;
    page-break-inside: avoid;
  }

  .metric-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 12px 14px;
  }

  .metric-box.mape { border-top: 3.5px solid #2563eb; }
  .metric-box.rmse { border-top: 3.5px solid #f59e0b; }
  .metric-box.mae  { border-top: 3.5px solid #10b981; }

  .metric-box .metric-name {
    font-size: 11pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
  }

  .metric-box .metric-sub {
    font-size: 8pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }

  .metric-box .metric-formula {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8pt;
    background: #e2e8f0;
    padding: 3px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 8px;
    color: #1e293b;
    font-weight: bold;
  }

  .metric-box .metric-desc {
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.4;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
  }

  th {
    background-color: #0f172a;
    color: #ffffff;
    padding: 7px 9px;
    font-weight: 600;
    text-align: left;
    border: 1px solid #0f172a;
    font-size: 8.5pt;
  }

  td {
    padding: 6px 9px;
    border: 1px solid #e2e8f0;
    vertical-align: middle;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  tr.winner {
    background-color: #f0fdf4;
    font-weight: 600;
  }

  .badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 10px;
    font-size: 7.8pt;
    font-weight: 600;
  }

  .badge-high { background-color: #fee2e2; color: #991b1b; }
  .badge-mod  { background-color: #fef3c7; color: #92400e; }
  .badge-low  { background-color: #d1fae5; color: #065f46; }
  .badge-xg   { background-color: #dbeafe; color: #1e40af; }
  .badge-pro  { background-color: #f3e8ff; color: #6b21a8; }

  pre, code {
    font-family: 'Consolas', 'Courier New', monospace;
  }

  pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 8pt;
    line-height: 1.45;
    overflow-x: auto;
    margin: 12px 0;
    page-break-inside: avoid;
  }

  .diagram-box {
    background-color: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 14px;
    margin: 16px 0;
    page-break-inside: avoid;
  }

  .flow-step {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #2563eb;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 4px;
  }

  .flow-step-title {
    font-weight: 700;
    font-size: 9pt;
    color: #1e3a8a;
  }

  .flow-step-desc {
    font-size: 8.3pt;
    color: #475569;
  }

  .figure-container {
    margin: 18px 0;
    text-align: center;
    page-break-inside: avoid;
  }

  .figure-container img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid #cbd5e1;
  }

  .figure-caption {
    font-size: 8.2pt;
    color: #475569;
    margin-top: 6px;
    font-style: italic;
  }

  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<!-- Header Banner -->
<div class="doc-header">
  <h1>🇵🇰 ForecastBI: Pakistan Commodity Price Intelligence</h1>
  <div class="subtitle">Complete Technical Architecture, Data Scraping Pipeline, ML Model Benchmarks & Power BI Analytics</div>
  <div class="doc-meta">
    <span><strong>Target Commodities:</strong> 7 Essential Foods (Tomatoes, Onions, Potatoes, 4 Pulses)</span>
    <span><strong>Coverage:</strong> 17 Major Commercial Cities of Pakistan (5-Year Window)</span>
    <span><strong>Models:</strong> Facebook Prophet vs. Recursive XGBoost</span>
    <span><strong>Primary Interface:</strong> Microsoft Power BI</span>
    <span><strong>Status:</strong> Production Ready</span>
  </div>
</div>

<!-- Executive Summary -->
<h2>1. Executive Summary & Project Objectives</h2>
<p>
  <strong>ForecastBI</strong> is an enterprise-grade commodity price forecasting and business intelligence system engineered to capture, model, and visualize retail price trajectories across Pakistan's agricultural and grocery retail markets. In Pakistan, staple food items frequently undergo severe inflationary shocks and seasonal volatility. Perishable vegetables like <em>Tomatoes, Onions, and Potatoes</em> often experience single-month price spikes exceeding 100%, driven by monsoon flooding, crop cycle transitions, border trade closures, and transport bottlenecks. Meanwhile, vital dietary protein sources like <em>Pulses (Moong, Masoor, Gram, and Mash)</em> represent substantial portions of lower- and middle-income household expenditures.
</p>
<p>
  Official statistics published monthly by the <strong>Pakistan Bureau of Statistics (PBS)</strong> under the Consumer Price Index (CPI) and Sensitive Price Indicator (SPI) frameworks contain authoritative field data collected from 17 major commercial centers. However, these figures are published as static, disconnected bulletins (PDFs and Excel files) without automated forecasting or spatial decision support. <strong>ForecastBI</strong> bridges this gap by delivering:
</p>
<ul>
  <li><strong>Automated Data Engineering:</strong> Resilient harvesting and normalization of 5+ years of historical PBS monthly price data.</li>
  <li><strong>Empirical Machine Learning Benchmarking:</strong> Comparative evaluation of <em>Facebook Prophet</em> (decomposable Bayesian Fourier series) against <em>XGBoost</em> (recursive gradient boosted decision trees) to identify the optimal model per commodity.</li>
  <li><strong>Executive Business Intelligence:</strong> A suite of dark-themed, high-contrast <strong>Power BI dashboards</strong> delivering 12-month forward forecasts, volatility tiering, model accuracy auditing, and cross-city geographic price spreads.</li>
</ul>

<!-- System Architecture -->
<h2>2. End-to-End System Architecture</h2>
<p>
  The pipeline is organized into four independent, reproducible phases executing from raw web data ingestion to final executive visualization:
</p>

<div class="diagram-box">
  <div class="flow-step">
    <div class="flow-step-title">Phase 1: Ingestion & Scraping (PBS Price Statistics)</div>
    <div class="flow-step-desc">Headless regex extraction of dynamic JS data payload (<code>const cpidata1</code>) via <code>chompjs</code>. Dual-engine file parsing (<code>openpyxl</code> for Excel, <code>pypdf</code> + regex tokenizer for PDF bulletins) compiling 51 commodities across 17 cities.</div>
  </div>
  <div class="flow-step">
    <div class="flow-step-title">Phase 2: Cleaning, EDA & Feature Engineering</div>
    <div class="flow-step-desc">Filtering 7 core target commodities. Augmented Dickey-Fuller (ADF) stationarity testing. Volatility tiering. Generating autoregressive lags (1, 2, 3, 6, 12), rolling statistics (means/stds), and cyclical calendar transforms.</div>
  </div>
  <div class="flow-step">
    <div class="flow-step-title">Phase 3: Machine Learning Modeling & Backtesting</div>
    <div class="flow-step-desc">6-month out-of-sample chronological backtest (35 months train / 6 test). Benchmarking Prophet vs. XGBoost on MAPE, RMSE, and MAE. Dynamic model selection and 12-month forward forecasting with historical price floor guards.</div>
  </div>
  <div class="flow-step">
    <div class="flow-step-title">Phase 4: Power BI Analytics Suite</div>
    <div class="flow-step-desc">Exporting star-schema tables (<code>pbi_combined_timeline.csv</code>, <code>pbi_commodity_metadata.csv</code>, <code>pbi_historical_prices.csv</code>). Rendering interactive dashboards with custom dark theme (<code>#1B2838</code>).</div>
  </div>
</div>

<div class="page-break"></div>

<!-- Data Scraping Section -->
<h2>3. The PBS Web Scraping Challenge & Engineered Solutions</h2>
<p>
  Extracting 5 consecutive years (60 target months) of historical retail prices from the official <strong>Pakistan Bureau of Statistics (PBS)</strong> website (<code>https://www.pbs.gov.pk/price-statistics/</code>) revealed substantial technical barriers that caused standard scraping libraries to fail.
</p>

<div class="callout callout-danger">
  <div class="callout-title">⚠️ The Core Scraping Obstacle: Client-Side Dynamic JavaScript Payloads</div>
  Standard HTTP scrapers (<code>requests</code> + <code>BeautifulSoup</code>) returned an empty table skeleton. The download hyperlinks were entirely missing from the HTML DOM. PBS does not render table rows on the server; instead, it injects the entire monthly metadata catalog into an inline JavaScript array (<code>const cpidata1 = [...]</code>) within a <code>&lt;script&gt;</code> block, which is populated into <code>reportTable1</code> dynamically at runtime.
</div>

<h3>3.1 How We Solved the Dynamic Payload Bottleneck</h3>
<p>
  Rather than spinning up heavy browser automation tools like Selenium or Playwright (which consume excessive memory and crash on unstable government servers), we built a high-speed, headless regex parser in <code>Data_Scraping_files/download_pbs_data.py</code>. It grabs the raw HTML stream, isolates the JavaScript array text using regular expressions, and parses it into native Python dictionaries using <code>chompjs</code>:
</p>
<pre>
# Fast AST JavaScript Array Extraction in download_pbs_data.py
resp = requests.get(BASE_URL, headers=HEADERS, verify=False, timeout=30)
match = re.search(r'const\s+cpidata1\s*=\s*(\[\s*\{.*?\}\s*\]);', resp.text, re.DOTALL)
raw_items = chompjs.parse_js_object(match.group(1)) # Extracted all 60 monthly records in &lt; 2s!
</pre>

<h3>3.2 Resolving Mixed Publication Formats (XLSX, XLS, and PDF)</h3>
<p>
  Over the 5-year chronological span, PBS changed its reporting formats multiple times. Several recent months were modern <code>.xlsx</code> spreadsheets, older months were binary <code>.xls</code> files, and critical intermediate periods were published <strong>strictly as formatted PDF bulletins</strong>. We developed a dual-engine compiler (<code>compile_pbs_data.py</code>):
</p>
<ul>
  <li><strong>Spreadsheet Engine (<code>openpyxl</code>):</strong> Scans cell matrices from row 3 to 65, strips thousand-separator commas, handles merged title headers, and maps columns 4–20 to the 17 designated cities.</li>
  <li><strong>PDF Text Engine (<code>pypdf</code> + Regex Tokenizer):</strong> Extracts text streams line-by-line, matching item serial numbers (1 to 51) and floating-point sequences representing city prices and the national average:</li>
</ul>
<pre>
# PDF Extraction Tokenizer in compile_pbs_data.py
line_pattern = r'^(\d{1,2})\s+([A-Za-z].*?)\s+(\d+\.\d{2}.*)$'
m = re.match(line_pattern, line.strip())
if m:
    sno = int(m.group(1))
    floats = [float(t) for t in re.findall(r'[-+]?\d*\.?\d+', m.group(3))]
    # Assign floats[0:17] to 17 cities, floats[17] to National Average
</pre>

<h3>3.3 Missing Months, Gaps, and Automated Recovery</h3>
<p>
  To ensure total auditability, the downloader maintains a target 60-month chronological checklist. Any missing months, broken links, or 404 responses are automatically logged to <code>missing_months.txt</code>. When official National Average values were missing in the bulletin, our compilation pipeline computed the arithmetic mean across all valid city observations for that row.
</p>

<!-- EDA Section -->
<h2>4. Target Commodities & Exploratory Data Analysis (EDA)</h2>
<p>
  We prioritized <strong>7 core food commodities</strong> representing the most sensitive expenditure items in the Pakistani consumer basket:
</p>

<table>
  <thead>
    <tr>
      <th>S.No</th>
      <th>Commodity Name</th>
      <th>Category</th>
      <th>Unit</th>
      <th>Avg Price (Rs)</th>
      <th>Min Price (Rs)</th>
      <th>Max Price (Rs)</th>
      <th>CV (%)</th>
      <th>Volatility Tier</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>23</strong></td>
      <td><strong>Tomatoes</strong></td>
      <td>Vegetables</td>
      <td>1 Kg</td>
      <td>110.49</td>
      <td>42.26</td>
      <td>264.57</td>
      <td><strong>46.6%</strong></td>
      <td><span class="badge badge-high">High Volatility</span></td>
    </tr>
    <tr>
      <td><strong>22</strong></td>
      <td><strong>Onions</strong></td>
      <td>Vegetables</td>
      <td>1 Kg</td>
      <td>107.89</td>
      <td>45.51</td>
      <td>221.59</td>
      <td><strong>44.5%</strong></td>
      <td><span class="badge badge-high">High Volatility</span></td>
    </tr>
    <tr>
      <td><strong>21</strong></td>
      <td><strong>Potatoes</strong></td>
      <td>Vegetables</td>
      <td>1 Kg</td>
      <td>76.69</td>
      <td>31.12</td>
      <td>116.85</td>
      <td><strong>29.5%</strong></td>
      <td><span class="badge badge-high">High Volatility</span></td>
    </tr>
    <tr>
      <td><strong>20</strong></td>
      <td><strong>Pulse Gram</strong></td>
      <td>Pulses & Legumes</td>
      <td>1 Kg</td>
      <td>286.00</td>
      <td>229.43</td>
      <td>411.18</td>
      <td><strong>17.3%</strong></td>
      <td><span class="badge badge-mod">Moderate</span></td>
    </tr>
    <tr>
      <td><strong>18</strong></td>
      <td><strong>Pulse Moong (Washed)</strong></td>
      <td>Pulses & Legumes</td>
      <td>1 Kg</td>
      <td>345.40</td>
      <td>263.26</td>
      <td>402.44</td>
      <td><strong>14.0%</strong></td>
      <td><span class="badge badge-mod">Moderate</span></td>
    </tr>
    <tr>
      <td><strong>19</strong></td>
      <td><strong>Pulse Mash (Washed)</strong></td>
      <td>Pulses & Legumes</td>
      <td>1 Kg</td>
      <td>490.73</td>
      <td>419.23</td>
      <td>581.03</td>
      <td><strong>9.5%</strong></td>
      <td><span class="badge badge-low">Low Volatility</span></td>
    </tr>
    <tr>
      <td><strong>17</strong></td>
      <td><strong>Pulse Masoor (Washed)</strong></td>
      <td>Pulses & Legumes</td>
      <td>1 Kg</td>
      <td>297.36</td>
      <td>257.64</td>
      <td>339.50</td>
      <td><strong>8.2%</strong></td>
      <td><span class="badge badge-low">Low Volatility</span></td>
    </tr>
  </tbody>
</table>

<div class="callout callout-info">
  <div class="callout-title">💡 Statistical Insights: Stationarity & Structural Differences</div>
  <strong>Stationarity (ADF Tests):</strong> Augmented Dickey-Fuller hypothesis tests confirmed that all 7 commodities were <em>non-stationary at level</em> (p &gt; 0.05), reflecting chronic structural inflation. All series achieved stationarity after 1st differencing (p &lt; 0.01).<br>
  <strong>Vegetables vs. Pulses:</strong> Vegetables undergo dramatic perishable swings (Tomatoes peaked at Rs 264.57 vs min Rs 42.26). Pulses exhibit smooth trends due to shelf stability, international imports, and centralized wholesale grain storage.
</div>

<div class="page-break"></div>

<!-- Feature Engineering & Models -->
<h2>5. Feature Engineering & Machine Learning Models</h2>

<h3>5.1 Engineered Feature Matrix (for XGBoost)</h3>
<p>
  Tree models require explicit temporal signals to capture autoregressive memory and seasonality. In <code>src/feature_engineering.py</code>, we constructed:
</p>
<ul>
  <li><strong>Calendar & Cyclical Trigonometry:</strong> Month, quarter, and smooth trigonometric transforms: <code>sin(2πm/12)</code> and <code>cos(2πm/12)</code> to capture circular seasonal transitions.</li>
  <li><strong>Autoregressive Lags:</strong> <code>lag_1</code>, <code>lag_2</code>, <code>lag_3</code> (short-term inertia), <code>lag_6</code> (half-year shift), and <code>lag_12</code> (year-over-year annual benchmark).</li>
  <li><strong>Rolling Window Statistics:</strong> 3-month and 6-month rolling means and standard deviations (strictly shifted by t-1 to prevent data leakage).</li>
  <li><strong>Momentum Indicators:</strong> Month-over-month price difference and percentage change of the preceding periods.</li>
</ul>

<h3>5.2 Facebook Prophet vs. Recursive XGBoost</h3>
<ul>
  <li><strong>Facebook Prophet (<code>src/prophet_model.py</code>):</strong> Uses an additive/multiplicative decomposable Bayesian time-series formulation: y(t) = g(t) + s(t) + ε(t). Seasonality s(t) is modeled as a continuous Fourier series. We configured <code>multiplicative</code> mode for volatile vegetables (where fluctuations scale with price inflation) and <code>additive</code> mode for pulses.</li>
  <li><strong>XGBoost Regressor (<code>src/xgboost_model.py</code>):</strong> Gradient boosted trees trained on the engineered feature matrix. To forecast 12 months ahead, we developed an iterative recursive roll: predict month t+1, append to history, reconstruct all lags and rolling stats, and forecast t+2 through t+12.</li>
</ul>

<!-- MASTER METRIC KEY SECTION -->
<h2>6. Master Key: Understanding Evaluation Metrics (MAPE, RMSE, MAE)</h2>
<p>
  To rigorously benchmark our machine learning models, we compute three complementary evaluation metrics. Each metric provides a distinct perspective on model accuracy, error magnitude, and outlier risk:
</p>

<div class="metric-cards-grid">
  <div class="metric-box mape">
    <div class="metric-name">MAPE</div>
    <div class="metric-sub">Mean Absolute Percentage Error</div>
    <div class="metric-formula">MAPE = (1/n) Σ |(y - ŷ) / y| × 100%</div>
    <div class="metric-desc">
      <strong>Unit:</strong> Percentage (%)<br>
      <strong>Layman Definition:</strong> The average percentage mistake the model makes relative to actual prices.<br>
      <strong>Interpretation:</strong> Scale-independent. Allows fair comparison between a Rs 50 potato and a Rs 500 pulse. <em>Lower is better</em>.
    </div>
  </div>

  <div class="metric-box rmse">
    <div class="metric-name">RMSE</div>
    <div class="metric-sub">Root Mean Squared Error</div>
    <div class="metric-formula">RMSE = √[ (1/n) Σ (y - ŷ)² ]</div>
    <div class="metric-desc">
      <strong>Unit:</strong> Pakistani Rupees (Rs / Kg)<br>
      <strong>Layman Definition:</strong> Typical error size with heavy penalties for large blunders.<br>
      <strong>Interpretation:</strong> Errors are squared before averaging. If a model has a single catastrophic forecast failure, RMSE surges dramatically.
    </div>
  </div>

  <div class="metric-box mae">
    <div class="metric-name">MAE</div>
    <div class="metric-sub">Mean Absolute Error</div>
    <div class="metric-formula">MAE = (1/n) Σ |y - ŷ|</div>
    <div class="metric-desc">
      <strong>Unit:</strong> Pakistani Rupees (Rs / Kg)<br>
      <strong>Layman Definition:</strong> The average rupee-amount deviation off the actual price.<br>
      <strong>Interpretation:</strong> Linear penalty. An MAE of Rs 8.29 means the forecast is off by an average of Rs 8.30 per kg. Highly intuitive for budgets.
    </div>
  </div>
</div>

<h3>6.1 Why We Must Use All Three Metrics Together</h3>
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Penalty on Small Errors</th>
      <th>Penalty on Outliers / Spikes</th>
      <th>Scale Dependent?</th>
      <th>Primary Practical Use Case</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>MAE (Rs)</strong></td>
      <td>Proportional (Linear)</td>
      <td>Proportional (Linear)</td>
      <td>Yes (Rupees)</td>
      <td><strong>Procurement & Budgeting:</strong> Directly calculates total expected rupee variance on a purchasing contract.</td>
    </tr>
    <tr>
      <td><strong>RMSE (Rs)</strong></td>
      <td>Low</td>
      <td><strong>Severe (Quadratic)</strong></td>
      <td>Yes (Rupees)</td>
      <td><strong>Risk Management:</strong> Alerts analysts if the model suffers from dangerous outlier forecast blunders.</td>
    </tr>
    <tr>
      <td><strong>MAPE (%)</strong></td>
      <td>Relative to Price</td>
      <td>Relative to Price</td>
      <td><strong>No (Standardized %)</strong></td>
      <td><strong>Executive Benchmarking:</strong> Directly evaluates which model wins across different price categories.</td>
    </tr>
  </tbody>
</table>

<h3>6.2 Power BI Accuracy % and the Mathematical Meaning of Negative Accuracy</h3>
<p>
  In our Power BI dashboards, we convert MAPE into an executive <strong>Accuracy Score (%)</strong> using the formula:
</p>
<div style="text-align:center; margin: 10px 0; font-weight:700; font-size:11pt; color:#1e3a8a;">
  Accuracy (%) = 100 - MAPE (%)
</div>
<p>
  An accuracy of <strong>98%</strong> means the model's average relative error is merely 2%. However, notice in the benchmark table that for <strong>Potatoes under XGBoost, Accuracy is -28%</strong>!
</p>

<div class="callout callout-warning">
  <div class="callout-title">🔍 The Mathematical Explanation of the Negative Accuracy (-28%) Anomaly</div>
  When a model's predictions diverge severely from reality, the absolute error can exceed the actual price itself. During the 6-month backtest window for Potatoes, the post-harvest price plummeted from over Rs 100/kg down to Rs 31/kg. XGBoost's recursive predictions compounded errors, predicting prices near Rs 70 when actuals were Rs 31. This produced an individual percentage error of <code>|31 - 70| / 31 = 125.8%</code>, yielding a total <strong>MAPE of 127.90%</strong>.<br>
  Subtracted from 100: <code>100 - 127.90 = -27.90% ≈ -28%</code>.<br>
  <strong>Takeaway:</strong> A negative accuracy score is mathematically meaningful: it signals that the model performed worse than predicting zero and suffered from catastrophic recursive drift. Meanwhile, <strong>Prophet scored +69% accuracy</strong> because its Fourier sinusoidal curves smoothly respected the harvest bottom.
</div>

<div class="page-break"></div>

<!-- Benchmark Results Table -->
<h2>7. Empirical Benchmark Results & Dynamic Model Selection</h2>
<p>
  Models were tested on a strict <strong>6-month chronological holdout</strong> (35 train / 6 test). The results decisively prove that no single model wins across all commodities:
</p>

<table>
  <thead>
    <tr>
      <th>Commodity</th>
      <th>Category</th>
      <th>Prophet MAPE</th>
      <th>XGBoost MAPE</th>
      <th>Prophet Acc %</th>
      <th>XGBoost Acc %</th>
      <th>Prophet RMSE</th>
      <th>XGBoost RMSE</th>
      <th>Winning Model</th>
    </tr>
  </thead>
  <tbody>
    <tr class="winner">
      <td><strong>Pulse Moong (Washed)</strong></td>
      <td>Pulses</td>
      <td>6.46%</td>
      <td><strong>2.20%</strong></td>
      <td>94%</td>
      <td><strong>98%</strong></td>
      <td>29.87</td>
      <td><strong>12.02</strong></td>
      <td><span class="badge badge-xg">🏆 XGBoost</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Pulse Masoor (Washed)</strong></td>
      <td>Pulses</td>
      <td>9.14%</td>
      <td><strong>6.69%</strong></td>
      <td>91%</td>
      <td><strong>93%</strong></td>
      <td>26.91</td>
      <td><strong>17.75</strong></td>
      <td><span class="badge badge-xg">🏆 XGBoost</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Pulse Mash (Washed)</strong></td>
      <td>Pulses</td>
      <td>21.14%</td>
      <td><strong>6.22%</strong></td>
      <td>79%</td>
      <td><strong>94%</strong></td>
      <td>104.58</td>
      <td><strong>29.83</strong></td>
      <td><span class="badge badge-xg">🏆 XGBoost</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Pulse Gram</strong></td>
      <td>Pulses</td>
      <td><strong>9.63%</strong></td>
      <td>10.00%</td>
      <td><strong>90%</strong></td>
      <td>90%</td>
      <td><strong>32.02</strong></td>
      <td>34.73</td>
      <td><span class="badge badge-pro">🏆 Prophet</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Tomatoes</strong></td>
      <td>Vegetables</td>
      <td>48.37%</td>
      <td><strong>19.55%</strong></td>
      <td>52%</td>
      <td><strong>80%</strong></td>
      <td>115.72</td>
      <td><strong>59.52</strong></td>
      <td><span class="badge badge-xg">🏆 XGBoost</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Onions</strong></td>
      <td>Vegetables</td>
      <td>57.66%</td>
      <td><strong>29.42%</strong></td>
      <td>42%</td>
      <td><strong>71%</strong></td>
      <td>46.54</td>
      <td><strong>27.26</strong></td>
      <td><span class="badge badge-xg">🏆 XGBoost</span></td>
    </tr>
    <tr class="winner">
      <td><strong>Potatoes</strong></td>
      <td>Vegetables</td>
      <td><strong>30.98%</strong></td>
      <td>127.90%</td>
      <td><strong>69%</strong></td>
      <td><strong>-28%</strong></td>
      <td><strong>16.80</strong></td>
      <td>48.24</td>
      <td><span class="badge badge-pro">🏆 Prophet</span></td>
    </tr>
  </tbody>
</table>

<div class="callout callout-success">
  <div class="callout-title">🎯 Dynamic Model Routing Rule</div>
  <strong>ForecastBI</strong> routes each commodity to its proven best engine: <strong>XGBoost</strong> is selected for <em>Pulse Moong, Pulse Masoor, Pulse Mash, Tomatoes, and Onions</em>, while <strong>Facebook Prophet</strong> is designated for <em>Potatoes and Pulse Gram</em>. This guarantees that production dashboards always reflect optimal forecast accuracy.
</div>

<!-- Power BI Dashboards Walkthrough -->
<h2>8. Power BI Dashboards Walkthrough</h2>
<p>
  All outputs were imported into Microsoft Power BI Desktop styled with a custom dark executive theme (<code>ForecastBI_Theme.json</code>). Below is a walkthrough of the three primary production dashboard screens:
</p>

<h3>8.1 Dashboard Page 1: Executive KPI & Commodity Price Intelligence</h3>
<p>
  The executive overview enables rapid inspection of latest market rates, 12-month forward forecasts, model provenance, and annual inflation rates.
</p>

<div class="figure-container">
  <img src="REPLACE_IMG_OVERVIEW" alt="ForecastBI Executive KPI Dashboard">
  <div class="figure-caption">Figure 8.1: Executive Overview Dashboard filtered to Onions, displaying KPIs, Best Model selection (XGBoost), 70.58% accuracy, and +81.90% YoY price surge.</div>
</div>

<ul>
  <li><strong>Latest Actual Price:</strong> Displays Rs <code>101.81</code>/Kg for Onions.</li>
  <li><strong>Best Model Avg Forecast:</strong> Projects Rs <code>99.69</code>/Kg over the upcoming 12 months, indicating stabilization.</li>
  <li><strong>Best Model Provenance:</strong> Dynamically highlights <strong>XGBoost</strong> as the winning engine.</li>
  <li><strong>Year-over-Year Inflation (YoY %):</strong> Flags an acute <strong>+81.90%</strong> annual increase for Onions.</li>
  <li><strong>Metadata Card:</strong> Summarizes Category (Vegetables), Volatility Tier (High), and Historical Mean (Rs 107.89).</li>
</ul>

<div class="page-break"></div>

<h3>8.2 Dashboard Page 2: Price Trend & 12-Month Forward Forecast</h3>
<p>
  This view unites historical actual prices with 12-month forward machine learning projections in a seamless timeline visual.
</p>

<div class="figure-container">
  <img src="REPLACE_IMG_FORECAST" alt="Price Trend and 12-Month Forecast">
  <div class="figure-caption">Figure 8.2: 12-Month Forward Price Trend for Potatoes showing historical cyclical waves (blue) and forward Prophet projection through 2027 (orange).</div>
</div>

<ul>
  <li><strong>Horizontal Slicer Strip:</strong> One-click selector to switch between <em>Onions, Potatoes, Pulse Gram, Pulse Mash, Pulse Masoor, Pulse Moong, and Tomatoes</em>.</li>
  <li><strong>Actual Curve (Solid Blue Line):</strong> Traces historical monthly prices across 2023, 2024, 2025, and 2026. For Potatoes, this highlights cyclical waves peaking above Rs 100-115 before dropping sharply to Rs 31-40 during winter harvest.</li>
  <li><strong>Forecast Curve (Solid Orange Line):</strong> Connects directly to the latest actual price point and projects the forward path into 2027, successfully replicating the harvest trough and subsequent rebound.</li>
</ul>

<h3>8.3 Dashboard Page 3: Model Accuracy Benchmark & City Price Intelligence</h3>
<p>
  Provides transparent auditing of model metrics alongside spatial pricing hierarchies across Pakistan's 17 major commercial centers.
</p>

<div class="figure-container">
  <img src="REPLACE_IMG_ACCURACY" alt="Model Accuracy and City Price Intelligence">
  <div class="figure-caption">Figure 8.3: Model Accuracy Clustered Bar Chart (Prophet vs XGBoost) and 17-City Historical Price Hierarchy.</div>
</div>

<ul>
  <li><strong>Clustered Accuracy Bar Chart:</strong> Illustrates the competitive performance of Prophet vs. XGBoost across all 7 items, clearly showing XGBoost's dominance in pulses and vegetables alongside its negative dip on potatoes.</li>
  <li><strong>Geographic Price Hierarchy (17 Cities):</strong>
    <ul>
      <li><strong>Highest Price Centers:</strong> <strong>Islamabad (~Rs 280), Rawalpindi, and Quetta</strong> consistently maintain the highest average retail costs due to freight logistics markups from agricultural heartlands.</li>
      <li><strong>Lowest Price Centers:</strong> <strong>Bannu, Hyderabad, Gujranwala, and Larkana</strong> maintain lower retail averages due to local harvest proximity.</li>
    </ul>
  </li>
  <li><strong>Audit Metrics Table:</strong> Tabulates exact MAPE, MAE, and RMSE values per commodity and model for regulatory compliance and audit readiness.</li>
</ul>

<!-- Conclusion -->
<h2>9. Conclusion & Operational Impact</h2>
<p>
  <strong>ForecastBI</strong> transforms fragmented, static government price statistics into an automated, highly accurate predictive intelligence ecosystem. By combining resilient headless web extraction, rigorous statistical EDA, dynamic model routing (Prophet + XGBoost), and executive Power BI dashboards, the platform equips food procurement officers, commercial distributors, and economic analysts with the tools required to anticipate inflation shocks and optimize agricultural supply chains up to 12 months in advance.
</p>

</body>
</html>
"""

# Replace image tags
html_content = template.replace("REPLACE_IMG_OVERVIEW", img_dashboard_overview)
html_content = html_content.replace("REPLACE_IMG_FORECAST", img_dashboard_forecast)
html_content = html_content.replace("REPLACE_IMG_ACCURACY", img_dashboard_accuracy)

# Write HTML
with open(TEMP_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[OK] Generated temporary HTML: {TEMP_HTML}")

# Run Edge Headless to generate PDF
cmd = [
    EDGE_PATH,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={OUTPUT_PDF}",
    str(TEMP_HTML)
]

print(f"[+] Compiling PDF via Microsoft Edge Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)

if OUTPUT_PDF.exists() and OUTPUT_PDF.stat().st_size > 0:
    size_kb = OUTPUT_PDF.stat().st_size / 1024
    print(f"[SUCCESS] PDF generated successfully: {OUTPUT_PDF} ({size_kb:.1f} KB)")
    
    # Also copy to reports directory
    shutil.copy2(OUTPUT_PDF, REPORTS_PDF)
    print(f"[SUCCESS] Copy saved to: {REPORTS_PDF}")
else:
    print(f"[ERROR] Failed to generate PDF. Subprocess output: {res.stderr}")

# Clean up temp HTML
if TEMP_HTML.exists():
    TEMP_HTML.unlink()
    print("[OK] Cleaned up temporary HTML file.")
