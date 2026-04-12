import pandas as pd
import numpy as np
import os
from config import Config

def run_data_pipeline():
    print("[1/3] Generating Synthetic Logistics Telemetry...")
    
    # 1. Setup Time Series & Seasonality 
    dates_range = pd.date_range(start='2025-01-01', end='2025-12-31')  #Human readable date range for one year
    time_array = np.arange(len(dates_range)) # This is just an array from 0 to 364 representing each day of the year
    
    prob_dist = 1 + 0.4 * np.sin(np.pi * time_array / len(dates_range))   #half cycle in 1 year, peaks in mid-year (summer) and troughs in winter
    prob_dist /= prob_dist.sum() 
    
    shipment_dates = np.random.choice(dates_range, Config.NUM_SHIPMENTS, p=prob_dist)
    

    # 2. Base DataFrame (Locked to the Flagship SKU)
    df = pd.DataFrame({
        'Order_ID': [f"ORD-{i:06d}" for i in range(Config.NUM_SHIPMENTS)],
        'Date': shipment_dates,
        'Product': '200ml Tetra Pak',
        'Unit_Price': Config.UNIT_PRICE
    })
    

    # 3. Scale quantities
    base_quantities = np.random.randint(100, 800, Config.NUM_SHIPMENTS)
    scaling_factor = Config.TARGET_ANNUAL_VOL / base_quantities.sum()
    df['Quantity_Shipped'] = (base_quantities * scaling_factor).astype(int)
    
    difference = Config.TARGET_ANNUAL_VOL - df['Quantity_Shipped'].sum()
    df.loc[df['Quantity_Shipped'].idxmax(), 'Quantity_Shipped'] += difference  #Add difference to the largest shipment to ensure we hit the target exactly
    
    df = df.sort_values('Date').reset_index(drop=True)
    

    # 4. Feature Engineering
    df['Month'] = df['Date'].dt.month_name()
    

    # 5. Advanced Dynamic Failure Logic (The Thermal Spike)  
  
    # --- THE THERMAL CURVE LOGIC ---
    df['Dynamic_Failure_Prob'] = df['Month'].map(Config.MONTHLY_FAILURE_RATES)
    dice_rolls = np.random.rand(Config.NUM_SHIPMENTS)
       
    df['Failure_Reason'] = 'None'
    
    # Apply the dynamic failure curve
    df.loc[dice_rolls < df['Dynamic_Failure_Prob'], 'Failure_Reason'] = 'Missing_Straw'

    # Minor random chances for other damages just to keep the dataset realistic

    # Top 3% of rolls (0.95 to 0.98) = Damaged Packaging
    df.loc[(df['Failure_Reason'] == 'None') & (dice_rolls >= 0.95) & (dice_rolls < 0.98), 'Failure_Reason'] = 'Damaged Packaging'
    
    # The absolute top 2% of rolls (0.98 to 1.0) = Leaking
    df.loc[(df['Failure_Reason'] == 'None') & (dice_rolls >= 0.98), 'Failure_Reason'] = 'Leaking'

    # 6. The Batch Rejection Penalty

    # If the truck is flagged for missing straws, the retailer rejects a massive chunk of the load.
    df['Units_Rejected'] = np.where(
        df['Failure_Reason'] == 'Missing_Straw',
        (df['Quantity_Shipped'] * np.random.uniform(0.25, 0.40, Config.NUM_SHIPMENTS)).astype(int), # 25-40% Rejection!
        np.where(df['Failure_Reason'] != 'None', 
                 (df['Quantity_Shipped'] * 0.05).astype(int), # Minor 5% rejection for standard damage
                 0)
    )
    
    # 7. Core Financials
    df['Gross_Revenue'] = df['Quantity_Shipped'] * df['Unit_Price']
    df['Revenue_Lost'] = df['Units_Rejected'] * df['Unit_Price']
    
    # 8. Export
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    df.to_csv(Config.DATA_OUTPUT_PATH, index=False)
    print(f"      ✓ {df['Quantity_Shipped'].sum():,} units simulated and saved.")
    
    