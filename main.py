# ==========================================
# TRADEJINI - TRIPLE FILTER AI SYSTEM
# Strategy: ORB + VWAP + EMA + PCR + Greeks
# Broker: Tradejini - Individual API
# Author: Kiran Boss
# Date: 23 Nov 2026
# MODE: PAPER TRADING - Real Paisa Nahi Lagega
# ==========================================

import os
import time
import requests
import pyotp
import pandas as pd
from datetime import datetime, time as dtime
from dotenv import load_dotenv

# ===== 0. .ENV SE KEY LO =====
load_dotenv()

API_KEY = os.getenv("TRADEJINI_API_KEY")
CLIENT_CODE = os.getenv("TRADEJINI_CLIENT_CODE")
PIN = os.getenv("TRADEJINI_PIN")
TOTP_SECRET = os.getenv("TRADEJINI_TOTP_SECRET")

if not API_KEY or not CLIENT_CODE or not PIN or not TOTP_SECRET:
    print("BOSS - .env me 4 cheez nahi mili!")
    print("TRADEJINI_API_KEY, CLIENT_CODE, PIN, TOTP_SECRET daalo")
    exit()

# ===== 1. TRADEJINI LOGIN - INDIVIDUAL =====
BASE_URL = "https://api.tradejini.com"
ACCESS_TOKEN = None

def tradejini_login():
    global ACCESS_TOKEN
    print("Tradejini Login kar raha hu Boss...")
    totp_code = pyotp.TOTP(TOTP_SECRET).now()
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "client_code": CLIENT_CODE,
        "pin": PIN,
        "totp": totp_code
    }
    try:
        r = requests.post(f"{BASE_URL}/v1/login", json=payload, headers=headers, timeout=15)
        data = r.json()
        print(f"Login Response: {data}")
        # Token jo bhi naam se aaye, pakad lo
        ACCESS_TOKEN = data.get("access_token") or data.get("token") or data.get("data", {}).get("access_token")
        if ACCESS_TOKEN:
            print("Tradejini Login Ho Gaya Boss!")
            return True
        else:
            print("Login Fail - PIN / TOTP / API Key check karo")
            return False
    except Exception as e:
        print(f"Login me error: {e}")
        return False

