# Hyperliquid Trader Performance & Bitcoin Sentiment Analysis

This repository contains a self-contained quantitative research pipeline and backtesting suite. It explores the empirical relationship between **Bitcoin market sentiment** (measured by the Crypto Fear & Greed Index) and **high-frequency trader execution data** on the **Hyperliquid decentralized exchange**. 

The dataset analyzed contains **211,224 executions** across **32 unique wallets** over a **2-year overlapping period (May 2023 – May 2025)**.

---

## 📊 Core Quantitative Findings

1. **Volume Surges in Fear (Statistically Significant)**: There is a **statistically significant negative Pearson correlation** ($r = -0.2644$, $p = 4.2 \times 10^{-9}$) between daily FGI values and daily trading volume. This mathematically proves that market panic (low FGI) drives higher trading activity and larger trade sizes on Hyperliquid.
2. **Net Profitability and Sentiment Regimes (ANOVA)**: A one-way Analysis of Variance (ANOVA) validates that daily trader Net PnL averages differ significantly across sentiment categories:
   - **F-statistic**: 2.6690
   - **p-value**: 0.0317 ($p < 0.05$)
   - *Takeaway*: Sentiment regimes have a statistically valid impact on trader PnL, justifying their integration into execution models.
3. **The Retail "Dumb Money" Signature**: Under **Extreme Fear**, retail/losing accounts buy only **16.59%** of the time (panic selling the bottom). Under **Greed**, their Buy Ratio climbs to **73.96%** (FOMO buying the top). This results in heavy realized losses during market extensions.
4. **The Whale Pro "Smart Money" Signature**: Whale Elite Pros maintain a balanced accumulation posture under **Extreme Fear** (Buy Ratio **52.74%**) and actively distribute/short during **Extreme Greed** (Buy Ratio drops to **40.74%**, taking profit into retail buy walls).
5. **The Shorting Trap & Drawdown Mitigation**: In a multi-year secular bull market (BTC returned +126.71% during the study period), aggressive Long/Short sentiment-following strategies suffer due to shorting market extension. However, a risk-mitigated **Long-Only Contrarian Sentiment** strategy delivers positive returns (+12.72%) and slashes maximum drawdown from **-28.34%** (BTC benchmark) down to **-19.96%**.

---

## 📂 Repository Structure

* **`data_pipeline.py`**: Loads the source files, standardizes calendar dates (matching IST and UTC), incorporates transaction fees, and merges the datasets into `cleaned_merged_data.csv`.
* **`eda_analysis.py`**: Computes trading counts, volumes, win rates, and PnLs grouped by FGI class. Performs ANOVA and correlation tests, and saves visualization charts to `plots/`.
* **`trader_profiles.py`**: Classifies wallets into behavioral cohorts ("Elite Pro", "Pro", "Retail / Losing", "Whale") based on cumulative PnL/volume, and analyzes cohort buy-ratios across sentiment regimes.
* **`strategy_backtest.py`**: Runs daily simulations of Contrarian FGI, copying Whale Pros, and fading retail order flows across both Long/Short and Long/Cash (Long-Only) regimes (signals are shifted by 1 day to prevent look-ahead bias).
* **`generate_report.py`**: Compiles data tables and statistical summaries into the markdown report `report.md`.
* **`generate_pdf.py`**: Generates a highly formatted, professionally styled 9-page research report `Primetrade_Quant_Research_Report.pdf` with embedded charts and custom navy/teal branding.
* **`run_all.py`**: The master orchestration script that executes the entire pipeline end-to-end sequentially.
* **`plots/`**: Folder containing all generated visualization charts and metrics tables.

---

## ⚙️ How to Run the Pipeline

### 1. Prerequisites
Ensure you have Python 3.8+ installed along with the required scientific libraries:
```bash
pip install pandas numpy matplotlib scipy fpdf2
```

### 2. Run the Pipeline
To clean the data, generate statistical tables, run backtests, and compile both Markdown and PDF reports, run the master orchestrator script:
```bash
python run_all.py
```

### 3. View the Reports
* **Interactive/Visual PDF**: Open `Primetrade_Quant_Research_Report.pdf` in any web browser or PDF viewer.
* **Markdown Summary**: Read `report.md` directly inside your editor or GitHub page.

---

## 📈 Strategy Backtest Performance (2023–2025)

| Strategy | Total Return (%) | Annualized Return (%) | Annualized Volatility (%) | Sharpe Ratio | Max Drawdown (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **BTC Buy & Hold (Benchmark)** | **126.72%** | **78.83%** | **45.88%** | **1.7180** | **-28.34%** |
| Contrarian Sentiment (L/S) | -51.62% | -40.29% | 35.43% | -1.1373 | -61.67% |
| **Contrarian Sentiment (Long-Only)** | **12.72%** | **8.88%** | **29.52%** | **0.3007** | **-19.96%** |
| Copy Smart Money (L/S) | -72.77% | -60.30% | 42.41% | -1.4218 | -73.77% |
| Copy Smart Money (Long-Only) | -11.56% | -8.36% | 33.40% | -0.2501 | -32.60% |
| Fade Dumb Money (L/S) | -6.54% | -4.69% | 22.63% | -0.2073 | -31.27% |
| Fade Dumb Money (Long-Only) | -14.31% | -10.39% | 19.56% | -0.5312 | -32.14% |
