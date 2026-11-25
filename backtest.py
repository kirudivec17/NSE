# BACKTEST - Pichle 30 Din Ka Asli Data - Strategy Test
# Market Band Hai Toh Bhi Chalega - Kyuki Purana Data Use Karega

import yfinance as yf
import math

CAPITAL = 10000
QTY = 25

def black_scholes_price(spot, strike, days=2):
    r = 0.065
    iv = 0.13
    T = max(days / 365.0, 0.001)
    if spot <= 0 or strike <= 0:
        return 0, 0
    d1 = (math.log(spot / strike) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
    d2 = d1 - iv * math.sqrt(T)
    def N(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    ce = spot * N(d1) - strike * math.exp(-r * T) * N(d2)
    pe = strike * math.exp(-r * T) * N(-d2) - spot * N(-d1)
    return round(ce, 2), round(pe, 2)

def get_greeks(spot, strike, days=2):
    r = 0.065
    iv = 0.13
    T = max(days / 365.0, 0.001)
    d1 = (math.log(spot / strike) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
    d2 = d1 - iv * math.sqrt(T)
    def N(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    def n(x):
        return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
    delta = N(d1)
    gamma = n(d1) / (spot * iv * math.sqrt(T))
    theta = (-(spot * n(d1) * iv) / (2 * math.sqrt(T)) - r * strike * math.exp(-r * T) * N(d2)) / 365.0
    return delta, gamma, theta

def strategy_signal(move, delta, gamma, theta):
    # Wahi Strategy - Jo main.py me hai
    if abs(move) > 0.3:
        return "BUY_CE" if move > 0 else "BUY_PE", "MODE 1 - DELTA"
    if gamma > 0.001:
        return ("BUY_CE", "MODE 2 - GAMMA") if move >= 0 else ("BUY_PE", "MODE 2 - GAMMA")
    return "SELL_CE", "MODE 3 - THETA"

def backtest_symbol(symbol, yahoo_symbol):
    print(f"\n========== {symbol} BACKTEST - Pichle 30 Din ==========")
    ticker = yf.Ticker(yahoo_symbol)
    hist = ticker.history(period="1mo", interval="1d")
    if hist.empty:
        print(f"{symbol} - Data nahi mila")
        return 0, 0, 0

    balance = CAPITAL
    wins = 0
    losses = 0
    total_trades = 0

    # Har din - Subah Open pe Entry, Shaam Close pe Exit - Asli Price Pe
    for i in range(len(hist) - 1):
        today = hist.iloc[i]
        tomorrow = hist.iloc[i + 1]
        open_price = float(today["Open"])
        close_price = float(today["Close"])
        prev_close = float(hist.iloc[i-1]["Close"]) if i > 0 else open_price

        # Aaj ka Move - Open se Close tak
        move = ((close_price - open_price) / open_price * 100) if open_price else 0

        step = 50 if symbol == "NIFTY" else 100
        strike = round(open_price / step) * step
        ce_price, pe_price = black_scholes_price(open_price, strike)
        delta, gamma, theta = get_greeks(open_price, strike)

        signal, mode = strategy_signal(move, delta, gamma, theta)

        # Entry price - Subah Open wale Spot se
        entry = ce_price if "CE" in signal else pe_price
        # Exit price - Shaam Close wale Spot se - Asli
        ce_exit, pe_exit = black_scholes_price(close_price, strike)
        exit_price = ce_exit if "CE" in signal else pe_exit

        if signal.startswith("BUY"):
            pnl = (exit_price - entry) * QTY
        else:
            pnl = (entry - exit_price) * QTY

        balance += pnl
        total_trades += 1
        if pnl > 0:
            wins += 1
        else:
            losses += 1

        date = hist.index[i].strftime("%d-%m-%Y")
        print(f"{date} | Move {round(move,2)}% | {mode} | {signal} Entry {entry} Exit {exit_price} | PnL {round(pnl,2)} | Bal {round(balance,2)}")

    print(f"--- {symbol} RESULT ---")
    print(f"Total Trades: {total_trades} | Win: {wins} | Loss: {losses} | Win Rate: {round(wins/total_trades*100,1) if total_trades else 0}%")
    print(f"Final Balance: {round(balance,2)} | Total PnL: {round(balance-CAPITAL,2)}")
    return balance, wins, total_trades

if __name__ == "__main__":
    print("=== BACKTEST START - Pichle 30 Din Ka Asli Data ===")
    print("Capital Har Symbol Ke Liye Alag 10000 - Taaki Pata Chale Kaun Sa Symbol Best Hai")
    backtest_symbol("NIFTY", "^NSEI")
    backtest_symbol("BANKNIFTY", "^NSEBANK")
    backtest_symbol("SENSEX", "^BSESN")
    print("\n=== BACKTEST KHATAM ===")
    print("Agar 3 Me Se 2 Me Loss Hai Toh Strategy Me Change Karna Padega - Kal Subah Live Chalane Se Pehle!")
