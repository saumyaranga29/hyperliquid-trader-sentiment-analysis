import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def run_backtest():
    print("=== STARTING TRADING STRATEGY BACKTESTING (V2) ===")
    
    # Load dataset
    input_path = "cleaned_merged_data.csv"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset '{input_path}' not found. Run data_pipeline.py first.")
        
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} trades.")
    
    # Ensure plots directory exists
    os.makedirs("plots", exist_ok=True)
    
    # 1. Reconstruct BTC Daily Price Series
    print("Reconstructing daily BTC price series...")
    btc_df = df[df['Coin'] == 'BTC'].copy()
    
    daily_btc = btc_df.groupby('date_str')['Execution Price'].mean().reset_index()
    daily_btc.columns = ['date_str', 'btc_price']
    
    # Create a continuous date range to check for gaps
    daily_btc['parsed_date'] = pd.to_datetime(daily_btc['date_str'])
    daily_btc = daily_btc.sort_values('parsed_date').reset_index(drop=True)
    
    # Generate complete date range from min to max date
    full_dates = pd.date_range(start=daily_btc['parsed_date'].min(), end=daily_btc['parsed_date'].max(), freq='D')
    full_df = pd.DataFrame({'parsed_date': full_dates})
    full_df['date_str'] = full_df['parsed_date'].dt.strftime('%Y-%m-%d')
    
    # Merge daily BTC price into the full date range and forward fill gaps
    price_series = pd.merge(full_df, daily_btc[['date_str', 'btc_price']], on='date_str', how='left')
    price_series['btc_price'] = price_series['btc_price'].ffill().bfill()
    
    # Add daily FGI value and classification
    daily_fgi = df.groupby('date_str').agg(
        fgi_value=('value', 'first'),
        fgi_class=('classification', 'first')
    ).reset_index()
    
    price_series = pd.merge(price_series, daily_fgi, on='date_str', how='left')
    price_series['fgi_value'] = price_series['fgi_value'].ffill().bfill()
    price_series['fgi_class'] = price_series['fgi_class'].ffill().bfill()
    
    # Calculate BTC Daily Returns
    price_series['btc_return'] = price_series['btc_price'].pct_change().fillna(0)
    
    # 2. Extract Trader Activity Signals
    leaderboard_path = "plots/account_leaderboard.csv"
    if not os.path.exists(leaderboard_path):
        raise FileNotFoundError(f"Leaderboard file '{leaderboard_path}' not found. Run trader_profiles.py first.")
    
    leaderboard = pd.read_csv(leaderboard_path)
    account_to_profile = dict(zip(leaderboard['Account'], leaderboard['total_net_pnl'].apply(
        lambda pnl: "Elite Pro" if pnl >= 100000 else ("Pro" if pnl > 0 else "Retail / Losing")
    )))
    whale_accounts = set(leaderboard[leaderboard['total_volume_usd'] >= 25000000]['Account'])
    
    # Classify in df
    def get_class(acc):
        base = account_to_profile.get(acc, "Retail / Losing")
        if acc in whale_accounts:
            return "Whale " + base
        return base
        
    df['ProfileClass'] = df['Account'].apply(get_class)
    
    # Aggregate daily trade direction by group
    df['is_buy'] = df['Side'].apply(lambda s: 1 if s == 'BUY' else 0)
    
    daily_group_direction = df.groupby(['date_str', 'ProfileClass']).agg(
        buys=('is_buy', 'sum'),
        total_trades=('Trade ID', 'count')
    ).reset_index()
    
    daily_group_direction['buy_ratio'] = daily_group_direction['buys'] / daily_group_direction['total_trades']
    
    pivot_direction = daily_group_direction.pivot(index='date_str', columns='ProfileClass', values='buy_ratio').reset_index()
    price_series = pd.merge(price_series, pivot_direction, on='date_str', how='left')
    
    # Fill missing values
    groups = ['Whale Elite Pro', 'Retail / Losing']
    for grp in groups:
        if grp in price_series.columns:
            price_series[grp] = price_series[grp].fillna(0.5)
        else:
            price_series[grp] = 0.5
            
    price_series = price_series.rename(columns={
        'Whale Elite Pro': 'smart_buy_ratio',
        'Retail / Losing': 'dumb_buy_ratio'
    })
    
    # Shift signals by 1 day to avoid look-ahead bias
    price_series['fgi_value_lag'] = price_series['fgi_value'].shift(1).fillna(50)
    price_series['smart_buy_ratio_lag'] = price_series['smart_buy_ratio'].shift(1).fillna(0.5)
    price_series['dumb_buy_ratio_lag'] = price_series['dumb_buy_ratio'].shift(1).fillna(0.5)
    
    # --- STRATEGY DEFINITIONS ---
    # 1. Contrarian Sentiment (LS)
    price_series['pos_contrarian_ls'] = 0
    price_series.loc[price_series['fgi_value_lag'] <= 30, 'pos_contrarian_ls'] = 1
    price_series.loc[price_series['fgi_value_lag'] >= 70, 'pos_contrarian_ls'] = -1
    
    # 2. Contrarian Sentiment (LO - Long/Cash)
    price_series['pos_contrarian_lo'] = 0
    price_series.loc[price_series['fgi_value_lag'] <= 50, 'pos_contrarian_lo'] = 1 # hold long in fear/neutral
    price_series.loc[price_series['fgi_value_lag'] > 50, 'pos_contrarian_lo'] = 0  # cash in greed
    
    # 3. Copy Smart Money (LS)
    price_series['pos_smart_ls'] = 0
    price_series.loc[price_series['smart_buy_ratio_lag'] > 0.50, 'pos_smart_ls'] = 1
    price_series.loc[price_series['smart_buy_ratio_lag'] < 0.50, 'pos_smart_ls'] = -1
    
    # 4. Copy Smart Money (LO - Long/Cash)
    price_series['pos_smart_lo'] = 0
    price_series.loc[price_series['smart_buy_ratio_lag'] > 0.49, 'pos_smart_lo'] = 1 # follow buys
    price_series.loc[price_series['smart_buy_ratio_lag'] <= 0.49, 'pos_smart_lo'] = 0 # go to cash
    
    # 5. Fade Dumb Money (LS)
    price_series['pos_fade_dumb_ls'] = 0
    price_series.loc[price_series['dumb_buy_ratio_lag'] > 0.55, 'pos_fade_dumb_ls'] = -1
    price_series.loc[price_series['dumb_buy_ratio_lag'] < 0.45, 'pos_fade_dumb_ls'] = 1
    
    # 6. Fade Dumb Money (LO - Long/Cash)
    # Long when retail is panic selling (buy ratio < 45%), cash when retail is buying (buy ratio > 55%)
    price_series['pos_fade_dumb_lo'] = 0
    price_series.loc[price_series['dumb_buy_ratio_lag'] < 0.50, 'pos_fade_dumb_lo'] = 1
    price_series.loc[price_series['dumb_buy_ratio_lag'] >= 0.50, 'pos_fade_dumb_lo'] = 0
    
    # --- CALCULATE RETURNS ---
    price_series['ret_benchmark'] = price_series['btc_return']
    
    # LS Returns
    price_series['ret_contrarian_ls'] = price_series['pos_contrarian_ls'] * price_series['btc_return']
    price_series['ret_smart_ls'] = price_series['pos_smart_ls'] * price_series['btc_return']
    price_series['ret_fade_dumb_ls'] = price_series['pos_fade_dumb_ls'] * price_series['btc_return']
    
    # LO Returns
    price_series['ret_contrarian_lo'] = price_series['pos_contrarian_lo'] * price_series['btc_return']
    price_series['ret_smart_lo'] = price_series['pos_smart_lo'] * price_series['btc_return']
    price_series['ret_fade_dumb_lo'] = price_series['pos_fade_dumb_lo'] * price_series['btc_return']
    
    # --- CUMULATIVE RETURNS ---
    price_series['cum_benchmark'] = (1 + price_series['ret_benchmark']).cumprod()
    
    price_series['cum_contrarian_ls'] = (1 + price_series['ret_contrarian_ls']).cumprod()
    price_series['cum_smart_ls'] = (1 + price_series['ret_smart_ls']).cumprod()
    price_series['cum_fade_dumb_ls'] = (1 + price_series['ret_fade_dumb_ls']).cumprod()
    
    price_series['cum_contrarian_lo'] = (1 + price_series['ret_contrarian_lo']).cumprod()
    price_series['cum_smart_lo'] = (1 + price_series['ret_smart_lo']).cumprod()
    price_series['cum_fade_dumb_lo'] = (1 + price_series['ret_fade_dumb_lo']).cumprod()
    
    # --- METRICS FUNCTION ---
    def calc_metrics(returns, cum_returns, name):
        total_ret = cum_returns.iloc[-1] - 1
        n_days = len(returns)
        ann_ret = (cum_returns.iloc[-1]) ** (365 / n_days) - 1 if cum_returns.iloc[-1] > 0 else np.nan
        ann_vol = returns.std() * np.sqrt(365)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
        
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        max_dd = drawdown.min()
        
        return {
            'Strategy': name,
            'Total Return (%)': total_ret * 100,
            'Annualized Return (%)': ann_ret * 100,
            'Annualized Volatility (%)': ann_vol * 100,
            'Sharpe Ratio': sharpe,
            'Max Drawdown (%)': max_dd * 100
        }
        
    metrics_list = [
        calc_metrics(price_series['ret_benchmark'], price_series['cum_benchmark'], 'BTC Buy & Hold (Benchmark)'),
        calc_metrics(price_series['ret_contrarian_ls'], price_series['cum_contrarian_ls'], 'Contrarian Sentiment (L/S)'),
        calc_metrics(price_series['ret_contrarian_lo'], price_series['cum_contrarian_lo'], 'Contrarian Sentiment (Long-Only)'),
        calc_metrics(price_series['ret_smart_ls'], price_series['cum_smart_ls'], 'Copy Smart Money (L/S)'),
        calc_metrics(price_series['ret_smart_lo'], price_series['cum_smart_lo'], 'Copy Smart Money (Long-Only)'),
        calc_metrics(price_series['ret_fade_dumb_ls'], price_series['cum_fade_dumb_ls'], 'Fade Dumb Money (L/S)'),
        calc_metrics(price_series['ret_fade_dumb_lo'], price_series['cum_fade_dumb_lo'], 'Fade Dumb Money (Long-Only)')
    ]
    
    metrics_df = pd.DataFrame(metrics_list)
    print("\nStrategy Performance Comparison (Including Long-Only):")
    print(metrics_df.to_string(index=False))
    
    metrics_df.to_csv("plots/strategy_performance_metrics.csv", index=False)
    
    # 5. Plot Performance Chart
    plt.figure(figsize=(12, 7))
    plt.plot(price_series['parsed_date'], price_series['cum_benchmark'], label='BTC Buy & Hold', color='gray', linestyle='--', linewidth=1.5)
    
    plt.plot(price_series['parsed_date'], price_series['cum_contrarian_ls'], label='Contrarian Sentiment (L/S)', color='#fdb863', alpha=0.5, linewidth=1.5)
    plt.plot(price_series['parsed_date'], price_series['cum_contrarian_lo'], label='Contrarian Sentiment (Long-Only)', color='#e08214', linewidth=2)
    
    plt.plot(price_series['parsed_date'], price_series['cum_smart_ls'], label='Copy Smart Money (L/S)', color='#80b1d3', alpha=0.5, linewidth=1.5)
    plt.plot(price_series['parsed_date'], price_series['cum_smart_lo'], label='Copy Smart Money (Long-Only)', color='#3182bd', linewidth=2.5)
    
    plt.plot(price_series['parsed_date'], price_series['cum_fade_dumb_ls'], label='Fade Dumb Money (L/S)', color='#fb8072', alpha=0.5, linewidth=1.5)
    plt.plot(price_series['parsed_date'], price_series['cum_fade_dumb_lo'], label='Fade Dumb Money (Long-Only)', color='#b30000', linewidth=2)
    
    plt.title('Backtest: Trading Strategy Performance (L/S vs Long-Only)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return (1.0 = Principal)', fontsize=12)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('plots/strategy_performance.png', dpi=300)
    plt.close()
    
    # Save the time series for reference
    price_series.to_csv("plots/backtest_time_series.csv", index=False)
    
    print("Strategy backtesting completed! Plots and data saved to plots/ directory.")

if __name__ == "__main__":
    run_backtest()
