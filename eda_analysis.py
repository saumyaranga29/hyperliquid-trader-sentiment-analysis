import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import f_oneway, pearsonr, spearmanr

def run_eda():
    print("=== STARTING EXPLORATORY DATA ANALYSIS & STATISTICS ===")
    
    # Load dataset
    input_path = "cleaned_merged_data.csv"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset '{input_path}' not found. Run data_pipeline.py first.")
        
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} trades.")
    
    # Ensure plots directory exists
    os.makedirs("plots", exist_ok=True)
    
    # 1. Classification Order
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    # Filter to only rows with non-null classification
    df_clean = df.dropna(subset=['classification']).copy()
    
    # 2. General Statistics by Sentiment
    print("\nCalculating metrics by Sentiment Classification...")
    
    # We define win rate as: (Closed PnL > 0) / (Closed PnL != 0)
    # Let's verify with Is Realized
    realized_df = df_clean[df_clean['Is Realized'] == True].copy()
    
    # Group by classification
    sentiment_stats = df_clean.groupby('classification').agg(
        trade_count=('Trade ID', 'count'),
        total_volume_usd=('Size USD', 'sum'),
        avg_size_usd=('Size USD', 'mean'),
        total_closed_pnl=('Closed PnL', 'sum'),
        total_net_pnl=('Net PnL', 'sum'),
        avg_closed_pnl=('Closed PnL', 'mean'),
        avg_net_pnl=('Net PnL', 'mean'),
        total_fee=('Fee', 'sum')
    ).reindex(sentiment_order)
    
    # Calculate win rate separately for realized trades
    win_rate_series = realized_df.groupby('classification').apply(
        lambda x: (x['Closed PnL'] > 0).sum() / len(x) if len(x) > 0 else np.nan
    ).reindex(sentiment_order)
    
    sentiment_stats['win_rate'] = win_rate_series
    
    print("\nSentiment Stats Summary Table:")
    print(sentiment_stats.to_string())
    
    # Save table to CSV for report
    sentiment_stats.to_csv("plots/sentiment_stats.csv")
    
    # 3. Daily Aggregations and Statistical Testing
    print("\nPerforming Daily Aggregate Statistical Analysis...")
    # Group by date
    daily_stats = df_clean.groupby('date_str').agg(
        total_trades=('Trade ID', 'count'),
        total_volume_usd=('Size USD', 'sum'),
        total_closed_pnl=('Closed PnL', 'sum'),
        total_net_pnl=('Net PnL', 'sum'),
        fgi_value=('value', 'first'),
        fgi_class=('classification', 'first')
    ).reset_index()
    
    # Calculate daily win rate
    daily_realized = realized_df.groupby('date_str').apply(
        lambda x: (x['Closed PnL'] > 0).sum() / len(x) if len(x) > 0 else np.nan
    ).reset_index(name='daily_win_rate')
    
    daily_stats = pd.merge(daily_stats, daily_realized, on='date_str', how='left')
    daily_stats = daily_stats.dropna(subset=['fgi_value'])
    
    # Calculate correlation between FGI value and daily metrics
    metrics = ['total_trades', 'total_volume_usd', 'total_closed_pnl', 'total_net_pnl', 'daily_win_rate']
    correlations = {}
    for metric in metrics:
        valid_data = daily_stats.dropna(subset=[metric, 'fgi_value'])
        if len(valid_data) > 1:
            pearson_r, pearson_p = pearsonr(valid_data['fgi_value'], valid_data[metric])
            spearman_r, spearman_p = spearmanr(valid_data['fgi_value'], valid_data[metric])
            correlations[metric] = {
                'pearson_r': pearson_r, 'pearson_p': pearson_p,
                'spearman_r': spearman_r, 'spearman_p': spearman_p
            }
            print(f"Correlation FGI vs Daily {metric}:")
            print(f"  Pearson:  r = {pearson_r:.4f}, p = {pearson_p:.4e}")
            print(f"  Spearman: r = {spearman_r:.4f}, p = {spearman_p:.4e}")
            
    # Save correlation results
    corr_df = pd.DataFrame(correlations).T
    corr_df.to_csv("plots/daily_correlations.csv")
    
    # ANOVA test for daily Net PnL across FGI Classifications
    groups = []
    for cls in sentiment_order:
        group_pnl = daily_stats[daily_stats['fgi_class'] == cls]['total_net_pnl'].dropna().values
        if len(group_pnl) > 0:
            groups.append(group_pnl)
            
    if len(groups) > 1:
        f_val, p_val = f_oneway(*groups)
        print(f"\nANOVA test for Daily Net PnL across FGI classifications:")
        print(f"  F-statistic: {f_val:.4f}")
        print(f"  p-value:     {p_val:.4e}")
        with open("plots/anova_result.txt", "w") as f:
            f.write(f"ANOVA F-statistic: {f_val:.6f}\nANOVA p-value: {p_val:.6e}\n")
            
    # 4. Plots Generation
    print("\nGenerating Plots...")
    
    # Style configuration
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    colors = ['#d7191c', '#fdae61', '#ffffbf', '#abd9e9', '#2c7bb6']  # Fear to Greed color scale
    
    # Plot 1: Total Net PnL by Sentiment
    plt.figure(figsize=(10, 6))
    bars = plt.bar(sentiment_stats.index, sentiment_stats['total_net_pnl'] / 1e6, color=colors, edgecolor='black', alpha=0.85)
    plt.title('Total Net PnL by Market Sentiment Classification', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Total Net PnL (Millions USD)', fontsize=12)
    plt.xlabel('Fear & Greed Classification', fontsize=12)
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + (0.1 if yval >= 0 else -0.4), f"${yval:.2f}M", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('plots/pnl_by_sentiment.png', dpi=300)
    plt.close()
    
    # Plot 2: Win Rate by Sentiment
    plt.figure(figsize=(10, 6))
    bars = plt.bar(sentiment_stats.index, sentiment_stats['win_rate'] * 100, color=colors, edgecolor='black', alpha=0.85)
    plt.title('Average Trade Win Rate by Market Sentiment Classification', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Win Rate (%)', fontsize=12)
    plt.xlabel('Fear & Greed Classification', fontsize=12)
    plt.ylim(0, 100)
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('plots/winrate_by_sentiment.png', dpi=300)
    plt.close()
    
    # Plot 3: Trade Volume and Activity by Sentiment
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Trade Count (Bar)
    ax1.bar(sentiment_stats.index, sentiment_stats['trade_count'], color='#cccccc', edgecolor='black', alpha=0.6, label='Trade Count')
    ax1.set_ylabel('Number of Trades', fontsize=12, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xlabel('Fear & Greed Classification', fontsize=12)
    
    # Volume (Line)
    ax2 = ax1.twinx()
    ax2.plot(sentiment_stats.index, sentiment_stats['total_volume_usd'] / 1e6, color='#e34a33', marker='o', linewidth=2.5, label='Volume ($M)')
    ax2.set_ylabel('Total Trading Volume (Millions USD)', fontsize=12, color='#e34a33')
    ax2.tick_params(axis='y', labelcolor='#e34a33')
    
    plt.title('Trading Activity and Volume by Market Sentiment', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig('plots/trade_activity_by_sentiment.png', dpi=300)
    plt.close()
    
    # Plot 4: Daily FGI vs Daily PnL Scatter Plot
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(daily_stats['fgi_value'], daily_stats['total_net_pnl'] / 1e3, c=daily_stats['fgi_value'], cmap='RdYlBu', edgecolor='black', alpha=0.75, s=70)
    cb = plt.colorbar(sc)
    cb.set_label('Fear & Greed Index Value', fontsize=11)
    
    # Add regression line if there's any correlation
    valid_data = daily_stats.dropna(subset=['fgi_value', 'total_net_pnl'])
    if len(valid_data) > 1:
        slope, intercept = np.polyfit(valid_data['fgi_value'], valid_data['total_net_pnl'] / 1e3, 1)
        x_vals = np.array([0, 100])
        y_vals = slope * x_vals + intercept
        plt.plot(x_vals, y_vals, color='red', linestyle='--', linewidth=2, label=f'Trend (Slope: {slope:.2f}k USD/FGI)')
        plt.legend(fontsize=11)
        
    plt.title('Daily Trader Net PnL vs Fear & Greed Index', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Fear & Greed Index Value (0 = Extreme Fear, 100 = Extreme Greed)', fontsize=12)
    plt.ylabel('Daily Net PnL (Thousands USD)', fontsize=12)
    plt.tight_layout()
    plt.savefig('plots/daily_pnl_vs_fgi.png', dpi=300)
    plt.close()
    
    print("EDA and Statistics completed! Outputs saved to plots/ directory.")

if __name__ == "__main__":
    run_eda()
