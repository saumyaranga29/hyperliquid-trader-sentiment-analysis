import pandas as pd
import numpy as np
import os

def run_pipeline():
    print("=== STARTING DATA PIPELINE ===")
    
    
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
    
    
    print("Parsing trader timestamps (Timestamp IST)...")
   
    df['parsed_ist'] = pd.to_datetime(df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    
    
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
    
    
    print(f"Fee Summary:\n{df['Fee'].describe()}")
    
    
    df['Net PnL'] = df['Closed PnL'] - df['Fee']
    
    df['Is Realized'] = df['Closed PnL'] != 0
    df['Trade Type'] = df['Direction'].apply(lambda d: 'Derivatives' if d in ['Open Long', 'Close Long', 'Open Short', 'Close Short', 'Long > Short', 'Short > Long', 'Auto-Deleveraging', 'Liquidated Isolated Short', 'Settlement'] else 'Spot')
    
    
    df['Is Win'] = np.nan
    df.loc[df['Is Realized'] & (df['Closed PnL'] > 0), 'Is Win'] = 1
    df.loc[df['Is Realized'] & (df['Closed PnL'] < 0), 'Is Win'] = 0
 
    df.loc[df['Is Realized'] & (df['Closed PnL'] == 0), 'Is Win'] = 0.5
    
    
    print("Merging datasets on date...")
    
    merged_df = pd.merge(df, fg[['date_str', 'value', 'classification']], on='date_str', how='left')
    
    missing_fgi = merged_df['value'].isna().sum()
    if missing_fgi > 0:
        print(f"Warning: {missing_fgi} trades do not have matching Fear & Greed values.")
        
    print(f"Merged dataset shape: {merged_df.shape}")
    
    output_path = "cleaned_merged_data.csv"
    print(f"Saving merged data to '{output_path}'...")
    merged_df.to_csv(output_path, index=False)
    print("Pipeline completed successfully!")
    
if __name__ == "__main__":
    run_pipeline()
