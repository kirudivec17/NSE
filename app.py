# APP.PY V2 - UPSTOX REAL DATA - Yahoo Band
# Chalane ke liye: streamlit run app.py

import streamlit as st
import requests
import time

st.set_page_config(page_title="FNO Pvt App", layout="wide")
st.title("🔥 FNO PAPER TRADING - PVT APP - UPSTOX REAL")

# --- SIDEBAR ---
st.sidebar.header("🔑 Broker Connect")
broker = st.sidebar.selectbox("Broker", ["UPSTOX"])
api_key = st.sidebar.text_input("API Key", type="password")
api_secret = st.sidebar.text_input("API Secret", type="password")
access_token = st.sidebar.text_input("Access Token - Roz Naya", type="password")

mode = st.sidebar.radio("Mode", ["PAPER - Nakli Paisa, Asli Price"])
capital = st.sidebar.number_input("Capital", value=10000)
symbols = st.sidebar.multiselect("Symbols", ["NIFTY", "BANKNIFTY", "SENSEX"], default=["NIFTY"])

if st.sidebar.button("🔌 Connect Karo"):
    if not access_token:
        st.sidebar.warning("Pehle Access Token Daalo!")
    else:
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        r = requests.get("https://api.upstox.com/v2/user/profile", headers=headers)
        if r.status_code == 200:
            data = r.json().get("data", {})
            st.session_state["connected"] = True
            st.session_state["token"] = access_token
            st.session_state["user"] = data.get("user_name", "User")
            st.sidebar.success(f"Connected! ✅ Welcome {data.get('user_name','')}")
        else:
            st.sidebar.error(f"Token Galat / Expire Hai! Code: {r.status_code} - Naya Token Banao")

if not st.session_state.get("connected"):
    st.info("👈 Pehle Left Me API Key + Access Token Daal Ke Connect Karo")
    st.stop()

st.success(f"Welcome {st.session_state.get('user')} - Upstox Connected ✅ | Mode: {mode}")

# --- UPSTOX REAL DATA ---
def get_upstox_quote(instrument_key):
    headers = {"Authorization": f"Bearer {st.session_state['token']}", "Accept": "application/json"}
    url = f"https://api.upstox.com/v2/market-quote/quotes?instrument_key={instrument_key}"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    return r.json().get("data", {}).get(instrument_key, {})

instrument_map = {
    "NIFTY": "NSE_INDEX%7CNifty%2050",
    "BANKNIFTY": "NSE_INDEX%7CNifty%20Bank",
    "SENSEX": "BSE_INDEX%7CSENSEX",
}

# --- DASHBOARD ---
if "balance" not in st.session_state:
    st.session_state["balance"] = capital
    st.session_state["orders"] = []

col1, col2, col3 = st.columns(3)
col1.metric("Balance", st.session_state["balance"])
col2.metric("Open Orders", len([o for o in st.session_state["orders"] if o["status"]=="OPEN"]))
col3.metric("Total PnL", st.session_state["balance"] - capital)

if st.button("▶️ Live Price Dekho - Upstox Se"):
    for sym in symbols:
        q = get_upstox_quote(instrument_map[sym])
        if q:
            ltp = q.get("last_price")
            open_p = q.get("ohlc", {}).get("open", ltp)
            move = ((ltp - open_p)/open_p*100) if open_p else 0
            st.write(f"**{sym}** | REAL LTP: {ltp} | Open: {open_p} | Aaj Move: {round(move,3)}%")
            if move > 0.3:
                st.write(f"→ Signal: BUY_CE")
            elif move < -0.3:
                st.write(f"→ Signal: BUY_PE")
            else:
                st.write(f"→ Signal: SELL_CE")
        else:
            st.error(f"{sym} - Data Nahi Mila - Token Check Karo")

st.subheader("📋 Orders")
if st.session_state["orders"]:
    st.table(st.session_state["orders"])
else:
    st.write("Abhi Koi Order Nahi Hai - Pehle Live Price Dekho")

st.info("Agla Step: Isme Paper Order + Target/SL + Auto Loop Jodenge - Pehle Ye Wala Chala Ke Dekho Token Kaam Kar Raha Hai Ya Nahi")
