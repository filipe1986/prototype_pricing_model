# J.P. Morgan - Natural Gas Storage Pricing Tool

A desktop application to value natural gas storage contracts using historical data and seasonality forecasting.

![Natural Gas Storage Valuation Tool](images/app_screenshot.png)

## Overview
This tool calculates the **net value** of gas storage contracts by comparing purchase and sale prices (with seasonality), storage costs, and operational constraints.

## Features
- Interactive Tkinter GUI
- Price forecasting with linear trend + monthly seasonality
- Real-time contract valuation
- Profitability warnings (red/green) and break-even analysis
- Supports different injection/withdrawal dates and volumes

## How to Run
1. Install dependencies:
   ```bash
   pip install pandas scipy matplotlib
2 Make sure nat_gas.csv is in the project folder
3. Run the application: 
bash
python main.py
##Tech Stack
- Python 3
- Pandas, SciPy, Tkinter
