import streamlit as st
import pandas as pd
from scipy.stats import linregress
import plotly.express as px
from datetime import datetime

# page config
st.set_page_config(
    page_title="J.P. Morgan Gas Storage Tool",
    page_icon="🛢️",
    layout="wide"
)

st.title("🛢️ J.P. Morgan - Natural Gas Storage Valuation Desk")
st.markdown("**Prototype for Natural Gas Storage Contract Valuation**")

# load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('nat_gas.csv')
    df.columns = df.columns.str.lower()
    df['dates'] = pd.to_datetime(df["dates"])
    df.set_index('dates', inplace=True)

    daily_df = df.resample('D').interpolate(method='linear')
    daily_df['days_since_start'] = (daily_df.index - daily_df.index.min()).days

    slope, intercept, _, _, _ = linregress(daily_df['days_since_start'], daily_df['prices'])

    daily_df['trend_price'] = intercept + slope * daily_df['days_since_start']
    daily_df['deviation'] = daily_df['prices'] - daily_df['trend_price']
    daily_df['month'] = daily_df.index.month
    monthly_seasonality = daily_df.groupby('month')['deviation'].mean()

    return daily_df, slope, intercept, monthly_seasonality

daily_df, slope, intercept, monthly_seasonality = load_data()

def get_gas_price(date_str):
    target_date = pd.to_datetime(date_str)
    if target_date in daily_df.index:
        return daily_df.loc[target_date, 'prices']
    
    days_since = (target_date - daily_df.index.min()).days
    trend = intercept + slope * days_since
    seasonal = monthly_seasonality.get(target_date.month, 0)
    return trend * seasonal

# calc
def calculate_contract(inj_date, wth_date, max_vol, storage_cost_monthly):
    buy_price = get_gas_price(inj_date)
    sell_price = get_gas_price(wth_date)

    days = (pd.to_datetime(wth_date) - pd.to_datetime(inj_date)).days
    months_stored = days / 30.0

    gross_revenue = max_vol * sell_price
    gross_purchase = max_vol * buy_price
    storage_cost = months_stored * storage_cost_monthly

    net_value = gross_revenue - gross_purchase - storage_cost
    spread = sell_price - buy_price

    return {
        "net_value": net_value,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "spread": spread,
        "months_stored": months_stored
    }

# sidebar
st.sidebar.header("Contract Parameters")

col1, col2 = st.sidebar.columns(2)
with col1:
    inj_date = st.date_input("Injection Date", value=datetime(2025, 7, 1))
with col2:
    wth_date = st.date_input('Withdrawal Date', value=datetime(2025, 12, 1))

volume = st.sidebar.number_input("Volume (MMBtu)", value=1_000_000, step=50_000)
storage_cost = st.sidebar.number_input("Monthly Storage Cost ($)", value=10_000, step=1_000)

# main
if st.button("Calculate Contract Value", type="primary", use_container_width=True):
    result = calculate_contract(str(inj_date), str(wth_date), volume, storage_cost)

    col1, col2, col3 = st.columns(3)
    with(col1):
        st.metric("Net Contract Value", f"${result['net_value']:,.2f}", delta=f"${result['spread']:.4f} spread")

    with col2:
        st.metric("Buy Price", f"${result['buy_price']:.4f}")
    with col3:
        st.metric("Sell Price", f"${result['sell_price']:.4f}")
    
    if result['net_value'] >= 0:
        st.success("✅ Profitable Contract!")
    else:
        st.error("⚠️ Unprofitable Contract.")

# show price forecast chart
if st.checkbox("Show Price Forecast Chart"):
    future_dates = pd.date_range(start='2025-01-01', end='2026-12-31', freq='D')
    future_prices = [get_gas_price(str(d.date())) for d in future_dates]

    fig = px.line(x=future_dates, y=future_prices, title="Natural Gas Price Forecast")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Prototype by Filipe Vieira | built with Streamlit")


