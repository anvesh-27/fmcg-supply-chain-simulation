import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
from config import Config

def render_pitch_deck_charts(df, be_date, be_day):
    print("[3/3] Rendering Full Pitch Deck Suite (3 Charts)...")
    
    if be_date is None:
        print("      - Skipping Visuals: No break-even point achieved.")
        return

    plt.style.use('dark_background')
    os.makedirs(Config.IMAGE_DIR, exist_ok=True)
    df['Date'] = pd.to_datetime(df['Date'])
    be_date = pd.to_datetime(be_date)

    # --- 1. THE SLA IMPACT STACKED BAR ---
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    total_trad_opex = df['Trad_OPEX'].sum()
    total_kirana = df['Kirana_Bleed'].sum()
    total_mt = df['MT_Bleed'].sum()
    total_mbed = df['MBed_Cumulative_Cost'].iloc[-1]
    
    ax_bar.bar(['Traditional System'], [total_trad_opex], label='Base Factory OPEX', color='#34495e', width=0.4)
    ax_bar.bar(['Traditional System'], [total_kirana], bottom=[total_trad_opex], label='Kirana Store Loss', color='#e67e22', width=0.4)
    ax_bar.bar(['Traditional System'], [total_mt], bottom=[total_trad_opex + total_kirana], label='Modern Trade SLA Loss', color='#e74c3c', width=0.4)
    ax_bar.bar(['M-Bedded System'], [total_mbed], label='M-Bedded Total Cost', color='#2ecc71', width=0.4)
    
    ax_bar.set_title('Financial Impact: Quick Commerce SLA Penalties', fontsize=14, fontweight='bold', pad=20)
    ax_bar.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{x/1e7:.1f}Cr"))
    ax_bar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    plt.tight_layout()
    plt.savefig(Config.IMAGE_OUTPUT_PATH_BAR, dpi=300)

    # --- 2. THE FINAL PROFIT WATERFALL ---
    fig_wf, ax_wf = plt.subplots(figsize=(12, 6))
    
    total_trad_bleed = total_kirana + total_mt
    # Change total_found_rev to total_found_profit
    total_found_profit = df['Daily_Found_Profit'].sum()
    total_tax_shield = df['Daily_Tax_Shield'].sum()
    opex_premium = df['MBed_OPEX'].sum() - total_trad_opex
    capex = Config.MBED_CAPEX
    
    # Update net profit calculation
    net_profit = total_trad_bleed + total_found_profit + total_tax_shield - opex_premium - capex

    # Update labels and values
    cats = ['Avoided\nLogistics Bleed', 'OEE Found\nProfit', 'Tax Shield\nSavings', 'OPEX\nPremium', 'CAPEX', 'True Net\nProfit']
    vals = [total_trad_bleed, total_found_profit, total_tax_shield, -opex_premium, -capex, net_profit]
    
    # Update steps logic
    steps = [
        0, 
        total_trad_bleed, 
        total_trad_bleed + total_found_profit, 
        total_trad_bleed + total_found_profit + total_tax_shield, 
        total_trad_bleed + total_found_profit + total_tax_shield - opex_premium, 
        0
    ]
    colors = ['#2ecc71', '#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c', '#3498db' if net_profit > 0 else '#e74c3c']
    
    ax_wf.bar(cats, vals, bottom=steps, color=colors, width=0.6, edgecolor='white')
    ax_wf.set_title('Final Profitability Flow: OEE Gains & Tax Shields', fontsize=14, fontweight='bold', pad=20)
    ax_wf.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{x/1e7:.1f}Cr"))
    
    # Add exact value labels inside/above the bars
    for i in range(len(cats)):
        y_pos = steps[i] + (vals[i] / 2) if vals[i] > 0 else steps[i] + vals[i] - 500000
        val_label = f"₹{abs(vals[i])/1e7:.2f}Cr" if abs(vals[i]) >= 10000000 else f"₹{abs(vals[i])/100000:.1f}L"
        ax_wf.text(i, y_pos, val_label, ha='center', va='center', color='white', fontweight='bold', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(Config.IMAGE_OUTPUT_PATH_WATERFALL, dpi=300)

    # --- 3. THE CUMULATIVE CASH FLOW LINE ---
    fig_line, ax_line = plt.subplots(figsize=(12, 7))
    ax_line.plot(df['Date'], df['Trad_Cumulative_Cost'], label='Traditional Cumulative Cost', color='#e74c3c', linewidth=2.5)
    ax_line.plot(df['Date'], df['MBed_Cumulative_Cost'], label='M-Bedded Cumulative Cost (Net of OEE/Tax)', color='#2ecc71', linewidth=2.5)
    
    be_row = df[df['Date'] == be_date]
    if not be_row.empty:
        be_cost = be_row['MBed_Cumulative_Cost'].item()
        ax_line.scatter(be_date, be_cost, color='white', s=120, zorder=5)
        ax_line.annotate(f'BREAK-EVEN\n{be_date.strftime("%b %d")}', xy=(be_date, be_cost), 
                         xytext=(20, -20), textcoords='offset points', color='white', fontweight='bold',
                         arrowprops=dict(facecolor='white', shrink=0.05))
    
    ax_line.set_title('Cumulative Cost Comparison & Recovery Point', fontsize=16, fontweight='bold')
    ax_line.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{x/1e7:.1f}Cr"))
    ax_line.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax_line.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(Config.IMAGE_OUTPUT_PATH_LINE, dpi=300)

    print(f"      ✓ SUCCESS: All 3 charts generated in {Config.IMAGE_DIR}")