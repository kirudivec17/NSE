# APP.PY - TUMHARA PVT FNO APP - Broker API Daalo Aur Connect Karo
# Chalane Ke Liye: streamlit run app.py

import streamlit as st
import time
import yfinance as yf
import math
import os

st.set_page_config(page_title="FNO Pvt App", layout="wide")
st.title("🔥 FNO PAPER TRADING - PVT APP")
st.write("Broker API Daalo - Connect Karo - Paper Trading Shuru Karo")

# --- SIDEBAR - BROKER CONNECT ---
st.sidebar.header("🔑 Broker Connect")
broker = st.sidebar.selectbox("Broker Chuno", ["UPSTOX", "ZERODHA", "ANGEL ONE", "DHAN"])
api_key = st.sidebar.text_input("API Key Daalo", type="password", placeholder="Upstox API Key")
api_secret = st.sidebar.text_input("API Secret Daalo", type="password", placeholder="Upstox API Secret")
access_token = st.sidebar.text_input("Access Token Daalo", type="password", placeholder="Upstox Access Token")

mode = st.sidebar.radio("Mode", ["PAPER - Nakli Paisa, Asli Price", "LIVE - Asli Paisa (Abhi Band Hai)"])
capital = st.sidebar.number_input("Capital", value=10000)
symbols = st.sidebar.multiselect("Symbols", ["NIFTY", "BANKNIFTY", "SENSEX"], default=["NIFTY", "BANKNIFTY", "SENSEX"])

if st.sidebar.button("🔌 Broker Connect Karo"):
    if not api_key:
        st.sidebar.warning("Pehle API Key Daalo Boss! Bina API Ke Connect Nahi Hoga")
    else:
        # Yaha Asli Upstox Login Hoga - Abhi Ke Liye Yahoo Se Test Kar Rahe Hai
        st.session_state["connected"] = True
        st.session_state["broker"] = broker
        st.sidebar.success(f"{broker} Connected! ✅ - Abhi Yahoo Data Se Chal Raha Hai, Upstox API Baad Me Lagega")
        os.environ["UPSTOX_API_KEY"] = api_key
        os.environ["UPSTOX_ACCESS_TOKEN"] = access_token

if "connected" not in st.session_state:
    st.session_state["connected"] = False

if not st.session_state.get("connected"):
    st.info("👈 Pehle Left Side Me Broker Ka API Daal Ke Connect Karo")
    st.stop()

# --- LIVE DATA FUNCTION ---
def get_live(symbol):
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "SENSEX": "^BSESN"}
    ticker = yf.Ticker(ticker_map[symbol])
    hist = ticker.history(period="1d", interval="1m")
    if hist.empty:
        return None
    spot = float(hist["Close"].iloc[-1])
    open_price = float(hist["Open"].iloc[0])
    move = ((spot - open_price) / open_price * 100) if open_price else 0
    # Black-Scholes se CE/PE Price
    def bs(spot, strike):
        r, iv, T = 0.065, 0.13, 2/365
        d1 = (math.log(spot/strike) + (r + 0.5*iv*iv)*T) / (iv*math.sqrt(T))
        d2 = d1 - iv*math.sqrt(T)
        def N(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
        ce = spot*N(d1) - strike*math.exp(-r*T)*N(d2)
        pe = strike*math.exp(-r*T)*N(-d2) - spot*N(-d1)
        return round(ce,2), round(pe,2)
    step = 50 if symbol == "NIFTY" else 100
    strike = round(spot/step)*step
    ce, pe = bs(spot, strike)
    return {"spot": round(spot,2), "move": round(move,3), "strike": strike, "ce": ce, "pe": pe}

# --- DASHBOARD ---
st.subheader(f"Broker: {st.session_state.get('broker')} | Mode: {mode} | Capital: {capital}")

if "balance" not in st.session_state:
    st.session_state["balance"] = capital
    st.session_state["orders"] = []
    st.session_state["running"] = False

col1, col2, col3 = st.columns(3)
col1.metric("Balance", st.session_state["balance"])
col2.metric("Open Orders", len([o for o in st.session_state["orders"] if o["status"]=="OPEN"]))
col3.metric("Total PnL", st.session_state["balance"] - capital)

start = st.button("▶️ Trading START Karo")
stop = st.button("⏹️ Trading STOP Karo")
if start:
    st.session_state["running"] = True
if stop:
    st.session_state["running"] = False

placeholder = st.empty()

if st.session_state["running"]:
    st.success("Trading Chal Rahi Hai - Live Price Har 10 Sec Me Update Hoga")
    # Ek Round Chalao
    for symbol in symbols:
        data = get_live(symbol)
        if data:
            st.write(f"**{symbol}** | Spot: {data['spot']} | Move: {data['move']}% | ATM: {data['strike']} | CE: {data['ce']} | PE: {data['pe']}")
            # Signal - Pichle Wala Logic
            if data['move'] > 0.3:
                signal = "BUY_CE"
            elif data['move'] < -0.3:
                signal = "BUY_PE"
            else:
                signal = "SELL_CE"
            st.write(f"→ Signal: {signal}")
    st.info("Abhi 1 Round Dikhaya Hai - Auto Loop Ke Liye Neeche Wala Tarika Dekho - Streamlit Me Auto Refresh Lagana Padega")
else:
    st.warning("Trading Band Hai - START Dabao")

st.subheader("📋 Orders")
if st.session_state["orders"]:
    st.table(st.session_state["orders"])
else:
    st.write("Abhi Koi Order Nahi Hai")

st.subheader("❓ Agla Step Kya Hai?")
st.write("1. Upstox Developer Portal Pe Jao - https://api.upstox.com - App Banao - API Key Lo")
st.write("2. Yaha API Key Daalo - Connect Karo")
st.write("3. Fir Main Upstox Ka Asli Data Wala Code Is App Me Jod Dunga - Yahoo Hat Jayega")
