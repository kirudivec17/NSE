# UPSTOX BROKER - AB KOI FAKE DATA NAHI - SIRF REAL NSE DATA

from broker import BaseBroker
import os
import requests

class UpstoxBroker(BaseBroker):
    def __init__(self):
        super().__init__("UPSTOX")
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.api_secret = os.getenv("UPSTOX_API_SECRET")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.logged_in = False
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        })

    def login(self):
        # PAPER MODE me login ki zarurat nahi, lekin REAL data ke liye NSE session chahiye
        try:
            # NSE se session cookie lo - bina iske data nahi milega
            self.session.get("https://www.nseindia.com", timeout=10)
            print("NSE Live Connection Ready Hai!")
            self.logged_in = True
            return True
        except Exception as e:
            print(f"NSE Connection Fail: {e}")
            return False

    def get_live_price(self, symbol):
        # Asli Live Price - NSE se
        try:
            # NIFTY / BANKNIFTY / SENSEX ka asli spot price
            nse_symbol = symbol
            if symbol == "SENSEX":
                # SENSEX NSE pe nahi hai, isliye NIFTY jaisa hi treat karo test me
                # Asli me yaha BSE API lagega
                return None

            url = f"https://www.nseindia.com/api/quote-derivative?symbol={nse_symbol}"
            r = self.session.get(url, timeout=10)
            data = r.json()
            # Underlying ka asli price
            price = data.get("underlyingValue")
            return float(price) if price else None
        except Exception as e:
            print(f"{symbol} Live Price Nahi Mila: {e}")
            return None

    def get_option_chain(self, symbol):
        # Asli Option Chain - Greeks ke saath - NSE se
        try:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            r = self.session.get(url, timeout=10)
            data = r.json()
            records = data.get("records", {}).get("data", [])
            spot = data.get("records", {}).get("underlyingValue", 0)

            if not records or not spot:
                print(f"{symbol} - Asli Data Nahi Mila - Trade Nahi Karenge")
                return None

            # ATM ke sabse paas wala strike dhoondo
            atm = min(records, key=lambda x: abs(x.get("strikePrice", 0) - spot))
            ce = atm.get("CE", {})
            pe = atm.get("PE", {})

            # Asli Greeks
            ce_greeks = ce.get("greeks", {})
            # Market kitna hila - pichle close se
            # NSE se change nikalte hai
            print(f"{symbol} REAL Spot: {spot} | ATM Strike: {atm.get('strikePrice')} | CE LTP: {ce.get('lastPrice')} | PE LTP: {pe.get('lastPrice')}")

            return {
                "symbol": symbol,
                "broker": "UPSTOX",
                "status": "REAL",
                "spot": spot,
                "strike": atm.get("strikePrice"),
                "ce_price": ce.get("lastPrice", 0),
                "pe_price": pe.get("lastPrice", 0),
                "move": 0.0,  # Abhi spot change se calculate karenge - neeche main.py me
                "delta": ce_greeks.get("delta", 0),
                "gamma": ce_greeks.get("gamma", 0),
                "theta": ce_greeks.get("theta", 0),
                "ce_greeks": ce_greeks,
                "pe_greeks": pe.get("greeks", {}),
            }
        except Exception as e:
            print(f"{symbol} Option Chain Fail: {e}")
            return None

    def place_order(self, symbol, option_type, strike, qty, order_type="BUY"):
        print(f"Upstox Order: {symbol} {option_type} {strike} Qty {qty} Type {order_type}")
        return {"order_id": "UPSTOX123", "status": "PLACED"}

    def get_order_status(self, order_id):
        return {"order_id": order_id, "status": "OPEN"}
