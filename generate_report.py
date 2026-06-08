import os
import shutil
import pandas as pd

def df_to_markdown_simple(df):
    cols = df.columns.tolist()
    headers = " | ".join(str(c) for c in cols)
    separator = " | ".join("---" for _ in cols)
    rows = []
    for _, row in df.iterrows():
        rows.append(" | ".join(str(val) for val in row))
    return f"| {headers} |\n| {separator} |\n" + "\n".join(f"| {r} |" for r in rows)

def compile_report():
    print("=== STARTING REPORT GENERATION ===")
    
    workspace_dir = r"c:\Users\Saumya Ranga\OneDrive - UPES\Desktop\primetrade"
    artifact_dir = r"C:\Users\Saumya Ranga\.gemini\antigravity-ide\brain\615ea503-12fd-4a78-ac64-4483f1813617"
    
    # 1. Copy plots to the artifact directory
    src_plots_dir = os.path.join(workspace_dir, "plots")
    dest_plots_dir = os.path.join(artifact_dir, "plots")
    
    os.makedirs(dest_plots_dir, exist_ok=True)
    
    print("Copying plots to artifact directory...")
    plots_files = [
        "pnl_by_sentiment.png",
        "winrate_by_sentiment.png",
        "trade_activity_by_sentiment.png",
        "daily_pnl_vs_fgi.png",
        "account_pnl_distribution.png",
        "winrate_vs_sentiment_by_profile.png",
        "buy_ratio_vs_sentiment_by_profile.png",
        "strategy_performance.png"
    ]
    
    for filename in plots_files:
        src_file = os.path.join(src_plots_dir, filename)
        dest_file = os.path.join(dest_plots_dir, filename)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            print(f"  Copied {filename} to artifact directory.")
        else:
            print(f"  Warning: {filename} not found in workspace plots directory.")
            
    # Load statistical results for text compilation
    sentiment_stats_csv = os.path.join(src_plots_dir, "sentiment_stats.csv")
    anova_txt = os.path.join(src_plots_dir, "anova_result.txt")
    corr_csv = os.path.join(src_plots_dir, "daily_correlations.csv")
    perf_csv = os.path.join(src_plots_dir, "strategy_performance_metrics.csv")
    
    sentiment_stats_md = ""
    if os.path.exists(sentiment_stats_csv):
        df_stats = pd.read_csv(sentiment_stats_csv)
        # format numbers
        df_stats['total_volume_usd'] = df_stats['total_volume_usd'].map(lambda x: f"${x:,.2f}")
        df_stats['avg_size_usd'] = df_stats['avg_size_usd'].map(lambda x: f"${x:,.2f}")
        df_stats['total_closed_pnl'] = df_stats['total_closed_pnl'].map(lambda x: f"${x:,.2f}")
        df_stats['total_net_pnl'] = df_stats['total_net_pnl'].map(lambda x: f"${x:,.2f}")
        df_stats['avg_closed_pnl'] = df_stats['avg_closed_pnl'].map(lambda x: f"${x:,.4f}")
        df_stats['avg_net_pnl'] = df_stats['avg_net_pnl'].map(lambda x: f"${x:,.4f}")
        df_stats['total_fee'] = df_stats['total_fee'].map(lambda x: f"${x:,.2f}")
        df_stats['win_rate'] = df_stats['win_rate'].map(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        sentiment_stats_md = df_to_markdown_simple(df_stats)
        
    anova_result_str = ""
    if os.path.exists(anova_txt):
        with open(anova_txt, "r") as f:
            anova_result_str = f.read()
            
    corr_md = ""
    if os.path.exists(corr_csv):
        df_corr = pd.read_csv(corr_csv)
        df_corr = df_corr.rename(columns={'Unnamed: 0': 'Metric'})
        df_corr['pearson_r'] = df_corr['pearson_r'].map(lambda x: f"{x:.4f}")
        df_corr['pearson_p'] = df_corr['pearson_p'].map(lambda x: f"{x:.4e}")
        df_corr['spearman_r'] = df_corr['spearman_r'].map(lambda x: f"{x:.4f}")
        df_corr['spearman_p'] = df_corr['spearman_p'].map(lambda x: f"{x:.4e}")
        corr_md = df_to_markdown_simple(df_corr)
        
    perf_md = ""
    if os.path.exists(perf_csv):
        df_perf = pd.read_csv(perf_csv)
        df_perf['Total Return (%)'] = df_perf['Total Return (%)'].map(lambda x: f"{x:.2f}%")
        df_perf['Annualized Return (%)'] = df_perf['Annualized Return (%)'].map(lambda x: f"{x:.2f}%")
        df_perf['Annualized Volatility (%)'] = df_perf['Annualized Volatility (%)'].map(lambda x: f"{x:.2f}%")
        df_perf['Sharpe Ratio'] = df_perf['Sharpe Ratio'].map(lambda x: f"{x:.4f}")
        df_perf['Max Drawdown (%)'] = df_perf['Max Drawdown (%)'].map(lambda x: f"{x:.2f}%")
        perf_md = df_to_markdown_simple(df_perf)
        
    # Leaderboard details
    leaderboard_csv = os.path.join(src_plots_dir, "account_leaderboard.csv")
    leaderboard_md = ""
    if os.path.exists(leaderboard_csv):
        df_lead = pd.read_csv(leaderboard_csv)
        df_lead['total_volume_usd'] = df_lead['total_volume_usd'].map(lambda x: f"${x:,.2f}")
        df_lead['total_closed_pnl'] = df_lead['total_closed_pnl'].map(lambda x: f"${x:,.2f}")
        df_lead['total_net_pnl'] = df_lead['total_net_pnl'].map(lambda x: f"${x:,.2f}")
        df_lead['total_fee'] = df_lead['total_fee'].map(lambda x: f"${x:,.2f}")
        df_lead['avg_trade_size_usd'] = df_lead['avg_trade_size_usd'].map(lambda x: f"${x:,.2f}")
        df_lead['win_rate'] = df_lead['win_rate'].map(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
        df_lead['profit_factor'] = df_lead['profit_factor'].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        leaderboard_md = df_to_markdown_simple(df_lead.head(10))

    # Build the report content
    def get_report_content(img_path_prefix):
        content = f"""# Quantifying the Edge: Hyperliquid Trader Performance & Bitcoin Sentiment Analysis

**Prepared for**: Sonika, Primetrade.ai Hiring Team  
**Author**: Data Science Candidate  
**Date**: June 2026  

---

## 1. Executive Summary

This report explores the quantitative relationship between **Bitcoin market sentiment** (measured by the daily Crypto Fear & Greed Index) and **trader performance** (realized profit/loss, transaction frequency, volume, and trade direction) on the **Hyperliquid exchange**. 

### Core Insights:
1. **Activity and Volume Surges in Fear**: We identified a strong, statistically significant negative correlation between market sentiment (FGI) and aggregate trading volume/activity. Traders execute larger trade sizes and trade far more frequently when fear grips the market.
2. **The "Dumb Money" Panic Signature**: Retail/Losing accounts exhibit classic contrarian-to-optimal trading behavior. Under **Extreme Fear**, their Buy Ratio (proportion of spot buys or long opens) drops to **16.59%**, indicating heavy panic selling at the market bottom. Conversely, in **Greed**, their Buy Ratio spikes to **73.96%**, showing FOMO buying at the local top. This results in heavy aggregate losses.
3. **The "Smart Money" Profit Accumulation**: Whale Pros (high-volume, highly profitable accounts) display sophisticated behavior. They accumulate or maintain balanced positions in **Extreme Fear** (Buy Ratio **52.74%**) and actively distribute/short during **Extreme Greed** (Buy Ratio drops to **40.74%**), capturing massive returns.
4. **Bull Market Trap in Algorithmic Strategies**: A standard Long/Short sentiment-following strategy suffers heavy losses because shorting during "Extreme Greed" is fatal in a multi-year secular bull market. A risk-mitigated **Long-Only Contrarian Sentiment** strategy performs significantly better, delivering positive returns (+12.72%) and slashing maximum drawdown (from -28.34% to -19.96%).
5. **Statistical Significance**: An ANOVA test validates that trader Net PnL is significantly different across Fear and Greed categories (p-value = 0.0317), proving that market sentiment is a statistically valid input for trading models.

---

## 2. Dataset Description & Data Pipeline

The analysis aligns two primary datasets over a **two-year overlapping period** from **May 1, 2023, to May 1, 2025**:
1. **Bitcoin Market Sentiment (Fear & Greed Index)**: A daily sentiment metric (0 to 100) classified into *Extreme Fear, Fear, Neutral, Greed,* and *Extreme Greed*.
2. **Historical Trader Data (Hyperliquid)**: 211,224 execution rows across 32 unique wallets containing `Account`, `Coin`, `Execution Price`, `Size USD`, `Side`, `Direction`, `Closed PnL`, `Fee`, and `Timestamp IST`.

### Preprocessing and Timezone Alignment:
- **Date Standardization**: The trader dataset timestamps were logged in India Standard Time (`Timestamp IST`, DD-MM-YYYY HH:MM), while the FGI was recorded in daily UTC. We parsed and aligned the timestamps to local calendar dates (`date_str`) to perform an exact merge.
- **Transaction Costs**: We computed **Net PnL** as `Closed PnL - Fee` to account for Hyperliquid taker fees.
- **Outcome Metrics**: Realized trades (where `Closed PnL != 0`) were isolated to calculate win rates (`Win Count / Realized Count`) and Profit Factors (`Gross Profit / Absolute Gross Loss`).

---

## 3. Exploratory Data Analysis & Statistical Significance

Trading performance, volume, and frequency were analyzed across the five Fear & Greed classifications:

{sentiment_stats_md}

### Visualizing Sentiment-Based Performance and Activity:

![PnL by Sentiment]({img_path_prefix}pnl_by_sentiment.png)  
*Figure 1: Total Net PnL (USD Millions) generated by all traders across sentiment levels.*

![Win Rate by Sentiment]({img_path_prefix}winrate_by_sentiment.png)  
*Figure 2: Average trade win rate by Fear & Greed classification.*

![Trade Activity by Sentiment]({img_path_prefix}trade_activity_by_sentiment.png)  
*Figure 3: Trade counts (bars) and trading volumes in USD Millions (line) across sentiment levels.*

### Key EDA Takeaways:
- **Maximum Profitability in Extreme Greed & Fear**: Traders generated the highest total Net PnL (\$2.69M) during Extreme Greed periods, which also had the highest trade win rate (89.17%). Surprisingly, standard **Fear** periods were also highly profitable (\$3.26M, 87.29% win rate).
- **Activity Compression in Greed**: Despite the profitability, total trading volume and trade counts peak during **Fear** (\$483.3M over 61.8k trades) rather than Greed. 

### Statistical Tests:
To determine if daily trading activity and performance correlate linearly with daily FGI values, we ran Pearson and Spearman correlation tests on daily aggregates:

{corr_md}

- **Volume Correlation**: There is a **statistically significant negative Pearson correlation** (r = -0.2644, p = 4.2e-9) between daily FGI and daily trade volume. This confirms that market panic (low FGI) drives higher trading activity and larger trade sizes on Hyperliquid.
- **ANOVA Hypothesis Testing**: We ran a one-way Analysis of Variance (ANOVA) to test whether daily Net PnL averages differ significantly across sentiment categories:
  - **F-statistic**: 2.6690
  - **p-value**: 0.0317  
  *Interpretation*: Since the p-value is < 0.05, we reject the null hypothesis. Trader profitability differences across Fear & Greed regimes are **statistically significant**, justifying the integration of sentiment indices into trading execution.

![Daily PnL vs FGI]({img_path_prefix}daily_pnl_vs_fgi.png)  
*Figure 4: Daily trader aggregate Net PnL vs daily FGI values. The negative slope indicates aggregate profitability rises slightly as fear increases.*

---

## 4. Trader Profiling: Smart Money vs. Dumb Money

To understand if all traders behave identically, we profiled the 32 unique wallets. 
- **Classification Schema**:
  - **Elite Pro**: Cumulative Net PnL >= \$100,000.
  - **Pro**: Cumulative Net PnL between \$0 and \$100,000.
  - **Retail / Losing**: Cumulative Net PnL < \$0.
  - **Whale**: Total trading volume >= \$25,000,000.

### Top 10 Trader Leaderboard:
{leaderboard_md}

- **Profit Concentration**: A tiny group of traders dominates profitability. The top 3 accounts generated over **\$4.6M** in net profit. Account `0xbaaaf6571ab7d571043ff1e313a9609a10637864` achieved a win rate of **99.12%** and a Profit Factor of **27,208.37** over 21k trades, representing a high-probability market-making algorithm.

![Account PnL Distribution]({img_path_prefix}account_pnl_distribution.png)  
*Figure 5: Cumulative Net PnL distribution across the 32 accounts.*

### Behavior Analysis under Sentiment Regimes:
We merged the trader classifications back to individual trades and measured the **Buy Ratio** (BUY trades / Total trades) and **Win Rate** under different FGI conditions.

![Win Rate by Profile Class]({img_path_prefix}winrate_vs_sentiment_by_profile.png)  
*Figure 6: Win rate changes across sentiment levels for different trader profiles.*

![Buy Ratio by Profile Class]({img_path_prefix}buy_ratio_vs_sentiment_by_profile.png)  
*Figure 7: Buy Ratio (Long/Spot BUY) vs. sentiment. Notice the diverging behavior under Extreme Fear and Extreme Greed.*

### Critical Findings:
1. **The dumb money contrarian signature**: 
   - Under **Extreme Fear**, **Retail / Losing** accounts buy only **16.59%** of the time (selling 83.41%). They panic sell at the absolute bottom.
   - Under **Greed**, their Buy Ratio climbs to **73.96%**. They FOMO buy the local top.
   - Consequently, they lose money heavily during Extreme Fear (aggregate PnL of -\$44.3k) and Greed (-\$364.3k).
2. **The smart money distribution signature**:
   - **Whale Elite Pros** maintain a balanced accumulation posture during **Extreme Fear** (Buy Ratio **52.74%**).
   - During **Extreme Greed**, their Buy Ratio drops to **40.74%** (selling 59.26%). They distribute positions and short into retail buyer FOMO.
   - This sophisticated execution results in massive profits during Extreme Greed (+\$1.88M) and Extreme Fear (+\$612.6k).

---

## 5. Trading Strategy Backtesting

We backtested three trading strategies based on daily lag-1 (to prevent look-ahead bias) signals, using a daily reconstructed BTC price series from the execution logs. 

### Strategies Evaluated:
1. **BTC Buy & Hold (Benchmark)**: Long BTC continuously.
2. **Contrarian Sentiment**: 
   - *Long/Short (L/S)*: Go Long when FGI <= 30, Go Short when FGI >= 70.
   - *Long-Only*: Go Long when FGI <= 50 (Neutral/Fear), hold Cash (0 position) when FGI > 50 (Greed).
3. **Copy Smart Money**:
   - *L/S*: Go Long if Whale Elite Pros net-buy on t-1; Go Short if they net-sell.
   - *Long-Only*: Go Long if Whale Elite Pros net-buy; Cash otherwise.
4. **Fade Dumb Money**:
   - *L/S*: Go Short if Retail net-buys on t-1; Go Long if Retail net-sells.
   - *Long-Only*: Go Long if Retail net-sells; Cash otherwise.

### Performance Summary:
{perf_md}

![Strategy Performance]({img_path_prefix}strategy_performance.png)  
*Figure 8: Backtest cumulative returns comparing L/S and Long-Only strategies against the BTC benchmark.*

### Quantitative Insights:
- **The Shorting Trap**: During the 2023-2025 period, Bitcoin was in a strong secular bull market, gaining **+126.71%**. In a strong uptrend, any strategy that takes aggressive short positions (such as the L/S versions) gets run over. 
  - *Copy Smart Money (L/S)* lost **-72.77%** because smart money accounts take profit (resulting in net selling) during bullish extension. Forcing a Short position when Whale Pros are simply scaling out of longs leads to heavy losses.
- **Risk Mitigation via Long-Only Contrarian**: By replacing short positions with Cash (0% exposure), we protect capital. The **Contrarian Sentiment (Long-Only)** strategy achieved a positive return of **+12.72%** and significantly reduced the maximum drawdown to **-19.96%** (compared to the benchmark's drawdown of **-28.34%**). This is a highly attractive risk-adjusted choice for capital preservation during market peaks.

---

## 6. Strategic Recommendations for Primetrade.ai

Based on these findings, we recommend the following components for Primetrade.ai's algorithmic trading engines:

1. **Establish a Retail Sentiment Fade Engine**:
   - Integrate daily retail order flows on Hyperliquid. Since retail accounts panic-sell during Extreme Fear (Buy Ratio < 17%), build automated liquidity-searchers that take the long side of these forced/retail sells.
2. **Implement FGI-Based Portfolio Exposure Sizing**:
   - Rather than using FGI as a long/short direction trigger, use it for **dynamic cash allocation**.
   - When FGI >= 75 (Greed/Extreme Greed), automatically scale down long exposures to cash (30-50% cash buffer). This mimics Whale Pro profit-taking and avoids the high drawdowns associated with market local tops.
3. **Smart Money Flow Profiling (Maker vs. Directional)**:
   - When copying smart money, filter out accounts with high trade counts (>10,000) and win rates close to 100% (like account `0xbaaaf6571ab7d571043ff1e313a9609a10637864`). These represent market-making/hedging bots. Their flow is noisy and uninformative for macro direction. 
   - Instead, copy low-frequency Whale accounts (<2,000 trades) whose trades represent directional positional swings.
"""
        return content

    # Write report.md in workspace
    report_workspace_path = os.path.join(workspace_dir, "report.md")
    print(f"Writing report.md to workspace at: {report_workspace_path}")
    with open(report_workspace_path, "w", encoding="utf-8") as f:
        f.write(get_report_content("plots/"))
        
    # Write research_report.md to artifact directory
    report_artifact_path = os.path.join(artifact_dir, "research_report.md")
    print(f"Writing research_report.md to artifact directory at: {report_artifact_path}")
    with open(report_artifact_path, "w", encoding="utf-8") as f:
        f.write(get_report_content("plots/"))
        
    print("Report compilation completed successfully!")

if __name__ == "__main__":
    compile_report()
