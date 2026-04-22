import pandas as pd
from config import Config

def run_financial_math():
    print("[2/3] Executing ROI Mathematical Engine (Strict Stream Isolation)...")
    
    try:
        df = pd.read_csv(Config.DATA_OUTPUT_PATH)
    except FileNotFoundError:
        print(f"Error: {Config.DATA_OUTPUT_PATH} not found.")
        return None, None, None

    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- 1. PRE-GROUPING STREAM ISOLATION ---
    # Split rejected units immediately. MT and Kirana handle failures very differently.
    df['Units_Kirana'] = df['Units_Rejected'] * (1 - Config.MODERN_TRADE_PERCENTAGE)
    df['Units_MT'] = df['Units_Rejected'] * Config.MODERN_TRADE_PERCENTAGE
    net_salvage_val = Config.B2B_DISCOUNT_PRICE - Config.REVERSE_FREIGHT_COST


    # --- 2. KIRANA SALVAGE MATH (Allows cheap manual rework) ---
    mask_straw = df['Failure_Reason'] == 'Missing_Straw'
    

    # 60% Reworked (₹2.50 penalty) + 40% Liquidated (Price minus net salvage)
    kirana_rework_bleed = (df['Units_Kirana'] * Config.REWORK_RATIO) * Config.REWORK_PENALTY
    kirana_liq_bleed = (df['Units_Kirana'] * Config.LIQUIDATE_RATIO) * (Config.UNIT_PRICE - net_salvage_val)
    
    df['Kirana_Bleed_Base'] = 0.0
    df.loc[mask_straw, 'Kirana_Bleed_Base'] = kirana_rework_bleed + kirana_liq_bleed


    # --- 3. MODERN TRADE MATH (Zero-Tolerance: 100% Liquidation + Fines) ---
    # MT rejects pallets (multiplier) and does NOT allow cheap rework.
    df['MT_Inflated_Units'] = df['Units_MT'] * Config.PALLET_REJECTION_MULTIPLIER
    mt_base_bleed = df['MT_Inflated_Units'] * (Config.UNIT_PRICE - net_salvage_val)
    
    mt_sla_fine = df['Units_MT'] * Config.SLA_PENALTY_FINE  # SLA Penalty Fine applies ONLY to the actual defective units, not the collateral damage
    
    df['MT_Total_Bleed'] = 0.0
    df.loc[mask_straw, 'MT_Total_Bleed'] = mt_base_bleed + mt_sla_fine


    # --- 4. SEVERE DAMAGE HANDLING ---
    # Leaking/Crushed boxes are a 100% loss for the actual unit, but collateral units are liquidated.
    mask_damage = df['Failure_Reason'].isin(['Leaking', 'Damaged Packaging'])
    
    # Kirana: 100% loss of the actual damaged units (No multiplier here)
    df.loc[mask_damage, 'Kirana_Bleed_Base'] = df['Units_Kirana'] * Config.UNIT_PRICE
    
    # MT: Split the loss between the actual destroyed units and the collateral liquidated units
    mt_actual_destroyed = df['Units_MT']
    mt_collateral_rejected = (df['Units_MT'] * Config.PALLET_REJECTION_MULTIPLIER) - mt_actual_destroyed
    
    mt_destroyed_loss = mt_actual_destroyed * Config.UNIT_PRICE
    mt_collateral_loss = mt_collateral_rejected * (Config.UNIT_PRICE - net_salvage_val)
    mt_damage_sla_fine = mt_actual_destroyed * Config.SLA_PENALTY_FINE
    
    df.loc[mask_damage, 'MT_Total_Bleed'] = mt_destroyed_loss + mt_collateral_loss + mt_damage_sla_fine


    # --- 5. GROUP BY DAY ---
    daily_df = df.groupby('Date').agg({
        'Quantity_Shipped': 'sum',
        'Kirana_Bleed_Base': 'sum',
        'MT_Total_Bleed': 'sum'
    }).reset_index()
    daily_df.rename(columns={'Kirana_Bleed_Base': 'Kirana_Bleed', 'MT_Total_Bleed': 'MT_Bleed'}, inplace=True)

    # ADD THIS NEW BLOCK: 5.5 IN-FACTORY YIELD LOSS
    # ==========================================
    daily_df['Trad_Factory_Scrap_Cost'] = daily_df['Quantity_Shipped'] * Config.TRAD_IN_FACTORY_SCRAP * Config.COGS_PER_UNIT
    daily_df['MBed_Factory_Scrap_Cost'] = daily_df['Quantity_Shipped'] * Config.MBED_IN_FACTORY_SCRAP * Config.COGS_PER_UNIT


    # --- 6. TRADITIONAL COST TRAJECTORY ---
    daily_df['Trad_OPEX'] = daily_df['Quantity_Shipped'] * Config.TRAD_OPEX_PER_UNIT
    
    # ADD the Trad_Factory_Scrap_Cost to the daily total here:
    daily_df['Trad_Daily_Total_Cost'] = daily_df['Trad_OPEX'] + daily_df['Kirana_Bleed'] + daily_df['MT_Bleed'] + daily_df['Trad_Factory_Scrap_Cost']
    daily_df['Trad_Cumulative_Cost'] = daily_df['Trad_Daily_Total_Cost'].cumsum()

    # --- MODULE A: RELATIVE OEE (FOUND PROFIT) ---
    # FIX: Tie downtime directly to the actual dynamic daily volume
    daily_df['Trad_Lost_Units'] = daily_df['Quantity_Shipped'] * Config.TRADITIONAL_HMA_DOWNTIME_RATE
    daily_df['MBed_Lost_Units'] = daily_df['Quantity_Shipped'] * Config.MBEDDED_BLISTER_DOWNTIME_RATE
    
    daily_df['Net_Uptime_Units_Gained'] = daily_df['Trad_Lost_Units'] - daily_df['MBed_Lost_Units']
    
    daily_df['Daily_Found_Revenue'] = daily_df['Net_Uptime_Units_Gained'] * Config.UNIT_PRICE
    daily_df['Daily_Found_Profit'] = daily_df['Daily_Found_Revenue'] * Config.FMCG_PROFIT_MARGIN

    # --- MODULE B: CAPEX TAX SHIELD ---
    annual_depreciation = Config.MBED_CAPEX * Config.MACHINERY_DEPRECIATION_RATE
    annual_tax_shield = annual_depreciation * Config.CORPORATE_TAX_RATE
    daily_df['Daily_Tax_Shield'] = annual_tax_shield / 365.0


   # --- 7. M-BEDDED TRAJECTORY ---
    daily_df['MBed_OPEX'] = daily_df['Quantity_Shipped'] * Config.MBED_OPEX_PER_UNIT
    
    # ADD the MBed_Factory_Scrap_Cost to the daily total here:
    daily_df['MBed_Daily_Total_Cost'] = daily_df['MBed_OPEX'] - daily_df['Daily_Found_Profit'] - daily_df['Daily_Tax_Shield'] + daily_df['MBed_Factory_Scrap_Cost']

    # Absorb the ₹35L CAPEX plus the ₹7.7L Factory Downtime Debt
    total_day_zero_investment = Config.MBED_CAPEX + Config.IMPLEMENTATION_DEBT
    daily_df['MBed_Cumulative_Cost'] = daily_df['MBed_Daily_Total_Cost'].cumsum() + total_day_zero_investment
    
    # --- 8. BREAK-EVEN MATH ---

    break_even_mask = daily_df['MBed_Cumulative_Cost'] < daily_df['Trad_Cumulative_Cost']
    
    total_trad = daily_df['Trad_Cumulative_Cost'].iloc[-1]
    total_mbed = daily_df['MBed_Cumulative_Cost'].iloc[-1]
    annual_savings = total_trad - total_mbed
    
    break_even_date = None
    days_to_be = None
    
    print("\n" + "="*50)
    print(" M-BEDDED EXECUTIVE FINANCIAL SUMMARY ")
    print("="*50)
    
    if break_even_mask.any() and annual_savings > 0:
        break_even_idx = break_even_mask.idxmax()
        break_even_date = daily_df.loc[break_even_idx, 'Date']
        days_to_be = (break_even_date - daily_df['Date'].iloc[0]).days
        
        print(f"Total Traditional Annual Cost: ₹{total_trad/1e7:.2f} Crores")
        print(f"Total M-Bedded Annual Cost:    ₹{total_mbed/1e7:.2f} Crores")
        print("-" * 50)
        print(f"✅ ANNUAL NET SAVINGS:          ₹{annual_savings/1e7:.2f} Crores")
        print(f"🚀 SUSTAINED BREAK-EVEN ON:     {break_even_date.strftime('%B %d, %Y')} (Day {days_to_be})")
    else:
        print(f"Total Traditional Annual Cost: ₹{total_trad/1e7:.2f} Crores")
        print(f"Total M-Bedded Annual Cost:    ₹{total_mbed/1e7:.2f} Crores")
        print("-" * 50)
        print(f"❌ ANNUAL NET LOSS:             ₹{annual_savings/1e7:.2f} Crores")
        print("⚠️ NOTICE: System does not sustain profitability over 12 months.")
    print("="*50 + "\n")
    
    return daily_df, break_even_date, days_to_be