import os
import pandas as pd
from fpdf import FPDF
from fpdf.fonts import FontFace

class PrimetradeReportPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_margins(15, 15, 15)
        
    def header(self):
        # We only want headers from page 2 onwards
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 10, "Hyperliquid Trader Performance & Bitcoin Sentiment Analysis", align="L", new_x="LEFT", new_y="LAST")
            self.cell(0, 10, "CONFIDENTIAL RESEARCH REPORT", align="R", new_x="RIGHT", new_y="NEXT")
            self.set_draw_color(220, 220, 220)
            self.line(15, 22, 195, 22)
            self.ln(5)

    def footer(self):
        # We only want footers from page 2 onwards
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.set_draw_color(220, 220, 220)
            self.line(15, self.get_y() - 2, 195, self.get_y() - 2)
            self.cell(0, 10, "Prepared for Primetrade.ai Hiring Team", align="L", new_x="LEFT", new_y="LAST")
            # Dynamic page count (using {nb} placeholder supported by fpdf2)
            self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align="R", new_x="RIGHT", new_y="NEXT")

    def chapter_title(self, label):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(27, 42, 71)  # Dark Navy primary color
        self.cell(0, 10, label, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(2)

    def section_title(self, label):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 168, 150)  # Teal secondary color
        self.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(1)

    def body_text(self, text, style="", size=9.5, align="L"):
        self.set_font("Helvetica", style, size)
        self.set_text_color(50, 50, 50)  # Charcoal body color
        self.multi_cell(0, 5, text, align=align)
        self.ln(3)

