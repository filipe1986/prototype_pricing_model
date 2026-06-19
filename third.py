import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import tkinter as tk
from tkinter import messagebox

df = pd.read_csv('nat_gas.csv') # creating a dataframe
df.columns = df.columns.str.lower() # changing all column names to lowercase
df['dates'] = pd.to_datetime(df['dates']) # changing the dates columns from str to datetime64

df.set_index('dates', inplace=True) # now, the dates column will be the index

daily_df = df.resample('D').interpolate(method='linear')

# creating a numerical time variable representing the number of days since the start
daily_df['days_since_start'] = (daily_df.index - daily_df.index.min()).days

slope, intercept, r_value, p_value, std_err = linregress(daily_df['days_since_start'], daily_df['prices'])

# calculating the baseline trend price for every historical day
daily_df['trend_price'] = intercept + slope * daily_df['days_since_start']

# finding the deviation 
daily_df['deviation'] = daily_df['prices'] - daily_df['trend_price']

# grouping by month to get the average seasonal kick for each month (1 to 12)
daily_df['month'] = daily_df.index.month
monthly_seasonality = daily_df.groupby('month')['deviation'].mean()

def get_gas_price(date_str):
    target_date = pd.to_datetime(date_str)
    
    # logic path A: The date is within our historical data range
    if target_date <= daily_df.index.max() and target_date >= daily_df.index.min():
        return daily_df.loc[target_date, 'prices']
    
    # logic path B: The date is in the future (Extrapolation)
    else:
        # calc days since dataset start (2020-10-31)
        days_since = (target_date - daily_df.index.min()).days
        
        # calc trend component
        trend_component = intercept + slope * days_since
        
        # geting seasonal component for this month
        target_month = target_date.month
        seasonal_component = monthly_seasonality[target_month]
        
        # final price is trend + seasonal adjustment
        return trend_component + seasonal_component

def calculate_contract_pricing(inj_date, wth_date, buy_price, sell_price, inj_rate, wth_rate, max_vol, storage_cost_monthly):
    # 1. Parse dates and calculate total months stored
    date_inj = pd.to_datetime(inj_date)
    date_wth = pd.to_datetime(wth_date)
    total_days = (date_wth - date_inj).days
    months_stored = total_days / 30.0
    
    # 2. Revenue and purchase cost calculations
    gross_revenue = max_vol * sell_price
    gross_purchase = max_vol * buy_price
    
    # 3. Time required for operations based on constraints (Item #4)
    days_to_inject = max_vol / inj_rate
    days_to_withdraw = max_vol / wth_rate
    
    # 4. Total rental fees over time (Item #6)
    total_storage_fee = months_stored * storage_cost_monthly
    
    # 5. Final valuation statement
    net_value = gross_revenue - gross_purchase - total_storage_fee
    return net_value


# --- Senior Math Validation Test ---
test_val = calculate_contract_pricing(
    inj_date="2025-06-01",
    wth_date="2025-10-01",  # 4 months storage duration
    buy_price=2.0,          # Summer buy price ($/MMBtu)
    sell_price=3.0,         # Winter sell price ($/MMBtu)
    inj_rate=50000,
    wth_rate=50000,
    max_vol=1000000,        # 1 Million MMBtu volume
    storage_cost_monthly=100000  # $100k a month rent
)

print("\n==============================================")
print(f"🔬 CORE ARBITRAGE SIMULATION TEST RUN")
print(f"🎯 Net Calculated Valuation: ${test_val:,.2f}")
print("==============================================\n")


def open_contract_dashboard():
    # Initialize the master desktop window frame
    root = tk.Tk()
    root.title("J.P. Morgan Gas Storage Valuation Desk")
    root.geometry("520x400") 
    
    # Parameter Input Labels (Aligned down Column 0)
    tk.Label(root, text="Injection Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    tk.Label(root, text="Withdrawal Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
    tk.Label(root, text="Purchase Price ($/MMBtu):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
    tk.Label(root, text="Selling Price ($/MMBtu):").grid(row=3, column=0, padx=10, pady=8, sticky="w")
    tk.Label(root, text="Injection/Withdrawal Max Volume (MMBtu):").grid(row=4, column=0, padx=10, pady=8, sticky="w")
    tk.Label(root, text="Monthly Storage Cost ($):").grid(row=5, column=0, padx=10, pady=8, sticky="w")

    # Text Entry Boxes (Aligned down Column 1)
    entry_inj_date = tk.Entry(root)
    entry_inj_date.grid(row=0, column=1, padx=10, pady=8)
    
    entry_wth_date = tk.Entry(root)
    entry_wth_date.grid(row=1, column=1, padx=10, pady=8)
    
    entry_buy_price = tk.Entry(root)
    entry_buy_price.grid(row=2, column=1, padx=10, pady=8)
    
    entry_sell_price = tk.Entry(root)
    entry_sell_price.grid(row=3, column=1, padx=10, pady=8)
    
    entry_max_vol = tk.Entry(root)
    entry_max_vol.grid(row=4, column=1, padx=10, pady=8)
    
    entry_storage_cost = tk.Entry(root)
    entry_storage_cost.grid(row=5, column=1, padx=10, pady=8)

    # Flow Rate Constraint Fields (Rows 6 and 7)
    tk.Label(root, text="Injection Rate (MMBtu/day):").grid(row=6, column=0, padx=10, pady=8, sticky="w")
    entry_inj_rate = tk.Entry(root)
    entry_inj_rate.grid(row=6, column=1, padx=10, pady=8)
    
    tk.Label(root, text="Withdrawal Rate (MMBtu/day):").grid(row=7, column=0, padx=10, pady=8, sticky="w")
    entry_wth_rate = tk.Entry(root)
    entry_wth_rate.grid(row=7, column=1, padx=10, pady=8)

    # Keeping the window alive and responsive
    root.mainloop()

# Call the function at the very bottom so it opens automatically when run!
open_contract_dashboard()