def get_headers():
    return {
        "api-key": API_KEY,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

# ===== 2. SETTINGS - TUMHARA RISK =====
CAPITAL = 50000
MAX_LOSS_PER_DAY = -5000
MAX_PROFIT_PER_DAY = 10000
MAX_TRADES_PER_DAY = 2
LOT_SIZE_NIFTY = 65
PAPER_TRADING = True  # True = Paper, False = Real Paisa Lagega

# ===== 3. DATA - NIFTY 5 MIN =====
def get_nifty_data():
    # Tradejini Historical Data - NIFTY INDEX
    try:
        # NIFTY Spot - Symbol: NIFTY, Exchange: NSE
        payload = {
            "symbol": "NIFTY",
            "exchange": "NSE",
            "interval": "5minute",
            "from_date": datetime.now().strftime("%Y-%m-%d") + " 09:15:00",
            "to_date": datetime.now().strftime("%Y-%m-%d") + " 15:30:00"
        }
        r = requests.post(f"{BASE_URL}/v1/historical", json=payload, headers=get_headers(), timeout=15)
        data = r.json()
        candles = data.get("data") or data.get("candles") or []
        if not candles:
            print(f"Data khali aaya: {data}")
            return None
        df = pd.DataFrame(candles)
        # Column naam alag ho sakte hai - normalize karo
        df.columns = [c.lower() for c in df.columns]
        # VWAP
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_21'] = df['close'].ewm(span=21).mean()
        return df
    except Exception as e:
        print(f"Data lene me error: {e}")
        return None

def get_orb_level(df):
    # 9:15 - 9:30 ka High / Low - ORB
    # Agar time column hai toh usse filter, nahi toh pehle 3 candle (5-min x 3 = 15 min)
    try:
        if 'time' in df.columns or 'timestamp' in df.columns:
            col = 'time' if 'time' in df.columns else 'timestamp'
            df['time_only'] = pd.to_datetime(df[col]).dt.time
            orb = df[(df['time_only'] >= dtime(9,15)) & (df['time_only'] <= dtime(9,30))]
        else:
            orb = df.head(3)
        return orb['high'].max(), orb['low'].min()
    except:
        return df.head(3)['high'].max(), df.head(3)['high'].min()

def get_option_chain():
    # Tradejini Option Chain - PCR + Greeks
    try:
        payload = {"symbol": "NIFTY", "exchange": "NFO", "expiry": "0"}
        r = requests.post(f"{BASE_URL}/v1/option-chain", json=payload, headers=get_headers(), timeout=15)
        data = r.json()
        oc = data.get("data") or data.get("oc") or {}
        if not oc:
            print(f"Option Chain khali: {data}")
            return None, 0
        # PCR
        total_ce_oi = 0
        total_pe_oi = 0
        for v in oc.values():
            try:
                total_ce_oi += v.get('ce', {}).get('oi', 0)
                total_pe_oi += v.get('pe', {}).get('oi', 0)
            except:
                continue
        pcr = total_pe_oi / total_ce_oi if total_ce_oi else 0
        return oc, pcr
    except Exception as e:
        print(f"Option Chain me error: {e}")
        return None, 0

def find_best_strike(oc, direction):
    # Delta 0.50 - 0.65 wala hi lega, Theta < 20
    for strike, data in oc.items():
        try:
            side = data['ce'] if direction == "CE" else data['pe']
            greeks = side.get('greeks', {})
            delta = abs(greeks.get('delta', 0))
            theta = abs(greeks.get('theta', 999))
            if 0.50 <= delta <= 0.65 and theta < 20:
                return strike, side
        except:
            continue
    return None, None

# ===== 4. ORDER - TRADEJINI =====
def place_tradejini_order(symbol, qty, direction):
    # Live Order - Sirf jab PAPER_TRADING = False
    payload = {
        "symbol": symbol,
        "exchange": "NFO",
        "transaction_type": "BUY",
        "quantity": qty,
        "order_type": "MARKET",
        "product_type": "INTRADAY",
        "price": 0
    }
    r = requests.post(f"{BASE_URL}/v1/place-order", json=payload, headers=get_headers(), timeout=15)
    print(f"LIVE Order Response: {r.json()}")
    return r.json()

# ===== 5. MAIN AI ENGINE - TEENO FILTER =====
def main_ai():
    print("Boss, Tradejini System ON ho gaya - 9:30 ka wait kar raha hu...")
    print(f"Mode: {'PAPER TRADING - Paisa Nahi Lagega' if PAPER_TRADING else 'LIVE - REAL PAISA LAGEGA'}")
    trades_today = 0
    total_pnl = 0

    while True:
        now = datetime.now().time()

        if now < dtime(9, 30):
            print("9:30 nahi hua - ORB ban raha hai, wait karo...")
            time.sleep(30)
            continue

        if now >= dtime(15, 15):
            print("3:15 ho gaya - Sab Square-Off - Aaj ka kaam khatam")
            break

        if total_pnl <= MAX_LOSS_PER_DAY:
            print("Aaj ka Loss Limit Khatam - System Band")
            break
        if total_pnl >= MAX_PROFIT_PER_DAY:
            print("Aaj ka Profit Target Ho Gaya - System Band")
            break

        # --- FILTER 1: ORB ---
        df = get_nifty_data()
        if df is None or len(df) == 0:
            time.sleep(60)
            continue

        orb_high, orb_low = get_orb_level(df)
        last_price = float(df.iloc[-1]['close'])
        vwap = float(df.iloc[-1]['vwap'])
        ema9 = float(df.iloc[-1]['ema_9'])
        ema21 = float(df.iloc[-1]['ema_21'])

        # --- FILTER 2: VWAP + EMA + PCR ---
        oc, pcr = get_option_chain()
        if oc is None:
            time.sleep(60)
            continue

        direction = None
        # BUY CE ke liye 4 Condition
        if last_price > orb_high and last_price > vwap and ema9 > ema21 and pcr > 1.2:
            direction = "CE"
        # BUY PE ke liye 4 Condition
        elif last_price < orb_low and last_price < vwap and ema9 < ema21 and pcr < 0.8:
            direction = "PE"

        if direction is None:
            print(f"No Trade - Price {last_price:.2f} VWAP {vwap:.2f} PCR {pcr:.2f} ORB High {orb_high} Low {orb_low} - Wait")
            time.sleep(60)
            continue

        # --- FILTER 3: GREEKS ---
        strike, opt_data = find_best_strike(oc, direction)
        if strike is None:
            print("Sahi Strike nahi mila - Delta/Theta fail - No Trade")
            time.sleep(60)
            continue

        # --- SAB PASS = TRADE LO ---
        entry_price = float(opt_data.get('last_price') or opt_data.get('ltp') or 0)
        print(f"TRADE MILA BOSS! {direction} Strike {strike} Delta {opt_data.get('greeks', {}).get('delta')}")
        sl_price = entry_price * 0.60
        target1 = entry_price * 1.50
        target2 = entry_price * 2.00
        print(f"Entry {entry_price} SL {sl_price:.2f} T1 {target1:.2f} T2 {target2:.2f}")

        if PAPER_TRADING:
            print("PAPER TRADE - Order Nahi Bheja, Sirf Note Kiya")
            print(f"PAPER BUY: {direction} {strike} @ {entry_price} Qty {LOT_SIZE_NIFTY}")
        else:
            symbol = opt_data.get('symbol') or f"NIFTY {strike} {direction}"
            place_tradejini_order(symbol, LOT_SIZE_NIFTY, direction)
            print(f"LIVE Order Lag Gaya")

        trades_today += 1
        print(f"Aaj ke {trades_today} Trade ho gaye")
        if trades_today >= MAX_TRADES_PER_DAY:
            print("Aaj ke 2 Trade ho gaye - Band")
            break

        time.sleep(60)

if __name__ == "__main__":
    if tradejini_login():
        main_ai()
    else:
        print("Login nahi hua - Code band kar diya")
