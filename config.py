import os

class Config:
    # 1. Supply Chain Variables
    TARGET_ANNUAL_VOL = 90_000_000
    NUM_SHIPMENTS = 25000
    UNIT_PRICE = 30.00

    # --- NEW: Relative OEE & Tax Variables ---
    DAILY_THEORETICAL_CAPACITY = 246575  
    TRADITIONAL_HMA_DOWNTIME_RATE = 0.020  
    MBEDDED_BLISTER_DOWNTIME_RATE = 0.005  
    CORPORATE_TAX_RATE = 0.25              
    MACHINERY_DEPRECIATION_RATE = 0.15     
    FMCG_PROFIT_MARGIN = 0.10              # NEW: Only 10% of a ₹30 sale is actual profit

    # The 5.6% Blended Average Thermal/Humidity Curve
    MONTHLY_FAILURE_RATES = {
        'January': 0.02,
        'February': 0.02,
        'March': 0.05,   
        'April': 0.09,   
        'May': 0.12,     # Peak summer
        'June': 0.12,    # Peak summer
        'July': 0.10,    # Monsoons start (high humidity)
        'August': 0.08,  
        'September': 0.06,
        'October': 0.04,
        'November': 0.03,
        'December': 0.02
    }
    
    # 2. Unit Economics
    MBED_CAPEX = 3_500_000         # ₹35 Lakhs hardware module
    TRAD_OPEX_PER_UNIT = 0.51      # Traditional glue + BOPP wrapper
    MBED_OPEX_PER_UNIT = 0.9     # M-Bedded blister seal + W-fold straw + IP Royalty Fee

    # --- Manufacturing Yield Variables (In-Factory) ---
    TRAD_IN_FACTORY_SCRAP = 0.005  # 0.5% floor rejection
    MBED_IN_FACTORY_SCRAP = 0.001  # 0.1% floor rejection
    COGS_PER_UNIT = 20.00          # The raw cost of the liquid + packaging (₹18 liquid + ₹2 box)
   
    
    # 3. Salvage & Reverse Logistics Economics
    REWORK_RATIO = 0.60            # 60% of missing straws are manually resticked
    LIQUIDATE_RATIO = 0.40         # 40% are sold to airlines at a discount
    REVERSE_FREIGHT_COST = 2.50    # Cost to ship back to warehouse
    B2B_DISCOUNT_PRICE = 16.00     # Liquidated price to airlines/schools
    REWORK_PENALTY = 2.50          # Labor/tape cost to manually restick a straw
    

    # --- NEW: 4. Modern Trade & SLA Variables ---
    MODERN_TRADE_PERCENTAGE = 0.25      # 25% volume routes to Zepto/Blinkit/Reliance
    SLA_PENALTY_FINE = 5.00             # ₹5 fine per defective unit
    PALLET_REJECTION_MULTIPLIER = 2.0   # 1 defect = 2 rejected units (Collateral damage)

    # --- 5. Operational Friction & Implementation Debt ---
    RETROFIT_DOWNTIME_HOURS = 48         # 1 weekend (48 hrs) to bolt the module to the conveyor
    FACTORY_HOURLY_OPEX_BURN = 15_000    # The factory loses ₹15k per hour while the line is stopped
    OPERATOR_TRAINING_COST = 50_000      # One-time upskilling cost for the floor workers
    
    # Calculate total Day 0 Implementation Debt (Equals ₹7,70,000)
    IMPLEMENTATION_DEBT = (RETROFIT_DOWNTIME_HOURS * FACTORY_HOURLY_OPEX_BURN) + OPERATOR_TRAINING_COST


    # 6. File Paths
    DATA_DIR = 'data'
    IMAGE_DIR = 'images'
    DATA_OUTPUT_PATH = os.path.join(DATA_DIR, 'pilot_logistics_data.csv')
    IMAGE_OUTPUT_PATH_BAR = os.path.join(IMAGE_DIR, 'pitch_sla_impact_bar.png')
    IMAGE_OUTPUT_PATH_WATERFALL = os.path.join(IMAGE_DIR, 'pitch_waterfall.png')
    IMAGE_OUTPUT_PATH_LINE = os.path.join(IMAGE_DIR, 'pitch_breakeven_line.png')