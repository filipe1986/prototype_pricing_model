import pandas as pd
import tkinter as tk
from tkinter import messagebox
from scipy.stats import linregress

# ====================== DATA & FORECAST ======================
df = pd.read_csv('nat_gas.csv')
df.columns = df.columns.str.lower()
df['dates'] = pd.to_datetime(df['dates'], errors='coerce')
df.set_index('dates', inplace=True)

daily_df = df.resample('D').interpolate(method='linear')
daily_df['days_since_start'] = (daily_df.index - daily_df.index.min()).days

slope, intercept, _, _, _ = linregress(daily_df['days_since_start'], daily_df['prices'])

daily_df['trend_price'] = intercept + slope * daily_df['days_since_start']
daily_df['deviation'] = daily_df['prices'] - daily_df['trend_price']
daily_df['month'] = daily_df.index.month
monthly_seasonality = daily_df.groupby('month')['deviation'].mean()


def get_gas_price(date_str):
    target_date = pd.to_datetime(date_str, errors='coerce')
    if pd.isna(target_date):
        messagebox.showerror("Date Error", "Invalid date format!")
        return None
    
    if target_date in daily_df.index:
        return daily_df.loc[target_date, 'prices']
    
    days_since = (target_date - daily_df.index.min()).days
    trend = intercept + slope * days_since
    seasonal = monthly_seasonality.get(target_date.month, 0)
    return trend + seasonal


# ====================== CALCULATION ======================
def calculate_contract_pricing(inj_date, wth_date, max_vol, storage_cost_monthly, inj_rate, wth_rate):
    try:
        buy_price = get_gas_price(inj_date)
        sell_price = get_gas_price(wth_date)
        
        if buy_price is None or sell_price is None:
            return None
            
        date_inj = pd.to_datetime(inj_date)
        date_wth = pd.to_datetime(wth_date)
        
        total_days = (date_wth - date_inj).days
        months_stored = max(total_days / 30.0, 0)
        
        gross_revenue = max_vol * sell_price
        gross_purchase = max_vol * buy_price
        total_storage_fee = months_stored * storage_cost_monthly
        
        net_value = gross_revenue - gross_purchase - total_storage_fee
        spread = sell_price - buy_price
        break_even_price = (gross_purchase + total_storage_fee) / max_vol if max_vol > 0 else 0
        
        return {
            "net_value": net_value,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "spread": spread,
            "months_stored": months_stored,
            "break_even_price": break_even_price
        }
    except Exception as e:
        messagebox.showerror("Calculation Error", f"Error: {str(e)}")
        return None


# ====================== UI ======================
def open_contract_dashboard():
    root = tk.Tk()
    root.title("J.P. Morgan Gas Storage Valuation Desk")
    root.geometry("650x580")
    root.resizable(False, False)

    defaults = {
        "inj_date": "2025-07-01",
        "wth_date": "2025-12-01",
        "max_vol": "1000000",
        "storage_cost": "10000",
        "inj_rate": "50000",
        "wth_rate": "50000"
    }

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
        tk.Label(root, text=text, font=("Arial", 10)).grid(row=i, column=0, padx=15, pady=8, sticky="w")
        entry = tk.Entry(root, width=28, font=("Arial", 10))
        entry.insert(0, defaults[key])
        entry.grid(row=i, column=1, padx=15, pady=8)
        entries[key] = entry

    result_text = tk.Text(root, height=16, width=72, font=("Consolas", 10))
    result_text.grid(row=len(labels)+1, column=0, columnspan=2, padx=15, pady=12)

    def on_calculate():
        result = calculate_contract_pricing(
            entries["inj_date"].get(),
            entries["wth_date"].get(),
            float(entries["max_vol"].get()),
            float(entries["storage_cost"].get()),
            float(entries["inj_rate"].get()),
            float(entries["wth_rate"].get())
        )
        
        if not result:
            return

        net = result['net_value']
        color = "green" if net >= 0 else "red"
        
        output = f"""
=== CONTRACT VALUATION RESULT ===
Net Contract Value : ${net:,.2f}

Buy Price  ({entries["inj_date"].get()}): ${result['buy_price']:.4f}
Sell Price ({entries["wth_date"].get()}): ${result['sell_price']:.4f}
Price Spread       : ${result['spread']:.4f}

Storage Duration   : {result['months_stored']:.1f} months
Volume             : {float(entries["max_vol"].get()):,} MMBtu
Break-even Sell Price : ${result['break_even_price']:.4f}
"""

        if net < 0:
            output += "\n⚠️  WARNING: This contract is currently unprofitable!\n"
            output += "   Consider different dates or shorter storage period.\n"

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, output)
        result_text.config(fg=color)

    tk.Button(root, text="CALCULATE CONTRACT VALUE", 
              command=on_calculate,
              bg="#0066cc", fg="white", 
              font=("Arial", 11, "bold"), height=2).grid(
        row=len(labels), column=0, columnspan=2, pady=12, padx=15, sticky="ew"
    )

    root.mainloop()


if __name__ == "__main__":
    open_contract_dashboard()
    