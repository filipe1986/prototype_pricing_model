import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import tkinter as tk
from tkinter import messagebox

# ====================== LOAD & PREPARE DATA ======================
df = pd.read_csv('nat_gas.csv')
df.columns = df.columns.str.lower()
df['dates'] = pd.to_datetime(df['dates'])
df.set_index('dates', inplace=True)

daily_df = df.resample('D').interpolate(method='linear')
daily_df['days_since_start'] = (daily_df.index - daily_df.index.min()).days

slope, intercept, _, _, _ = linregress(daily_df['days_since_start'], daily_df['prices'])

daily_df['trend_price'] = intercept + slope * daily_df['days_since_start']
daily_df['deviation'] = daily_df['prices'] - daily_df['trend_price']
daily_df['month'] = daily_df.index.month
monthly_seasonality = daily_df.groupby('month')['deviation'].mean()


def get_gas_price(date_str):
    target_date = pd.to_datetime(date_str)
    
    if target_date in daily_df.index:
        return daily_df.loc[target_date, 'prices']
    
    # Future extrapolation
    days_since = (target_date - daily_df.index.min()).days
    trend = intercept + slope * days_since
    seasonal = monthly_seasonality.get(target_date.month, 0)
    return trend + seasonal


# ====================== CONTRACT VALUATION ======================
def calculate_contract_pricing(inj_date, wth_date, inj_rate, wth_rate, 
                               max_vol, storage_cost_monthly):
    
    try:
        date_inj = pd.to_datetime(inj_date)
        date_wth = pd.to_datetime(wth_date)
        
        # Get realistic prices from model
        buy_price = get_gas_price(inj_date)
        sell_price = get_gas_price(wth_date)
        
        total_days = (date_wth - date_inj).days
        months_stored = total_days / 30.0
        
        # Operational constraints
        days_to_inject = max_vol / inj_rate
        days_to_withdraw = max_vol / wth_rate
        
        # Costs & Revenue
        gross_revenue = max_vol * sell_price
        gross_purchase = max_vol * buy_price
        total_storage_fee = months_stored * storage_cost_monthly
        
        net_value = gross_revenue - gross_purchase - total_storage_fee
        
        return {
            "net_value": net_value,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "months_stored": months_stored,
            "spread": sell_price - buy_price
        }
        
    except Exception as e:
        messagebox.showerror("Calculation Error", str(e))
        return None


# ====================== UI DASHBOARD ======================
def open_contract_dashboard():
    root = tk.Tk()
    root.title("J.P. Morgan Gas Storage Valuation Desk")
    root.geometry("580x780")
    root.resizable(False, False)

    # Default values
    defaults = {
        "inj_date": "2025-07-01",
        "wth_date": "2026-01-01",
        "max_vol": "1000000",
        "storage_cost": "10000",
        "inj_rate": "50000",
        "wth_rate": "50000"
    }

    # Create entries
    entries = {}
    labels = [
        ("Injection Date (YYYY-MM-DD):", "inj_date"),
        ("Withdrawal Date (YYYY-MM-DD):", "wth_date"),
        ("Max Volume (MMBtu):", "max_vol"),
        ("Monthly Storage Cost ($):", "storage_cost"),
        ("Injection Rate (MMBtu/day):", "inj_rate"),
        ("Withdrawal Rate (MMBtu/day):", "wth_rate")
    ]

    for i, (text, key) in enumerate(labels):
        tk.Label(root, text=text, font=("Arial", 10)).grid(
            row=i, column=0, padx=15, pady=10, sticky="w"
        )
        entry = tk.Entry(root, width=25, font=("Arial", 10))
        entry.insert(0, defaults[key])
        entry.grid(row=i, column=1, padx=15, pady=10)
        entries[key] = entry

    # Result display area
    result_text = tk.Text(root, height=10, width=60, font=("Consolas", 9))
    result_text.grid(row=len(labels)+1, column=0, columnspan=2, padx=15, pady=10)

    def on_calculate():
        try:
            result = calculate_contract_pricing(
                inj_date=entries["inj_date"].get(),
                wth_date=entries["wth_date"].get(),
                inj_rate=float(entries["inj_rate"].get()),
                wth_rate=float(entries["wth_rate"].get()),
                max_vol=float(entries["max_vol"].get()),
                storage_cost_monthly=float(entries["storage_cost"].get())
            )
            
            if result:
                output = f"""
=== CONTRACT VALUATION RESULT ===
Net Contract Value : ${result['net_value']:,.2f}

Buy Price  ({entries["inj_date"].get()}): ${result['buy_price']:.4f}
Sell Price ({entries["wth_date"].get()}): ${result['sell_price']:.4f}
Price Spread   : ${result['spread']:.4f}

Storage Duration : {result['months_stored']:.1f} months
Volume           : {float(entries["max_vol"].get()):,} MMBtu
                """
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, output)
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")

    # Calculate Button
    tk.Button(root, text="CALCULATE CONTRACT VALUE", 
              command=on_calculate,
              bg="#0066cc", fg="white", 
              font=("Arial", 11, "bold"), height=2).grid(
        row=len(labels), column=0, columnspan=2, pady=15, padx=15, sticky="ew"
    )

    root.mainloop()


# ====================== RUN ======================
if __name__ == "__main__":
    # Optional: Show quick test in console
    print("Starting Gas Storage Pricing Dashboard...\n")
    open_contract_dashboard()
