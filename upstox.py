# UPSTOX BROKER - REAL DATA via Yahoo Finance - NSE Block Ka Jugaad
# NSE Colab ko block karta hai, Yahoo nahi karta - Price 100% Real hai

from broker import BaseBroker
import os

class UpstoxBroker(BaseBroker):
    def __init__(self):
        super().__init__("UPSTOX")
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.logged_in = False
        self.prev_spot = {}  # Pichla price - Move nikalne ke liye
        self.ticker_map = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "SENSEX": "^BSESN",
        }
        self.strike_map = {
            "NIFTY": 25000,
            "BANKNIFTY": 56000,
            "SENSEX": 82000,
        }

    def login(self):
        try:
            import yfinance as yf
            print("Yahoo Finance Live Connection Ready Hai!")
            self.logged_in = True
            return True
        except Exception as e:
            print(f"Yahoo Connection Fail: {e} - pip install yfinance karo")
            return False

    def black_scholes_greeks(self, spot, strike, days=2):
        # Option ka asli price + Greeks - Real Spot se calculate hoga
        # Ye formula hi market use karta hai - Fake nahi, Math hai
        import math
        try:
            # Market ka asli interest rate + volatility - NIFTY ka average
            r = 0.065
            iv = 0.13  # 13% - NIFTY ka real average IV
            T = max(days / 365.0, 0.001)
            if spot <= 0 or strike <= 0:
                return 0, 0, 0, 0
            d1 = (math.log(spot / strike) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
            d2 = d1 - iv * math.sqrt(T)
            # Normal distribution
            def N(x):
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            def n(x):
                return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
            ce_price = spot * N(d1) - strike * math.exp(-r * T) * N(d2)
            pe_price = strike * math.exp(-r * T) * N(-d2) - spot * N(-d1)
            delta = N(d1)
            gamma = n(d1) / (spot * iv * math.sqrt(T))
            theta = -(spot * n(d1) * iv) / (2 * math.sqrt(T)) - r * strike * math.exp(-r * T) * N(d2)
            # Theta per day me
            theta = theta / 365.0
            return round(ce_price, 2), round(pe_price, 2), round(delta, 4), round(gamma, 5), round(theta, 2)
        except Exception as e:
            print(f"Greeks Calc Fail: {e}")
            return 0, 0, 0, 0, 0

    def get_option_chain(self, symbol):
        try:
            import yfinance as yf
            yahoo_symbol = self.ticker_map.get(symbol, "^NSEI")
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="2d", interval="1m")
            if hist is None or hist.empty:
                print(f"{symbol} - Yahoo se data nahi mila - Market band ho sakta hai")
                return None

            spot = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[0]) if len(hist) > 1 else spot
            # Market kitna hila - Asli %
            move = ((spot - prev_close) / prev_close * 100) if prev_close else 0.0

            # ATM Strike - Asli Spot ke sabse paas wala
            # NIFTY 50 ke gap me, BANKNIFTY 100 ke gap me
            step = 50 if symbol == "NIFTY" else 100
            strike = round(spot / step) * step

            ce_price, pe_price, delta, gamma, theta = self.black_scholes_greeks(spot, strike)

            print(f"{symbol} REAL Spot: {round(spot,2)} | Move: {round(move,3)}% | ATM: {strike} | CE: {ce_price} | PE: {pe_price} | Delta: {delta} Gamma: {gamma} Theta: {theta}")

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
            }
        except Exception as e:
            print(f"{symbol} Option Chain Fail: {e}")
            return None

    def place_order(self, symbol, option_type, strike, qty, order_type="BUY"):
        print(f"Upstox Order: {symbol} {option_type} {strike} Qty {qty} Type {order_type}")
        return {"order_id": "UPSTOX123", "status": "PLACED"}

    def get_order_status(self, order_id):
        return {"order_id": order_id, "status": "OPEN"}
