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

# creating a hidden master window to host the dialog

def get_clean_date_ui():
    # Inner helper function to capture and combine inputs
    def submit():
        nonlocal final_date
        y, m, d = entry_y.get().strip(), entry_m.get().strip(), entry_d.get().strip()
        
        # Simple validation check to ensure entries aren't completely empty
        if not (y and m and d):
            messagebox.showerror("Error", "Please fill out all three fields!")
            return
            
        # Combine inputs into the standard string format
        formatted_str = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        
        try:
            # Let pandas verify if it's a real calendar date (catches Feb 30th, etc.)
            pd.to_datetime(formatted_str)
            final_date = formatted_str
            root.destroy()  # Close the window on success
        except ValueError:
            messagebox.showerror("Error", f"'{formatted_str}' is not a valid date! Try again.")

    final_date = None
    root = tk.Tk()
    root.title("Enter Target Forecast Date")
    root.geometry("420x100") # Compact, clean layout
    
    # Grid layout for inputs
    tk.Label(root, text="Year (YYYY):").grid(row=0, column=0, padx=5, pady=5)
    entry_y = tk.Entry(root, width=6)
    entry_y.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(root, text="Month (MM):").grid(row=0, column=2, padx=5, pady=5)
    entry_m = tk.Entry(root, width=4)
    entry_m.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(root, text="Day (DD):").grid(row=0, column=4, padx=5, pady=5)
    entry_d = tk.Entry(root, width=4)
    entry_d.grid(row=0, column=5, padx=5, pady=5)
    
    # Submit button across the bottom
    tk.Button(root, text="Generate Forecast", command=submit).grid(row=1, column=0, columnspan=6, pady=10)
    
    root.mainloop()
    return final_date

# calling the function
END = get_clean_date_ui()


# creating a daily date range for the extrapolation year
future_dates = pd.date_range(start='2024-10-01', end=END, freq='D')

# using a list comprehension
future_prices = [get_gas_price(str(d)) for d in future_dates]
future_df = pd.DataFrame(data={'prices': future_prices}, index=future_dates)

# plotig both dataframes together to see the final product
plt.figure(figsize=(12, 6))
plt.plot(daily_df.index, daily_df['prices'], label='Historical & Interpolated')
plt.plot(future_df.index, future_df['prices'], label='Extrapolated Forecast', linestyle='--', color='red')
plt.title('Natural Gas Price Estimation and Extrapolation')
plt.xlabel('Dates')
plt.ylabel('Prices')
plt.legend()
plt.grid(True)
plt.show()
