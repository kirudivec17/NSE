# APP.PY V3 - FULL CODE - UPSTOX REAL + PAPER TRADING
# Purana app.py mita ke ye poora paste karo
# Chalane ke liye: Streamlit Cloud pe GitHub se auto chalega

import streamlit as st
import requests
import math
import time
from datetime import datetime, date

st.set_page_config(page_title="FNO Pvt App - Upstox Real", layout="wide")
st.title("🔥 FNO PAPER TRADING - PVT APP - UPSTOX REAL")

# ============ SIDEBAR - BROKER CONNECT ============
st.sidebar.header("🔑 Broker Connect")
broker = st.sidebar.selectbox("Broker", ["UPSTOX"])
api_key = st.sidebar.text_input("API Key", type="password", placeholder="Upstox API Key")
api_secret = st.sidebar.text_input("API Secret", type="password", placeholder="Upstox API Secret")
access_token = st.sidebar.text_input("Access Token - Roz Naya", type="password", placeholder="Aaj ka Access Token")

mode = st.sidebar.radio("Mode", ["PAPER - Nakli Paisa, Asli Price"])
capital = st.sidebar.number_input("Capital", value=10000, step=1000)
symbols = st.sidebar.multiselect("Symbols", ["NIFTY", "BANKNIFTY", "SENSEX"], default=["NIFTY", "BANKNIFTY", "SENSEX"])
qty_map = {"NIFTY": 25, "BANKNIFTY": 25, "SENSEX": 10}
target_pct = st.sidebar.slider("Target %", 5, 50, 20)
stoploss_pct = st.sidebar.slider("Stoploss %", 5, 30, 10)

# Session init - ek baar hi hoga
if "balance" not in st.session_state:
    st.session_state["balance"] = float(capital)
    st.session_state["start_balance"] = float(capital)
    st.session_state["orders"] = []
    st.session_state["connected"] = False
    st.session_state["token"] = ""
    st.session_state["user"] = ""
    st.session_state["last_price"] = {}

