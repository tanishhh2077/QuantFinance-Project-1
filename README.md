# 📈 Algorithmic Trading Simulator (SMA Crossover)

A Python-based backtesting tool that implements a **20/50-day Simple Moving Average (SMA) crossover strategy**.  
It fetches historical stock data via Yahoo Finance, executes trades with **next-day discipline** to avoid look-ahead bias, logs results into SQLite, and generates equity curve plots comparing the strategy against a Buy & Hold benchmark.  

---



## 📊 Example Output

Running the backtest on **SPY (S&P 500 ETF)** produces:

- `equity.png` → Equity curve of strategy vs Buy & Hold  
- `trades.db` → SQLite database log of trades  

Example equity curve output:

![Equity Curve](equity.png)

---

## 🔧 Features
- 📊 Historical stock data retrieval with **yFinance**
- 📉 Implements **short-term vs long-term SMA crossover** strategy
- 🗄️ Logs trades and returns into **SQLite database** for reproducibility
- 📈 Plots equity curve vs Buy & Hold benchmark using **matplotlib**
- ✅ Avoids look-ahead bias by executing trades **next day**

---

## 🛠️ Tech Stack
- **Python 3.11**
- **pandas**, **NumPy**
- **yFinance**
- **matplotlib**
- **SQLite**

---

## 🚀 Quickstart

Clone the repository and set up your environment:

```bash
git clone https://github.com/USERNAME/trading-simulator.git
cd trading-simulator

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

Run the backtest:
python backtest.py






