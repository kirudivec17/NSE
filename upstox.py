# UPSTOX BROKER - REAL DATA via Yahoo - Market Band Ho Toh NO TRADE

from broker import BaseBroker
import os

class UpstoxBroker(BaseBroker):
    def __init__(self):
        super().__init__("UPSTOX")
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.logged_in = False
        self.ticker_map = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "SENSEX": "^BSESN",
        }

    def login(self):
        try:
            import yfinance as yf
            print("Yahoo Finance Live Connection Ready Hai!")
            self.logged_in = True
            return True
        except Exception as e:
            print(f"Yahoo Connection Fail: {e}")
            return False

    def black_scholes_greeks(self, spot, strike, days=2):
        import math
        try:
            r = 0.065
            iv = 0.13
            T = max(days / 365.0, 0.001)
            if spot <= 0 or strike <= 0:
                return 0, 0, 0, 0, 0
            d1 = (math.log(spot / strike) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
            d2 = d1 - iv * math.sqrt(T)
            def N(x):
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            def n(x):
                return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
            ce_price = spot * N(d1) - strike * math.exp(-r * T) * N(d2)
            pe_price = strike * math.exp(-r * T) * N(-d2) - spot * N(-d1)
            delta = N(d1)
            gamma = n(d1) / (spot * iv * math.sqrt(T))
            theta = (-(spot * n(d1) * iv) / (2 * math.sqrt(T)) - r * strike * math.exp(-r * T) * N(d2)) / 365.0
            return round(ce_price, 2), round(pe_price, 2), round(delta, 4), round(gamma, 5), round(theta, 2)
        except Exception:
            return 0, 0, 0, 0, 0

    def get_option_chain(self, symbol):
        try:
            import yfinance as yf
            from datetime import datetime
            yahoo_symbol = self.ticker_map.get(symbol, "^NSEI")
            ticker = yf.Ticker(yahoo_symbol)

            # AAJ ka hi data lo - 1 din ka
            hist = ticker.history(period="1d", interval="1m")
            if hist is None or hist.empty:
                print(f"{symbol} - Aaj ka data nahi mila - Market band hai")
                return None

            spot = float(hist["Close"].iloc[-1])
            # AAJ ka open - Aaj ka sahi Move
            today_open = float(hist["Open"].iloc[0])
            move = ((spot - today_open) / today_open * 100) if today_open else 0.0

            # Market band hai kya? - Aakhri candle kitni purani hai?
            last_time = hist.index[-1]
            now = datetime.now(last_time.tzinfo) if last_time.tzinfo else datetime.now()
            diff_min = (now - last_time).total_seconds() / 60
            # Agar 15 min se koi naya candle nahi aaya to market band samjho
            is_market_open = diff_min < 15
            # Subah 9:15 se 3:30 ke beech hi market khula hota hai
            # Raat me ye False hoga

            step = 50 if symbol == "NIFTY" else 100
            strike = round(spot / step) * step
            ce_price, pe_price, delta, gamma, theta = self.black_scholes_greeks(spot, strike)

            print(f"{symbol} REAL Spot: {round(spot,2)} | Aaj Move: {round(move,3)}% | ATM: {strike} | CE: {ce_price} | PE: {pe_price} | Market Open: {is_market_open}")

            return {
                "symbol": symbol,
                "broker": "UPSTOX",
                "status": "REAL-YAHOO",
                "spot": spot,
                "strike": strike,
                "ce_price": ce_price,
                "pe_price": pe_price,
                "move": move,
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "market_open": is_market_open,
            }
        except Exception as e:
            print(f"{symbol} Option Chain Fail: {e}")
            return None

    def place_order(self, symbol, option_type, strike, qty, order_type="BUY"):
        print(f"Upstox Order: {symbol} {option_type} {strike} Qty {qty} Type {order_type}")
        return {"order_id": "UPSTOX123", "status": "PLACED"}

    def get_order_status(self, order_id):
        return {"order_id": order_id, "status": "OPEN"}