if st.sidebar.button("🔌 Connect Karo"):
    if not api_key or not access_token:
        st.sidebar.warning("Pehle API Key + Access Token Daalo Boss!")
    else:
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        try:
            r = requests.get("https://api.upstox.com/v2/user/profile", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json().get("data", {})
                st.session_state["connected"] = True
                st.session_state["token"] = access_token
                st.session_state["user"] = data.get("user_name", "User")
                st.sidebar.success(f"Connected! ✅ Welcome {st.session_state['user']}")
            else:
                st.sidebar.error(f"Token Galat / Expire Hai! Code: {r.status_code} - Naya Token Banao")
                st.session_state["connected"] = False
        except Exception as e:
            st.sidebar.error(f"Network Error: {e}")

if not st.session_state.get("connected"):
    st.info("👈 Pehle Left Side Me API Key + API Secret + Access Token Daal Ke Connect Karo")
    st.warning("Access Token Roz Subah Naya Banana Padega - Upstox Developer Page Pe Generate Access Token Se")
    st.stop()

st.success(f"Welcome {st.session_state.get('user')} - Upstox Connected ✅ | Mode: {mode} | Capital: {capital}")

# ============ UPSTOX REAL DATA FUNCTIONS ============
INSTRUMENT_MAP = {
    "NIFTY": "NSE_INDEX|Nifty 50",
    "BANKNIFTY": "NSE_INDEX|Nifty Bank",
    "SENSEX": "BSE_INDEX|SENSEX",
}

def get_upstox_quote(instrument_key):
    """Upstox se real LTP lao - params se bhejte hai taaki Space / | sahi encode ho"""
    headers = {"Authorization": f"Bearer {st.session_state['token']}", "Accept": "application/json"}
    try:
        r = requests.get(
            "https://api.upstox.com/v2/market-quote/quotes",
            headers=headers,
            params={"instrument_key": instrument_key},
            timeout=10,
        )
        if r.status_code != 200:
            return None, f"Code {r.status_code}: {r.text[:200]}"
        data = r.json().get("data", {})
        if not data:
            return None, "Empty data"
        if instrument_key in data:
            return data[instrument_key], ""
        # Kabhi key thoda alag aata hai - pehla value le lo
        return list(data.values())[0], ""
    except Exception as e:
        return None, str(e)

def bs_price(spot, strike, days=2):
    """Black-Scholes se Option ka approx price - Paper ke liye"""
    if spot <= 0 or strike <= 0:
        return 0.0, 0.0
    r, iv, T = 0.065, 0.13, max(days / 365.0, 0.001)
    try:
        d1 = (math.log(spot / strike) + (r + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
        d2 = d1 - iv * math.sqrt(T)
        def N(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        ce = spot * N(d1) - strike * math.exp(-r * T) * N(d2)
        pe = strike * math.exp(-r * T) * N(-d2) - spot * N(-d1)
        return round(ce, 2), round(pe, 2)
    except Exception:
        return 0.0, 0.0

def is_market_open():
    """Market 9:15 - 15:30 Mon-Fri khula hota hai"""
    now = datetime.now()
    if now.weekday() >= 5:  # Sat Sun
        return False
    t = now.time()
    return (t.hour > 9 or (t.hour == 9 and t.minute >= 15)) and (t.hour < 15 or (t.hour == 15 and t.minute <= 30))

def get_signal(move):
    """Strategy - Pichle logic jaisa - Aaj ke move se signal (Live me yehi pata hota hai)"""
    if move > 0.3:
        return "BUY_CE", "MODE 1 - DELTA - Upar"
    if move < -0.3:
        return "BUY_PE", "MODE 1 - DELTA - Neeche"
    return "SELL_CE", "MODE 3 - THETA - Shant"

# ============ DASHBOARD ============
open_orders = [o for o in st.session_state["orders"] if o["status"] == "OPEN"]
total_pnl = st.session_state["balance"] - st.session_state["start_balance"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Balance", f"{st.session_state['balance']:.2f}")
col2.metric("Open Orders", len(open_orders))
col3.metric("Total PnL", f"{total_pnl:.2f}")
col4.metric("Market", "OPEN 🟢" if is_market_open() else "CLOSED 🔴")

st.divider()

# ============ LIVE PRICE + PAPER ORDER ============
st.subheader("📡 Live Price - Upstox Real")

if st.button("▶️ Live Price Dekho - Upstox Se", use_container_width=True):
    for sym in symbols:
        key = INSTRUMENT_MAP[sym]
        q, err = get_upstox_quote(key)
        if q is None:
            st.error(f"{sym} - Data Nahi Mila - {err}")
            continue

        ltp = float(q.get("last_price", 0) or 0)
        ohlc = q.get("ohlc", {}) or {}
        open_p = float(ohlc.get("open", ltp) or ltp)
        high_p = float(ohlc.get("high", ltp) or ltp)
        low_p = float(ohlc.get("low", ltp) or ltp)
        move = ((ltp - open_p) / open_p * 100) if open_p else 0.0

        step = 50 if sym == "NIFTY" else 100
        strike = int(round(ltp / step) * step)
        ce, pe = bs_price(ltp, strike)
        signal, mode_txt = get_signal(move)

        st.session_state["last_price"][sym] = {
            "ltp": ltp, "open": open_p, "move": round(move, 3),
            "strike": strike, "ce": ce, "pe": pe,
            "signal": signal, "mode": mode_txt,
        }

        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**{sym}**")
        c2.write(f"LTP: **{ltp}** | Open: {open_p}")
        c3.write(f"Move: **{move:.3f}%** | ATM: {strike}")
        c4.write(f"CE: {ce} | PE: {pe}")
        st.caption(f"→ Signal: {signal} | {mode_txt} | High: {high_p} Low: {low_p} | Time: {datetime.now().strftime('%H:%M:%S')}")

        # Paper Order Button - Har symbol ke liye alag
        if st.button(f"📝 Paper Order Lo - {sym} {signal} @ {ce if 'CE' in signal else pe}", key=f"order_{sym}"):
            if not is_market_open():
                st.warning(f"{sym} - Market BAND Hai - Abhi Paper Order Nahi Lagega - Kal 9:15 Pe Chalayenge")
            elif any(o["symbol"] == sym and o["status"] == "OPEN" for o in st.session_state["orders"]):
                st.warning(f"{sym} - Pehle Se Ek Open Order Hai - Pehle Usko Exit Karo")
            else:
                entry = ce if "CE" in signal else pe
                qty = qty_map.get(sym, 25)
                cost = entry * qty
                if cost > st.session_state["balance"]:
                    st.error(f"Paisa Kam Hai! Cost {cost:.2f} > Balance {st.session_state['balance']:.2f} - Capital Badhao Ya Dusra Symbol Lo")
                else:
                    if signal.startswith("BUY"):
                        tgt = round(entry * (1 + target_pct / 100), 2)
                        sl = round(entry * (1 - stoploss_pct / 100), 2)
                    else:  # SELL
                        tgt = round(entry * (1 - target_pct / 100), 2)
                        sl = round(entry * (1 + stoploss_pct / 100), 2)
                    order = {
                        "symbol": sym,
                        "signal": signal,
                        "strike": strike,
                        "entry": entry,
                        "qty": qty,
                        "target": tgt,
                        "stoploss": sl,
                        "status": "OPEN",
                        "time": datetime.now().strftime("%d-%m %H:%M"),
                        "pnl": 0.0,
                    }
                    st.session_state["orders"].append(order)
                    st.success(f"✅ Paper Order Lag Gaya! {sym} {signal} Entry {entry} Qty {qty} Target {tgt} SL {sl} - Paisa Real Nahi Kata, Sirf Paper Hai!")
                    st.rerun()

# Last price dikhao agar pehle se hai
if st.session_state["last_price"]:
    st.caption("Neeche Last Fetch Kiya Hua Price Hai - Naya Price Ke Liye Upar Wala Button Dobara Dabao")

# ============ OPEN ORDERS - EXIT + UPDATE ============
st.subheader("📋 Orders - Paper")

if not st.session_state["orders"]:
    st.write("Abhi Koi Order Nahi Hai - Pehle Upar Se Live Price Dekho, Fir Paper Order Lo")
else:
    for idx, o in enumerate(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        # Live price se current PnL nikalo
        lp = st.session_state["last_price"].get(o["symbol"], {})
        cur_ce = lp.get("ce", o["entry"])
        cur_pe = lp.get("pe", o["entry"])
        cur_price = cur_ce if "CE" in o["signal"] else cur_pe
        if o["signal"].startswith("BUY"):
            live_pnl = (cur_price - o["entry"]) * o["qty"]
        else:
            live_pnl = (o["entry"] - cur_price) * o["qty"]

        st.write(f"**{o['symbol']} {o['signal']}** | Strike {o['strike']} | Entry {o['entry']} | Abhi {cur_price} | Qty {o['qty']} | Target {o['target']} | SL {o['stoploss']} | Live PnL **{live_pnl:.2f}** | Time {o['time']}")

        # Auto Target / SL check
        hit = ""
        if o["signal"].startswith("BUY"):
            if cur_price >= o["target"]:
                hit = "TARGET"
            elif cur_price <= o["stoploss"]:
                hit = "STOPLOSS"
        else:
            if cur_price <= o["target"]:
                hit = "TARGET"
            elif cur_price >= o["stoploss"]:
                hit = "STOPLOSS"
        if hit:
            st.warning(f"⚠️ {hit} Hit Ho Gaya! Exit Dabao!")

        if st.button(f"❌ Exit Karo - {o['symbol']} {o['signal']}", key=f"exit_{idx}"):
            if o["signal"].startswith("BUY"):
                pnl = (cur_price - o["entry"]) * o["qty"]
            else:
                pnl = (o["entry"] - cur_price) * o["qty"]
            st.session_state["balance"] += pnl
            o["status"] = "CLOSED"
            o["pnl"] = round(pnl, 2)
            o["exit_price"] = cur_price
            st.success(f"Order Band! PnL: {pnl:.2f} | Naya Balance: {st.session_state['balance']:.2f}")
            st.rerun()

    # Closed orders history
    closed = [o for o in st.session_state["orders"] if o["status"] == "CLOSED"]
    if closed:
        st.subheader("✅ Closed Orders History")
        st.table(closed)

# ============ RESET ============
st.divider()
if st.button("🔄 Sab Reset Karo - Balance 10000 Pe Le Jao"):
    st.session_state["balance"] = float(capital)
    st.session_state["start_balance"] = float(capital)
    st.session_state["orders"] = []
    st.session_state["last_price"] = {}
    st.rerun()

st.info("💡 Yaad Rakho: Ye PAPER Hai - Real Paisa Nahi Katega! Access Token Roz Subah Naya Banana Padega! Market 9:15-15:30 Khula Hota Hai, Uske Bahar Naya Order Nahi Lagega!")
