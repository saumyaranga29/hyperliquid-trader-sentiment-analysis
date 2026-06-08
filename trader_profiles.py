import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def run_trader_profiling():
    print("=== STARTING TRADER PROFILING & SENTIMENT REACTION ANALYSIS ===")
    
    # Load dataset
    input_path = "cleaned_merged_data.csv"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset '{input_path}' not found. Run data_pipeline.py first.")
        
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} trades.")
    
    # Ensure plots directory exists
    os.makedirs("plots", exist_ok=True)
    
    # 1. Calculate Per-Account Metrics
    print("\nCalculating metrics for each account...")
    
    # Realized trades only for win rate
    realized_df = df[df['Is Realized'] == True]
    
    # Aggregate stats per account
    account_stats = df.groupby('Account').agg(
        total_trades=('Trade ID', 'count'),
        total_volume_usd=('Size USD', 'sum'),
        total_closed_pnl=('Closed PnL', 'sum'),
        total_net_pnl=('Net PnL', 'sum'),
        total_fee=('Fee', 'sum'),
        avg_trade_size_usd=('Size USD', 'mean')
    ).reset_index()
    
    # Calculate win rate per account
    win_rates = realized_df.groupby('Account').apply(
        lambda x: (x['Closed PnL'] > 0).sum() / len(x) if len(x) > 0 else np.nan
    ).reset_index(name='win_rate')
    
    # Calculate profit factor per account
    # PF = sum(gross profits) / sum(abs(gross losses))
    def calc_profit_factor(x):
        profits = x[x['Closed PnL'] > 0]['Closed PnL'].sum()
        losses = abs(x[x['Closed PnL'] < 0]['Closed PnL'].sum())
        return profits / losses if losses > 0 else (profits if profits > 0 else np.nan)
        
    profit_factors = realized_df.groupby('Account').apply(calc_profit_factor).reset_index(name='profit_factor')
    
    # Merge all account metrics
    account_profile = pd.merge(account_stats, win_rates, on='Account', how='left')
    account_profile = pd.merge(account_profile, profit_factors, on='Account', how='left')
    
    # Sort accounts by Net PnL to see the top performers
    account_profile = account_profile.sort_values(by='total_net_pnl', ascending=False).reset_index(drop=True)
    
    print("\nAccount Performance Leaderboard (Top 10):")
    print(account_profile.head(10)[['Account', 'total_trades', 'total_volume_usd', 'total_net_pnl', 'win_rate', 'profit_factor']].to_string())
    
    print("\nAccount Performance Leaderboard (Bottom 5):")
    print(account_profile.tail(5)[['Account', 'total_trades', 'total_volume_usd', 'total_net_pnl', 'win_rate', 'profit_factor']].to_string())
    
    # Save leaderboard to CSV
    account_profile.to_csv("plots/account_leaderboard.csv", index=False)
    
    # 2. Classification Logic
    # Let's define:
    # - "Elite Pro": Net PnL >= $100k
    # - "Pro": Net PnL between $0 and $100k
    # - "Retail / Losing": Net PnL < $0
    # Also, we can identify "Whales" separately as accounts with total volume > $50M
    
    def classify_account(row):
        pnl = row['total_net_pnl']
        vol = row['total_volume_usd']
        
        if pnl >= 100000:
            profile = "Elite Pro"
        elif pnl > 0:
            profile = "Pro"
        else:
            profile = "Retail / Losing"
            
        # We can append Whale if volume is high
        if vol >= 25000000:
            profile = "Whale " + profile
            
        return profile
        
    account_profile['ProfileClass'] = account_profile.apply(classify_account, axis=1)
    
    print("\nDistribution of Trader Profiles:")
    print(account_profile['ProfileClass'].value_counts())
    
    # Save the profiles mapping to merge back with main trades
    account_to_profile = account_profile[['Account', 'ProfileClass']]
    df = pd.merge(df, account_to_profile, on='Account', how='left')
    
    # 3. Analyze reactions to market sentiment by profile class
    # How does cumulative PnL of each group change by sentiment?
    print("\nAnalyzing behavior by Profile class and sentiment...")
    
    # Group trades by ProfileClass and sentiment classification
    profile_sentiment_stats = df.groupby(['ProfileClass', 'classification']).agg(
        trade_count=('Trade ID', 'count'),
        total_volume_usd=('Size USD', 'sum'),
        total_net_pnl=('Net PnL', 'sum'),
        avg_net_pnl=('Net PnL', 'mean')
    ).reset_index()
    
    # Win rate by profile class and sentiment
    profile_sentiment_winrate = df[df['Is Realized'] == True].groupby(['ProfileClass', 'classification']).apply(
        lambda x: (x['Closed PnL'] > 0).sum() / len(x) if len(x) > 0 else np.nan
    ).reset_index(name='win_rate')
    
    profile_sentiment_summary = pd.merge(profile_sentiment_stats, profile_sentiment_winrate, on=['ProfileClass', 'classification'])
    print("\nProfile Sentiment Response Table:")
    print(profile_sentiment_summary.to_string())
    
    profile_sentiment_summary.to_csv("plots/profile_sentiment_summary.csv", index=False)
    
    # 4. Long vs Short bias under sentiment
    # Let's inspect direction of trades (Buy/Long vs Sell/Short)
    # Define trade direction simplified: 'Long' (Open Long, Close Short, Buy, etc.) vs 'Short' (Open Short, Close Long, Sell, etc.)
    # Or more precisely, let's look at Direction / Side
    df['Side_Simple'] = df['Side'].apply(lambda s: 'BUY' if s == 'BUY' else 'SELL')
    
    side_sentiment = df.groupby(['ProfileClass', 'classification', 'Side_Simple']).size().unstack(fill_value=0).reset_index()
    side_sentiment['Buy_Ratio'] = side_sentiment['BUY'] / (side_sentiment['BUY'] + side_sentiment['SELL'])
    
    print("\nBuy Ratio by Profile and Sentiment:")
    print(side_sentiment.to_string())
    side_sentiment.to_csv("plots/profile_buy_ratio_sentiment.csv", index=False)
    
    # 5. Plots Generation
    # Plot 1: Cumulative Net PnL distribution across accounts
    plt.figure(figsize=(10, 6))
    colors = ['green' if x >= 0 else 'red' for x in account_profile['total_net_pnl']]
    # Limit Account label lengths for readability
    short_accounts = [acc[:6] + "..." for acc in account_profile['Account']]
    
    plt.bar(short_accounts, account_profile['total_net_pnl'] / 1e3, color=colors, edgecolor='black', alpha=0.8)
    plt.axhline(0, color='black', linewidth=1, linestyle='--')
    plt.title('Cumulative Net PnL by Trading Account', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Account (Truncated Address)', fontsize=12)
    plt.ylabel('Cumulative Net PnL (Thousands USD)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/account_pnl_distribution.png', dpi=300)
    plt.close()
    
    # Plot 2: Win Rate vs Sentiment by Profile Class
    plt.figure(figsize=(10, 6))
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    for profile in account_profile['ProfileClass'].unique():
        sub_df = profile_sentiment_summary[profile_sentiment_summary['ProfileClass'] == profile].copy()
        # Reorder
        sub_df['classification'] = pd.Categorical(sub_df['classification'], categories=sentiment_order, ordered=True)
        sub_df = sub_df.sort_values('classification')
        if len(sub_df) > 0:
            plt.plot(sub_df['classification'], sub_df['win_rate'] * 100, marker='o', label=profile, linewidth=2.5)
            
    plt.title('Win Rate vs Market Sentiment by Trader Profile Class', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Win Rate (%)', fontsize=12)
    plt.xlabel('Fear & Greed Index Sentiment', fontsize=12)
    plt.ylim(0, 105)
    plt.legend(fontsize=11, loc='lower left')
    plt.tight_layout()
    plt.savefig('plots/winrate_vs_sentiment_by_profile.png', dpi=300)
    plt.close()
    
    # Plot 3: Buy Ratio vs Sentiment by Profile Class
    plt.figure(figsize=(10, 6))
    for profile in account_profile['ProfileClass'].unique():
        sub_df = side_sentiment[side_sentiment['ProfileClass'] == profile].copy()
        sub_df['classification'] = pd.Categorical(sub_df['classification'], categories=sentiment_order, ordered=True)
        sub_df = sub_df.sort_values('classification')
        if len(sub_df) > 0:
            plt.plot(sub_df['classification'], sub_df['Buy_Ratio'] * 100, marker='s', label=profile, linewidth=2.5)
            
    plt.axhline(50, color='gray', linestyle='--', alpha=0.7)
    plt.title('Buy Ratio (Long/Spot Buy) vs Market Sentiment by Trader Profile', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Buy Ratio (%)', fontsize=12)
    plt.xlabel('Fear & Greed Index Sentiment', fontsize=12)
    plt.ylim(0, 100)
    plt.legend(fontsize=11, loc='upper right')
    plt.tight_layout()
    plt.savefig('plots/buy_ratio_vs_sentiment_by_profile.png', dpi=300)
    plt.close()
    
    print("Trader profiling and sentiment reaction analysis completed! Plots saved to plots/ directory.")

if __name__ == "__main__":
    run_trader_profiling()
