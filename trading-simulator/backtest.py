import pandas as pd, numpy as np, yfinance as yf, sqlite3, matplotlib.pyplot as plt
from dataclasses import dataclass

# ---- Config ----
TICKER = "NVDA"          # try AAPL, MSFT, TSLA, QQQ, etc.
START  = "2010-01-01"
FAST, SLOW = 50, 200     # short/long SMA windows (days)
COST = 0.001            # 0.1% per position change
TABLE = f"backtest_{TICKER.lower()}_{FAST}_{SLOW}"
# -----------------

@dataclass
class Perf:
    final_equity: float; cagr: float; sharpe: float; max_dd: float; max_dd_days: int

def download_prices(ticker=TICKER, start=START):
    """FORMAL: Pull daily OHLCV, adjusted; compute simple returns r_t = P_t/P_{t-1} - 1.
       EASY: Get daily prices and how much they changed."""
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False).dropna()
    if df.empty: raise ValueError("No data. Check ticker or internet.")
    df["ret"] = df["Close"].pct_change()
    return df

def sma_crossover_signals(df, fast=FAST, slow=SLOW):
    """FORMAL: Signal_t = 1{SMA_fast > SMA_slow}; enforce next-bar execution.
       EASY: If short avg > long avg, be IN; actually act tomorrow."""
    out = df.copy()
    out[f"sma_{fast}"] = out["Close"].rolling(fast, min_periods=fast).mean()
    out[f"sma_{slow}"] = out["Close"].rolling(slow, min_periods=slow).mean()
    out["signal"] = (out[f"sma_{fast}"] > out[f"sma_{slow}"]).astype(int)
    out["position"] = out["signal"].shift(1).fillna(0)  # no look-ahead
    return out

def apply_transaction_costs(pos: pd.Series, rate: float) -> pd.Series:
    """Charge cost when the position changes (enter/exit)."""
    trades = pos.diff().abs().fillna(pos.abs())
    return trades * rate

def equity_and_perf(df, cost_rate=COST):
    strat_ret_raw = df["position"] * df["ret"]
    costs = apply_transaction_costs(df["position"], cost_rate)
    strat_ret = strat_ret_raw - costs

    eq_s  = (1 + strat_ret.fillna(0)).cumprod()
    eq_bh = (1 + df["ret"].fillna(0)).cumprod()

    daily = strat_ret.dropna()
    final_eq = float(eq_s.iloc[-1])

    n = len(daily); cagr = np.nan
    if n > 252: cagr = final_eq ** (252 / n) - 1          # ~annualize

    mu, sigma = daily.mean(), daily.std(ddof=1)
    sharpe = (mu / sigma) * np.sqrt(252) if sigma > 0 else np.nan

    roll_max = eq_s.cummax()
    dd = (eq_s / roll_max) - 1.0
    max_dd = float(dd.min())

    underwater = dd < 0
    max_dd_days = cur = 0
    for flag in underwater:
        cur = cur + 1 if flag else 0
        if cur > max_dd_days: max_dd_days = cur

    return eq_s, eq_bh, strat_ret, costs, Perf(final_eq, cagr, sharpe, max_dd, max_dd_days)

def save_sqlite(df, path="trades.db", table=TABLE):
    conn = sqlite3.connect(path)
    out = df[["Close","ret","signal","position"]].copy()
    out["date"] = out.index.astype(str)
    out.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()

def plot_equity(eq_s, eq_bh, path="equity.png"):
    import yfinance as yf

    # fetch company name dynamically
    ticker_obj = yf.Ticker(TICKER)
    company_name = ticker_obj.info.get("longName", TICKER)

    plt.figure()
    plt.plot(eq_s, label=f"Strategy (SMA {FAST}/{SLOW})")
    plt.plot(eq_bh, label="Buy & Hold")
    plt.title("SMA Crossover vs Buy & Hold")
    plt.title(f"{company_name} ({TICKER}) SMA Crossover vs Buy & Hold")
    plt.xlabel("Date"); plt.ylabel("Equity (Start=1.0)")
    plt.legend(); plt.tight_layout(); plt.savefig(path); plt.close()

def main():
    print(f"Ticker={TICKER} Start={START} Fast={FAST} Slow={SLOW} Cost={COST:.3%}")
    df = download_prices(); df = sma_crossover_signals(df, FAST, SLOW)
    eq_s, eq_bh, strat_ret, costs, perf = equity_and_perf(df, COST)
    save_sqlite(df, "trades.db", TABLE); plot_equity(eq_s, eq_bh, "equity.png")

    print("\n=== Results ===")
    print(f"Final equity: {perf.final_equity:.3f}")
    if not np.isnan(perf.cagr):   print(f"CAGR: {perf.cagr:.2%}")
    if not np.isnan(perf.sharpe): print(f"Sharpe (ann.): {perf.sharpe:.2f}")
    print(f"Max drawdown: {perf.max_dd:.2%} (duration: {perf.max_dd_days} bars)")
    print("Files → equity.png  |  trades.db (table:", TABLE, ")")

if __name__ == "__main__":
    main()
