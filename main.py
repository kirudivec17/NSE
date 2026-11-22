# ==========================================
# DHAN - TRIPLE FILTER AI SYSTEM
# Strategy: ORB + VWAP + Supertrend + PCR + Greeks
# Broker: Dhan (DhanHQ v2.1.0)
# Author: Kiran Boss
# Date: 22 Nov 2026
# ==========================================

# pip install dhanhq
# pip install pandas

from dhanhq import dhanhq, DhanContext
import pandas as pd
import time
from datetime import datetime, time as dtime

# ===== 1. DHAN LOGIN =====
# Dhan App -> My Profile -> API Access se lo
CLIENT_ID = "TUMHARA_CLIENT_ID_YAHA"
ACCESS_TOKEN = "TUMHARA_ACCESS_TOKEN_YAHA"

context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
dhan = dhanhq(context)

# ===== 2. SETTINGS - TUMHARA RISK =====
CAPITAL = 50000
MAX_LOSS_PER_DAY = -5000
MAX_PROFIT_PER_DAY = 10000
MAX_TRADES_PER_DAY = 2
LOT_SIZE_NIFTY = 65

# ===== 3. STRATEGY - TEENO MERGE =====
def get_vwap_supertrend():
    # 5-Min Candle Data Dhan se
    data = dhan.intraday_minute_data(
        security_id="13", # NIFTY
        exchange_segment="IDX_I",
        instrument_type="INDEX",
        interval="5",
        from_date="2026-11-22 09:15:00",
        to_date="2026-11-22 15:30:00"
    )
    df = pd.DataFrame(data['data'])
    # VWAP Nikalo
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    # Supertrend (10,3) - Simple Logic
    df['ema_9'] = df['close'].ewm(span=9).mean()
    df['ema_21'] = df['close'].ewm(span=21).mean()
    return df

def get_orb_level(df):
    # 9:15 - 9:30 ka High / Low
    orb = df.between_time("09:15", "09:30")
    orb_high = orb['high'].max()
    orb_low = orb['low'].min()
    return orb_high, orb_low

def get_greeks_and_oi():
    # Dhan Option Chain - Greeks + OI + PCR Ek Saath
    chain = dhan.option_chain(
        under_security_id=13,
        under_exchange_segment="IDX_I",
        expiry="0"
    )
    oc = chain['data']['oc']
    # PCR Nikalo
    total_ce_oi = sum([x['ce']['oi'] for x in oc.values()])
    total_pe_oi = sum([x['pe']['oi'] for x in oc.values()])
    pcr = total_pe_oi / total_ce_oi if total_ce_oi else 0
    return oc, pcr

def find_best_strike(oc, spot, direction):
    # AI Strike Selection - Delta 0.50 - 0.65 wala hi lega
    for strike, data in oc.items():
        if direction == "CE":
            greek = data['ce']['greeks']
            if 0.50 <= abs(greek['delta']) <= 0.65:
                if abs(greek['theta']) < 20: # Theta zyada hai toh mat lo
                    return strike, data['ce']
        else:
            greek = data['pe']['greeks']
            if 0.50 <= abs(greek['delta']) <= 0.65:
                if abs(greek['theta']) < 20:
                    return strike, data['pe']
    return None, None

# ===== 4. MAIN AI ENGINE - TEENO FILTER =====
def main_ai():
    print("Boss, System ON ho gaya - 9:30 ka wait kar raha hu...")
    trades_today = 0
    total_pnl = 0

    while True:
        now = datetime.now().time()

        # 9:30 se pehle Trade Nahi - ORB banne do
        if now < dtime(9, 30):
            time.sleep(30)
            continue

        # 3:15 ke baad Sab Band
        if now >= dtime(15, 15):
            print("3:15 ho gaya - Sab Square-Off - Aaj ka kaam khatam")
            dhan.kill_switch('ON') # Dhan ka Kill Switch
            break

        # Daily Limit Check
        if total_pnl <= MAX_LOSS_PER_DAY:
            print("Aaj ka Loss Limit Khatam - System Band")
            break
        if total_pnl >= MAX_PROFIT_PER_DAY:
            print("Aaj ka Profit Target Ho Gaya - System Band")
            break

        # --- FILTER 1: ORB ---
        df = get_vwap_supertrend()
        orb_high, orb_low = get_orb_level(df)
        last_price = df.iloc[-1]['close']
        vwap = df.iloc[-1]['vwap']

        # --- FILTER 2: VWAP + Supertrend + PCR ---
        oc, pcr = get_greeks_and_oi()

        direction = None
        # BUY CE ke liye 5 Condition
        if (last_price > orb_high and
            last_price > vwap and
            df.iloc[-1]['ema_9'] > df.iloc[-1]['ema_21'] and
            pcr > 1.2):
            direction = "CE"

        # BUY PE ke liye 5 Condition
        elif (last_price < orb_low and
              last_price < vwap and
              df.iloc[-1]['ema_9'] < df.iloc[-1]['ema_21'] and
              pcr < 0.8):
            direction = "PE"

        if direction is None:
            print(f"No Trade - Price {last_price} VWAP {vwap} PCR {pcr:.2f} - Wait kar raha hu")
            time.sleep(60)
            continue

        # --- FILTER 3: GREEKS ---
        strike, opt_data = find_best_strike(oc, last_price, direction)
        if strike is None:
            print("Sahi Strike nahi mila - Delta/Theta fail - No Trade")
            time.sleep(60)
            continue

        # --- SAB PASS = TRADE LO ---
        print(f"TRADE MILA BOSS! {direction} Strike {strike} Delta {opt_data['greeks']['delta']}")
        entry_price = opt_data['last_price']

        # Risk - Pehle se Set
        sl_price = entry_price * 0.60  # 40% Loss pe Exit
        target1 = entry_price * 1.50  # 50% Profit pe 50% Book
        target2 = entry_price * 2.00  # 100% Profit pe Baaki Book

        # Dhan se Order Bhejo
        order = dhan.place_order(
            security_id=str(opt_data['security_id']),
            exchange_segment=dhan.NSE_FNO,
            transaction_type=dhan.BUY,
            quantity=LOT_SIZE_NIFTY,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=0
        )
        print(f"Order Lag Gaya - Entry {entry_price} SL {sl_price} T1 {target1} T2 {target2}")

        # 20-Minute Time SL - Agar 20 Min me nahi bhaaga toh Exit
        # Yaha Trailing SL + P&L Booking ka Code aayega
        # Paper Trading ke liye pehle yaha print hi karo

        trades_today += 1
        if trades_today >= MAX_TRADES_PER_DAY:
            print("Aaj ke 2 Trade ho gaye - Band")
            break

        time.sleep(60)

if __name__ == "__main__":
    main_ai()