def generate_pdf_report():
    print("=== STARTING QUANT REPORT PDF GENERATION ===")
    
    workspace_dir = r"c:\Users\Saumya Ranga\OneDrive - UPES\Desktop\primetrade"
    artifact_dir = r"C:\Users\Saumya Ranga\.gemini\antigravity-ide\brain\615ea503-12fd-4a78-ac64-4483f1813617"
    plots_dir = os.path.join(workspace_dir, "plots")
    
    pdf = PrimetradeReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    
    # ----------------------------------------------------
    # PAGE 1: COVER PAGE
    # ----------------------------------------------------
    pdf.add_page()
    
    # Sleek dark navy header block
    pdf.set_fill_color(27, 42, 71)
    pdf.rect(0, 0, 210, 100, "F")
    
    # Title inside the navy block
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Quantifying the Edge", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(0, 168, 150)  # Teal
    pdf.cell(0, 10, "Hyperliquid Trader Performance & Bitcoin Sentiment Analysis", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Cover page body
    pdf.set_y(120)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(27, 42, 71)
    pdf.cell(0, 8, "PREPARED FOR:", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "Sonika & the Primetrade.ai Hiring Team", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(27, 42, 71)
    pdf.cell(0, 8, "SUBMITTED BY:", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "Data Science & Quantitative Research Candidate", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(27, 42, 71)
    pdf.cell(0, 8, "DATE OF SUBMISSION:", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "June 2026", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Decorative bottom bar
    pdf.set_fill_color(0, 168, 150)
    pdf.rect(0, 285, 210, 12, "F")
    
    # ----------------------------------------------------
    # PAGE 2: EXECUTIVE SUMMARY & DATA PIPELINE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.chapter_title("1. Executive Summary")
    
    pdf.body_text(
        "This report explores the quantitative relationship between Bitcoin market sentiment (measured by the daily Crypto Fear & Greed Index) and trader performance (realized profit/loss, transaction frequency, volume, and trade direction) on the Hyperliquid exchange.",
        style=""
    )
    
    summary_bullets = [
        "1. Activity and Volume Surges in Fear: We identified a strong, statistically significant negative correlation between market sentiment (FGI) and aggregate trading volume/activity. Traders execute larger trade sizes and trade far more frequently when fear grips the market.",
        "2. The 'Dumb Money' Panic Signature: Retail/Losing accounts exhibit classic contrarian-to-optimal trading behavior. Under Extreme Fear, their Buy Ratio (proportion of spot buys or long opens) drops to 16.59%, indicating heavy panic selling at the market bottom. Conversely, in Greed, their Buy Ratio spikes to 73.96%, showing FOMO buying at the local top. This results in heavy aggregate losses.",
        "3. The 'Smart Money' Profit Accumulation: Whale Pros (high-volume, highly profitable accounts) display sophisticated behavior. They accumulate or maintain balanced positions in Extreme Fear (Buy Ratio 52.74%) and actively distribute/short during Extreme Greed (Buy Ratio drops to 40.74%), capturing massive returns.",
        "4. Bull Market Trap in Algorithmic Strategies: A standard Long/Short sentiment-following strategy suffers heavy losses because shorting during 'Extreme Greed' is fatal in a multi-year secular bull market. A risk-mitigated Long-Only Contrarian Sentiment strategy performs significantly better, delivering positive returns (+12.72%) and slashing maximum drawdown (from -28.34% to -19.96%).",
        "5. Statistical Significance: An ANOVA test validates that trader Net PnL is significantly different across Fear and Greed categories (p-value = 0.0317), proving that market sentiment is a statistically valid input for trading models."
    ]
    for bullet in summary_bullets:
        pdf.body_text(bullet, style="")
        
    pdf.ln(5)
    pdf.chapter_title("2. Dataset Description & Data Pipeline")
    pdf.body_text(
        "The analysis aligns two primary datasets over a two-year overlapping period from May 1, 2023, to May 1, 2025:\n"
        "1. Bitcoin Market Sentiment (Fear & Greed Index): A daily sentiment metric (0 to 100) classified into Extreme Fear, Fear, Neutral, Greed, and Extreme Greed.\n"
        "2. Historical Trader Data (Hyperliquid): 211,224 execution rows across 32 unique wallets containing Account, Coin, Execution Price, Size USD, Side, Direction, Closed PnL, Fee, and Timestamp IST."
    )
    pdf.section_title("Preprocessing and Timezone Alignment:")
    pdf.body_text(
        "- Date Standardization: The trader dataset timestamps were logged in India Standard Time (Timestamp IST, DD-MM-YYYY HH:MM), while the FGI was recorded in daily UTC. We parsed and aligned the timestamps to local calendar dates (date_str) to perform an exact merge.\n"
        "- Transaction Costs: We computed Net PnL as Closed PnL - Fee to account for Hyperliquid taker fees.\n"
        "- Outcome Metrics: Realized trades (where Closed PnL != 0) were isolated to calculate win rates (Win Count / Realized Count) and Profit Factors (Gross Profit / Absolute Gross Loss)."
    )

    # ----------------------------------------------------
    # PAGE 3: EXPLORATORY DATA ANALYSIS (EDA)
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.chapter_title("3. Exploratory Data Analysis & Statistics")
    pdf.body_text(
        "Trading performance, volume, and frequency were analyzed across the five Fear & Greed classifications. The table below provides a granular summary of key performance indicators grouped by sentiment regimes:"
    )
    
    # Table 1: Sentiment stats
    sentiment_stats_csv = os.path.join(plots_dir, "sentiment_stats.csv")
    if os.path.exists(sentiment_stats_csv):
        df_stats = pd.read_csv(sentiment_stats_csv)
        
        # Format table headers
        headers = ["Classification", "Trades", "Volume ($M)", "Avg Size", "Net PnL ($M)", "Win Rate"]
        
        # Build tabular data
        data_rows = []
        for _, r in df_stats.iterrows():
            vol_m = r['total_volume_usd'] / 1e6
            pnl_m = r['total_net_pnl'] / 1e6
            win_pct = r['win_rate'] * 100
            data_rows.append([
                str(r['classification']),
                f"{int(r['trade_count']):,}",
                f"${vol_m:.2f}M",
                f"${r['avg_size_usd']:.2f}",
                f"${pnl_m:.2f}M",
                f"{win_pct:.2f}%"
            ])
            
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(27, 42, 71)
        pdf.set_text_color(255, 255, 255)
        
        # Draw header row
        col_widths = [32, 22, 28, 28, 28, 22]
        for h, w in zip(headers, col_widths):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(50, 50, 50)
        
        for row in data_rows:
            # Alternating row colors
            pdf.set_fill_color(244, 247, 246)
            for idx, (val, w) in enumerate(zip(row, col_widths)):
                pdf.cell(w, 7, val, border=1, align="C")
            pdf.ln()
            
    pdf.ln(5)
    pdf.section_title("Visualizing Performance by Sentiment Classification:")
    
    # PnL & Win Rate Charts
    pnl_img = os.path.join(plots_dir, "pnl_by_sentiment.png")
    winrate_img = os.path.join(plots_dir, "winrate_by_sentiment.png")
    
    if os.path.exists(pnl_img):
        pdf.image(pnl_img, x=20, y=pdf.get_y(), w=80)
    if os.path.exists(winrate_img):
        pdf.image(winrate_img, x=110, y=pdf.get_y(), w=80)
        
    pdf.set_y(pdf.get_y() + 55) # offset for the image height
    pdf.body_text("Figure 1 & 2: Total Net PnL (left) and Average win rate (right) grouped by FGI class.", style="I", size=8.5, align="C")
    
    # ----------------------------------------------------
    # PAGE 4: EDA VOLUMES & STATISTICAL SIGNIFICANCE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.section_title("Trading Activity and Volume Distribution:")
    
    activity_img = os.path.join(plots_dir, "trade_activity_by_sentiment.png")
    if os.path.exists(activity_img):
        pdf.image(activity_img, x=30, y=pdf.get_y(), w=150)
        pdf.set_y(pdf.get_y() + 95)
        pdf.body_text("Figure 3: Trade counts and volumes across sentiment levels.", style="I", size=8.5, align="C")
        
    pdf.section_title("Statistical Significance & Correlation Results:")
    pdf.body_text(
        "To check if daily trading activity and performance correlate linearly with daily FGI values, we ran Pearson and Spearman correlation tests on daily aggregates. The table below highlights the findings:"
    )
    
    # Table 2: Correlations
    corr_csv = os.path.join(plots_dir, "daily_correlations.csv")
    if os.path.exists(corr_csv):
        df_corr = pd.read_csv(corr_csv)
        df_corr = df_corr.rename(columns={'Unnamed: 0': 'Metric'})
        
        headers_corr = ["Metric", "Pearson r", "Pearson p-val", "Spearman r", "Spearman p-val"]
        widths_corr = [45, 30, 35, 30, 35]
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(27, 42, 71)
        pdf.set_text_color(255, 255, 255)
        
        for h, w in zip(headers_corr, widths_corr):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(50, 50, 50)
        
        for _, r in df_corr.iterrows():
            row = [
                str(r['Metric']),
                f"{r['pearson_r']:.4f}",
                f"{r['pearson_p']:.4e}",
                f"{r['spearman_r']:.4f}",
                f"{r['spearman_p']:.4e}"
            ]
            for val, w in zip(row, widths_corr):
                pdf.cell(w, 7, val, border=1, align="C")
            pdf.ln()

    # ----------------------------------------------------
    # PAGE 5: ANOVA AND DAILY PNL VS FGI
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.section_title("Volume and Daily Profitability Analysis:")
    
    daily_fgi_img = os.path.join(plots_dir, "daily_pnl_vs_fgi.png")
    if os.path.exists(daily_fgi_img):
        pdf.image(daily_fgi_img, x=30, y=pdf.get_y(), w=150)
        pdf.set_y(pdf.get_y() + 95)
        pdf.body_text("Figure 4: Scatter plot of Daily Net PnL vs Fear & Greed Index with trendline.", style="I", size=8.5, align="C")
        
    pdf.body_text(
        "ANOVA Results Summary:\n"
        "We executed a one-way ANOVA test comparing daily Net PnL across FGI classifications to confirm if trading performance differs significantly across market sentiment classifications:\n"
        "- F-statistic: 2.6690\n"
        "- p-value: 0.0317\n"
        "Interpretation: Since the p-value is < 0.05, we reject the null hypothesis. Trader profitability differences across Fear & Greed regimes are statistically significant, proving that sentiment indices represent an actionable input for quantitative strategy engines."
    )

    # ----------------------------------------------------
    # PAGE 6: TRADER PROFILING
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.chapter_title("4. Trader Profiling: Smart Money vs. Dumb Money")
    pdf.body_text(
        "To understand if all traders behave identically, we profiled the 32 unique wallets based on cumulative Net PnL, trading volume, and win rates. Below is the Leaderboard of the Top 10 traders on Hyperliquid:"
    )
    
    # Table 3: Leaderboard
    leaderboard_csv = os.path.join(plots_dir, "account_leaderboard.csv")
    if os.path.exists(leaderboard_csv):
        df_lead = pd.read_csv(leaderboard_csv).head(10)
        headers_lead = ["Account", "Trades", "Volume ($M)", "Net PnL ($K)", "Win Rate", "Profit Factor"]
        widths_lead = [35, 20, 35, 30, 25, 35]
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(27, 42, 71)
        pdf.set_text_color(255, 255, 255)
        
        for h, w in zip(headers_lead, widths_lead):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(50, 50, 50)
        
        for _, r in df_lead.iterrows():
            short_acc = str(r['Account'])[:8] + "..." + str(r['Account'])[-6:]
            vol_m = r['total_volume_usd'] / 1e6
            pnl_k = r['total_net_pnl'] / 1e3
            win_pct = r['win_rate'] * 100
            pf_val = r['profit_factor']
            pf_str = f"{pf_val:.2f}" if pd.notna(pf_val) else "N/A"
            
            row = [
                short_acc,
                f"{int(r['total_trades']):,}",
                f"${vol_m:.2f}M",
                f"${pnl_k:.1f}k",
                f"{win_pct:.1f}%",
                pf_str
            ]
            for val, w in zip(row, widths_lead):
                pdf.cell(w, 7, val, border=1, align="C")
            pdf.ln()
            
    pdf.ln(5)
    
    acc_pnl_img = os.path.join(plots_dir, "account_pnl_distribution.png")
    if os.path.exists(acc_pnl_img):
        pdf.image(acc_pnl_img, x=30, y=pdf.get_y(), w=150)
        pdf.set_y(pdf.get_y() + 90)
        pdf.body_text("Figure 5: Leaderboard Net PnL distribution across accounts.", style="I", size=8.5, align="C")

    # ----------------------------------------------------
    # PAGE 7: BEHAVIORAL DIFFERENCES BY PROFILE
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.section_title("Divergent Behavior under Sentiment Regimes:")
    pdf.body_text(
        "By mapping accounts back to their trades, we compared the behavior of 'Whale Elite Pros' (Smart Money) and 'Retail / Losing' traders. The findings show a striking difference in Buy Ratio (the proportion of buy orders relative to total trades) and win rate:"
    )
    
    winrate_profile_img = os.path.join(plots_dir, "winrate_vs_sentiment_by_profile.png")
    buyratio_profile_img = os.path.join(plots_dir, "buy_ratio_vs_sentiment_by_profile.png")
    
    if os.path.exists(winrate_profile_img):
        pdf.image(winrate_profile_img, x=20, y=pdf.get_y(), w=80)
    if os.path.exists(buyratio_profile_img):
        pdf.image(buyratio_profile_img, x=110, y=pdf.get_y(), w=80)
        
    pdf.set_y(pdf.get_y() + 55)
    pdf.body_text("Figure 6 & 7: Win rate (left) and Buy Ratio (right) vs. Sentiment by profile cohort.", style="I", size=8.5, align="C")
    
    pdf.body_text(
        "Critical Findings:\n"
        "1. The Dumb Money Panic Signature: Under Extreme Fear, Retail / Losing accounts buy only 16.59% of the time (selling 83.41%), panic selling at the bottom. Conversely, in Greed/Extreme Greed, their Buy Ratio climbs to 73.96%, showing FOMO buying at local tops. This translates directly to heavy realized losses.\n"
        "2. The Smart Money Profit Accumulation Signature: Whale Elite Pros maintain a balanced accumulation stance during Extreme Fear (Buy Ratio 52.74%). During Extreme Greed, their Buy Ratio drops to 40.74% (meaning they are net-selling/distributing positions). This disciplined execution results in massive aggregate profits."
    )

    # ----------------------------------------------------
    # PAGE 8: STRATEGY BACKTESTING
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.chapter_title("5. Trading Strategy Backtesting")
    pdf.body_text(
        "We backtested three trading strategies based on daily lag-1 (to prevent look-ahead bias) signals, using a daily reconstructed BTC price series from the execution logs. The table below presents the quantitative comparison of standard Long/Short (L/S) and Long-Only strategies:"
    )
    
    # Table 4: Strategy performance metrics
    perf_metrics_csv = os.path.join(plots_dir, "strategy_performance_metrics.csv")
    if os.path.exists(perf_metrics_csv):
        df_perf = pd.read_csv(perf_metrics_csv)
        headers_perf = ["Strategy", "Total Return", "Ann. Return", "Ann. Vol", "Sharpe", "Max DD"]
        widths_perf = [60, 25, 25, 25, 20, 25]
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(27, 42, 71)
        pdf.set_text_color(255, 255, 255)
        
        for h, w in zip(headers_perf, widths_perf):
            pdf.cell(w, 8, h, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(50, 50, 50)
        
        for _, r in df_perf.iterrows():
            row = [
                str(r['Strategy']),
                f"{r['Total Return (%)']:.2f}%",
                f"{r['Annualized Return (%)']:.2f}%",
                f"{r['Annualized Volatility (%)']:.2f}%",
                f"{r['Sharpe Ratio']:.4f}",
                f"{r['Max Drawdown (%)']:.2f}%"
            ]
            for val, w in zip(row, widths_perf):
                pdf.cell(w, 7, val, border=1, align="C")
            pdf.ln()
            
    pdf.ln(5)
    
    strategy_img = os.path.join(plots_dir, "strategy_performance.png")
    if os.path.exists(strategy_img):
        pdf.image(strategy_img, x=30, y=pdf.get_y(), w=150)
        pdf.set_y(pdf.get_y() + 90)
        pdf.body_text("Figure 8: Strategy cumulative return comparison vs BTC Buy & Hold benchmark.", style="I", size=8.5, align="C")

    # ----------------------------------------------------
    # PAGE 9: RECOMMENDATIONS
    # ----------------------------------------------------
    pdf.add_page()
    pdf.set_y(30)
    pdf.chapter_title("6. Strategic Recommendations for Primetrade.ai")
    
    pdf.body_text(
        "Based on our empirical analysis, we recommend incorporating the following rules and structures into the Primetrade.ai algorithmic execution engines:"
    )
    
    recs = [
        "1. Establish a Retail Sentiment Fade Engine:\n"
        "Integrate daily retail order flows on Hyperliquid. Since retail accounts panic-sell during Extreme Fear (Buy Ratio < 17%), build automated limit-liquidity searchers that take the long side of these forced/retail sells. Taking the opposite side of retail orders during extreme market conditions provides high-probability execution.",
        
        "2. Implement FGI-Based Portfolio Exposure Sizing:\n"
        "Rather than using FGI as a long/short direction trigger, use it for dynamic cash allocation. When FGI >= 75 (Greed/Extreme Greed), automatically scale down long exposures to cash (30-50% cash buffer). This mimics Whale Pro profit-taking and avoids the high drawdowns associated with market local tops, without suffering losses from shorting a strong bull market.",
        
        "3. Smart Money Flow Profiling (Maker vs. Directional):\n"
        "When copying smart money, filter out accounts with high trade counts (>10,000) and win rates close to 100% (like account 0xbaaaf6571ab7d571043ff1e313a9609a10637864). These represent market-making/arbitrage operations. Their flow is noisy and uninformative for macro direction. Instead, copy low-frequency Whale accounts (<2,000 trades) whose trades represent directional positional swings."
    ]
    
    for rec in recs:
        pdf.body_text(rec, style="")
        
    pdf.ln(10)
    pdf.body_text("--- END OF REPORT ---", style="B", size=10, align="C")
    
    # Save the PDF in the workspace
    pdf_workspace_path = os.path.join(workspace_dir, "Primetrade_Quant_Research_Report.pdf")
    print(f"Saving PDF to workspace: {pdf_workspace_path}")
    pdf.output(pdf_workspace_path)
    
    # Save the PDF in the artifact directory
    pdf_artifact_path = os.path.join(artifact_dir, "Primetrade_Quant_Research_Report.pdf")
    print(f"Saving PDF to artifact directory: {pdf_artifact_path}")
    pdf.output(pdf_artifact_path)
    
    print("PDF generation completed successfully!")

if __name__ == "__main__":
    generate_pdf_report()
