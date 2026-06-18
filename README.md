# J.P. Morgan Quantitative Research – Commodity Storage Contract Pricing Engine 📊

This repository contains my production-grade pricing engine built for the **J.P. Morgan Quantitative Research** track simulation on Forage (Task 2). The application evaluates natural gas storage contracts by calculating net asset cash flows against forecasted pricing baselines and operational overhead constraints.

## 🧮 The Financial Valuation Model
The engine determines fair contract valuation via a physical arbitrage framework:
$$\text{Contract Value} = \text{Gross Sales Revenue} - \text{Gross Purchase Costs} - \text{Fixed Storage Costs} - \text{Operational/Transit Fees}$$

## 🚀 Key Features
- **Time-Series Pricing Feed:** Feeds dynamic, seasonally adjusted natural gas price estimates straight from our Task 1 linear regression forecasting model.
- **Multi-Date Processing Logic:** Built a modular cash-flow calculation loop using Python's `zip` iterator to seamlessly process multiple matching injection/withdrawal transaction windows.
- **Full-Stack Desktop GUI:** Developed an interactive desktop trading dashboard using Tkinter. It allows trading desks to input changing storage rates, transit fees, and processing charges to run quick real-time contract simulations.

## 🛠️ Tech Stack
- **Language:** Python 3
- **Libraries:** Pandas, NumPy, SciPy, Matplotlib, Tkinter
