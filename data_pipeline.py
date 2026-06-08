import pandas as pd
import numpy as np
import os

def run_pipeline():
    print("=== STARTING DATA PIPELINE ===")
    
    # Check if files exist
    trader_file = "historical_trader_data.csv"
    sentiment_file = "fear_greed_index.csv"
    
    if not os.path.exists(trader_file) or not os.path.exists(sentiment_file):
        raise FileNotFoundError("Source CSV files not found in the workspace directory.")
        
    print(f"Loading trader data from '{trader_file}'...")
    df = pd.read_csv(trader_file)
    print(f"Loaded {len(df)} rows.")
    
    print(f"Loading sentiment data from '{sentiment_file}'...")
    fg = pd.read_csv(sentiment_file)
    print(f"Loaded {len(fg)} rows.")
    
    # 1. Clean and parse trader dates
    print("Parsing trader timestamps (Timestamp IST)...")
    # Date format is DD-MM-YYYY HH:MM
    df['parsed_ist'] = pd.to_datetime(df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    
    # Check if there are any parsing failures
    na_dates = df['parsed_ist'].isna().sum()
    if na_dates > 0:
        print(f"Warning: {na_dates} rows failed to parse in 'Timestamp IST'. Dropping those rows.")
        df = df.dropna(subset=['parsed_ist'])
        
    df['date_str'] = df['parsed_ist'].dt.strftime('%Y-%m-%d')
    df['date_only'] = df['parsed_ist'].dt.date
    
    # 2. Clean and parse FGI dates
    print("Parsing Fear & Greed Index dates...")
    fg['parsed_date'] = pd.to_datetime(fg['date'], errors='coerce')
    fg['date_str'] = fg['parsed_date'].dt.strftime('%Y-%m-%d')
    fg['date_only'] = fg['parsed_date'].dt.date
    
    # Inspect Fee column to see how to incorporate it
    # We check if Fee is positive or negative. If it is positive, is it a cost?
    # Typically, fee is positive in transaction logs but represents a cash outflow (cost).
    # Let's inspect fee values:
    print(f"Fee Summary:\n{df['Fee'].describe()}")
    
    # Let's assume Fee is a cost. We'll define Net PnL = Closed PnL - Fee
    df['Net PnL'] = df['Closed PnL'] - df['Fee']
    
    # 3. Add helper columns for wins/losses on realizing trades
    # We only analyze trade outcome when a position is closed or modified (Closed PnL != 0)
    df['Is Realized'] = df['Closed PnL'] != 0
    df['Trade Type'] = df['Direction'].apply(lambda d: 'Derivatives' if d in ['Open Long', 'Close Long', 'Open Short', 'Close Short', 'Long > Short', 'Short > Long', 'Auto-Deleveraging', 'Liquidated Isolated Short', 'Settlement'] else 'Spot')
    
    # Define a Win flag for realized trades
    df['Is Win'] = np.nan
    df.loc[df['Is Realized'] & (df['Closed PnL'] > 0), 'Is Win'] = 1
    df.loc[df['Is Realized'] & (df['Closed PnL'] < 0), 'Is Win'] = 0
    # If Closed PnL is exactly 0 and it's realized, it's a scratch trade (break even)
    df.loc[df['Is Realized'] & (df['Closed PnL'] == 0), 'Is Win'] = 0.5
    
    # 4. Merge trader data with FGI daily sentiment
    print("Merging datasets on date...")
    # FGI is daily, trader data has multiple trades per day. We do a left merge to attach FGI to each trade.
    merged_df = pd.merge(df, fg[['date_str', 'value', 'classification']], on='date_str', how='left')
    
    # Check if there are any missing FGI values in the merged data
    missing_fgi = merged_df['value'].isna().sum()
    if missing_fgi > 0:
        print(f"Warning: {missing_fgi} trades do not have matching Fear & Greed values.")
        
    print(f"Merged dataset shape: {merged_df.shape}")
    
    # Save the cleaned and merged dataset
    output_path = "cleaned_merged_data.csv"
    print(f"Saving merged data to '{output_path}'...")
    merged_df.to_csv(output_path, index=False)
    print("Pipeline completed successfully!")
    
if __name__ == "__main__":
    run_pipeline()
