from src.data_generator import run_data_pipeline
from src.financial_engine import run_financial_math
from src.visualizer import render_pitch_deck_charts

def main():
    print("Initializing M-Bedded Enterprise Simulation Suite...\n")
    
    # 1. Generate the universe
    run_data_pipeline()
    
    # 2. Crunch the numbers
    daily_df, be_date, be_day = run_financial_math()
    
    # 3. Draw the visuals
    if daily_df is not None:
        render_pitch_deck_charts(daily_df, be_date, be_day)
        
    print("\nSimulation Complete. System shutting down.")

if __name__ == "__main__":
    main()