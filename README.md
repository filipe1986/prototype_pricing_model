# J.P. Morgan - Natural Gas Storage Pricing Tool

A desktop application to value natural gas storage contracts using historical data and seasonality forecasting.

![Natural Gas Storage Valuation Tool](images/pricing_model_ui.png)

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

Make sure nat_gas.csv is in the project folder
Run the application:bash

python main.py

Tech StackPython 3
Pandas, SciPy, Tkinter

# J.P. Morgan Natural Gas Storage Valuation Tool

A web application to value natural gas storage contracts using historical data and seasonality forecasting.

![Demo](https://github.com/filipe1986/prototype_pricing_model/blob/main/preview.png)

## Features
- Interactive price forecasting with trend + seasonality
- Real-time contract valuation
- Profitability analysis with color indicators
- Built with Streamlit (easy to use in browser)

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py

Live Demo
Will be added after deployment on Render

Tech Stack
- Python 3
- Streamlit
- Pandas and Scipy
- Plotly

Deployed on Render
This app is ready to be deployed on Render (free tier).
