# APP.PY V4 - ANGEL ONE STYLE - BLUE THEME - OPTION CHAIN + REAL JESA ORDER TICKET
# Purana mita ke ye poora paste karo

import streamlit as st
import requests
import math
from datetime import datetime

st.set_page_config(page_title="FNO Pvt App - Angel Style", layout="wide", initial_sidebar_state="collapsed")

# ============ ANGEL ONE BLUE CSS ============
st.markdown("""
<style>
.main { background-color: #F2F5FA; }
div[data-testid="stAppViewContainer"] { background-color: #F2F5FA; }
/* Blue Header */
.angel-header { background: linear-gradient(135deg, #1A4BFF 0%, #0A2E9E 100%); color: white; padding: 16px 16px 12px 16px; border-radius: 0 0 18px 18px; margin: -20px -20px 12px -20px; }
.angel-header h2 { color: white; margin: 0; font-size: 22px; }
.angel-header p { color: #D6E0FF; margin: 2px 0 0 0; font-size: 13px; }
/* Cards */
.card { background: white; border-radius: 14px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 10px; }
.small { font-size: 12px; color: #6B7280; }
.big { font-size: 20px; font-weight: 700; }
.green { color: #0E9F6E; font-weight: 700; }
.red { color: #E02424; font-weight: 700; }
/* Option Chain Header */
.oc-head { display: flex; background: #1A4BFF; color: white; border-radius: 10px 10px 0 0; padding: 8px; font-size: 13px; font-weight: 700; text-align: center; }
.oc-row { display: flex; background: white; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; }
.oc-row-atm { display: flex; background: #FFF7E6; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; border-left: 3px solid #FF9F00; }
.ce-btn { background: #E6F7EE; color: #0E9F6E; border-radius: 8px; padding: 6px; font-weight: 700; }
.pe-btn { background: #FDECEC; color: #E02424; border-radius: 8px; padding: 6px; font-weight: 700; }
/* Bottom Nav */
.bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid #E5E7EB; display: flex; justify-content: space-around; padding: 8px; z-index: 999; font-size: 11px; color: #6B7280; }
.stButton>button { border-radius: 10px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============ SESSION ============
if "balance" not in st.session_state:
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["connected"] = False
    st.session_state["token"] = ""
    st.session_state["user"] = ""
    st.session_state["chain"] = {}
    st.session_state["selected"] = None

# ============ HEADER - ANGEL ONE JESA ============
st.markdown("""
<div class="angel-header">
<h2>📈 Options Trading Made Intuitive</h2>
<p>Enjoy Enhanced Option Chain with Greeks • FNO Pvt App</p>
</div>
""", unsafe_allow_html=True)

# ============ TOP BAR - LOGIN / CONNECT ============
with st.expander("🔑 Broker Connect - Upstox - Yaha Click Karo", expanded=not st.session_state["connected"]):
    c1, c2, c3 = st.columns(3)
    api_key = c1.text_input("API Key", type="password")
    api_secret = c2.text_input("API Secret", type="password")
    access_token = c3.text_input("Access Token - Roz 9:00 Baje Naya", type="password")
    if st.button("🔌 Connect Karo - Upstox", use_container_width=True):
        if not access_token:
            st.warning("Pehle Access Token Daalo Boss!")
        else:
            headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
            try:
                r = requests.get("https://api.upstox.com/v2/user/profile", headers=headers, timeout=10)
                if r.status_code == 200:
                    d = r.json().get("data", {})
                    st.session_state["connected"] = True
                    st.session_state["token"] = access_token
                    st.session_state["user"] = d.get("user_name", "User")
                    st.success(f"Connected ✅ Welcome {st.session_state['user']}")
                    st.rerun()
                else:
                    st.error(f"Token Galat / Expire - Code {r.status_code} - Naya Token Banao")
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.get("connected"):
    st.info("👆 Upar Connect Karke Aao - Fir Option Chain Dikh Jayega")
    st.stop()

# ============ FUNCTIONS ============
INSTRUMENT_MAP = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank", "SENSEX": "BSE_INDEX|SENSEX"}
STEP_MAP = {"NIFTY": 50, "BANKNIFTY": 100, "SENSEX": 100}
LOT_MAP = {"NIFTY": 25, "BANKNIFTY": 25, "SENSEX": 10}

def get_quote(key):
    h = {"Authorization": f"Bearer {st.session_state['token']}", "Accept": "application/json"}
    try:
        r = requests.get("https://api.upstox.com/v2/market-quote/quotes", headers=h, params={"instrument_key": key}, timeout=10)
        if r.status_code != 200:
            return None, f"Code {r.status_code}"
        data = r.json().get("data", {})
        if not data:
            return None, "Empty"
        return list(data.values())[0], ""
    except Exception as e:
        return None, str(e)

def bs(spot, strike, days=2):
    if spot <= 0 or strike <= 0:
        return 0.0, 0.0
    r, iv, T = 0.065, 0.13, max(days/365.0, 0.001)
    try:
        d1 = (math.log(spot/strike) + (r + 0.5*iv*iv)*T) / (iv*math.sqrt(T))
        d2 = d1 - iv*math.sqrt(T)
        N = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
        ce = spot*N(d1) - strike*math.exp(-r*T)*N(d2)
        pe = strike*math.exp(-r*T)*N(-d2) - spot*N(-d1)
        return round(ce,2), round(pe,2)
    except:
        return 0.0, 0.0

# ============ TABS - NIFTY / BANKNIFTY / SENSEX ============
tab = st.radio("Index Chuno", ["NIFTY", "BANKNIFTY", "SENSEX"], horizontal=True, label_visibility="collapsed")
st.session_state["current_tab"] = tab

if st.button("🔄 Live Option Chain Refresh Karo - Upstox Se", use_container_width=True):
    q, err = get_quote(INSTRUMENT_MAP[tab])
    if q is None:
        st.error(f"Data Nahi Mila - {err} - Token Check Karo")
    else:
        ltp = float(q.get("last_price", 0) or 0)
        ohlc = q.get("ohlc", {}) or {}
        open_p = float(ohlc.get("open", ltp) or ltp)
        move = ((ltp-open_p)/open_p*100) if open_p else 0
        step = STEP_MAP[tab]
        atm = int(round(ltp/step)*step)
        chain = []
        for i in range(-4, 5):  # 9 strikes - ATM ke aas paas
            strike = atm + i*step
            ce, pe = bs(ltp, strike)
            # Fake OI / Volume jesa lagna chahiye - real me Upstox Option Chain API se aayega
            oi_ce = max(100000 - abs(i)*18000, 5000)
            oi_pe = max(100000 - abs(i)*15000, 5000)
            chain.append({"strike": strike, "ce": ce, "pe": pe, "oi_ce": oi_ce, "oi_pe": oi_pe, "is_atm": (i==0)})
        st.session_state["chain"] = {"ltp": ltp, "open": open_p, "move": move, "atm": atm, "chain": chain, "time": datetime.now().strftime("%H:%M:%S")}

chain_data = st.session_state.get("chain", {})

# ============ TOP CARD - INDEX PRICE ============
if chain_data:
    ltp = chain_data["ltp"]; move = chain_data["move"]; atm = chain_data["atm"]
    color = "green" if move >= 0 else "red"
    arrow = "▲" if move >= 0 else "▼"
    st.markdown(f"""
    <div class="card">
    <div style="display:flex; justify-content:space-between;">
    <div><div class="small">{tab} • {datetime.now().strftime('%d %b %Y')}</div><div class="big">{ltp:.2f} <span class="{color}">{arrow} {move:.2f}%</span></div><div class="small">ATM Strike: {atm} • Updated: {chain_data['time']}</div></div>
    <div style="text-align:right;"><div class="small">Balance</div><div class="big">₹{st.session_state['balance']:.0f}</div><div class="small">Day P&L: <span class="{'green' if st.session_state['balance']-st.session_state['start_balance']>=0 else 'red'}">₹{st.session_state['balance']-st.session_state['start_balance']:.2f}</span></div></div>
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"👆 Upar Wala Blue Button Dabao - {tab} Ka Live Option Chain Aayega")

# ============ OPTION CHAIN - ANGEL ONE JESA ============
if chain_data:
    st.markdown(f"""
    <div style="display:flex; gap:8px; margin-bottom:8px;">
    <div class="card" style="flex:1; text-align:center;"><div class="small">LTP</div><b>{chain_data['ltp']:.2f}</b></div>
    <div class="card" style="flex:1; text-align:center;"><div class="small">OI</div><b>Greeks</b></div>
    <div class="card" style="flex:1; text-align:center;"><div class="small">Expiry</div><b>Aaj / Kal</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="oc-head"><div style="flex:1;">CALL LTP</div><div style="flex:1;">STRIKE</div><div style="flex:1;">PUT LTP</div></div>
    """, unsafe_allow_html=True)

    for row in chain_data["chain"]:
        cls = "oc-row-atm" if row["is_atm"] else "oc-row"
        atm_tag = " • ATM" if row["is_atm"] else ""
        st.markdown(f"""
        <div class="{cls}"><div style="flex:1;"><span class="ce-btn">₹{row['ce']}</span><div class="small">OI {row['oi_ce']/100000:.2f}L</div></div>
        <div style="flex:1;"><b>{row['strike']}{atm_tag}</b></div>
        <div style="flex:1;"><span class="pe-btn">₹{row['pe']}</span><div class="small">OI {row['oi_pe']/100000:.2f}L</div></div></div>
        """, unsafe_allow_html=True)

    st.caption("Call Pe Click Karne Ke Liye Neeche Wala Order Ticket Use Karo - Strike Select Karo, Fir Buy Dabao")

    # ============ ORDER TICKET - REAL JESA ============
    st.markdown('<div class="card"><b>🧾 Order Ticket - Real Jaisa</b></div>', unsafe_allow_html=True)
    strikes = [r["strike"] for r in chain_data["chain"]]
    c1, c2, c3 = st.columns(3)
    sel_strike = c1.selectbox("Strike Chuno", strikes, index=4)
    sel_type = c2.selectbox("CE / PE", ["CE - Call", "PE - Put"])
    sel_side = c3.selectbox("Buy / Sell", ["BUY", "SELL"])

    # Selected price nikalo
    sel_row = [r for r in chain_data["chain"] if r["strike"] == sel_strike][0]
    sel_price = sel_row["ce"] if "CE" in sel_type else sel_row["pe"]
    lot = LOT_MAP[tab]
    qty = st.number_input(f"Qty - Lot Size {lot} - Kitne Lot?", min_value=1, max_value=10, value=1, step=1)
    total_qty = qty * lot
    total_cost = sel_price * total_qty

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Price", f"₹{sel_price}")
    o2.metric("Qty", f"{total_qty}")
    o3.metric("Total", f"₹{total_cost:.2f}")
    o4.metric("Balance", f"₹{st.session_state['balance']:.2f}")

    t1, t2 = st.columns(2)
    target_pct = t1.slider("Target %", 5, 50, 20)
    sl_pct = t2.slider("Stoploss %", 5, 30, 10)
    if sel_side == "BUY":
        tgt = round(sel_price * (1 + target_pct/100), 2)
        sl = round(sel_price * (1 - sl_pct/100), 2)
    else:
        tgt = round(sel_price * (1 - target_pct/100), 2)
        sl = round(sel_price * (1 + sl_pct/100), 2)
    st.write(f"🎯 Target: **₹{tgt}** | 🛑 Stoploss: **₹{sl}** | Order: **{tab} {sel_strike} {sel_type} {sel_side}**")

    # BUY / SELL BUTTON - ANGEL JESA BADA
    btn_label = f"🟢 BUY {tab} {sel_strike} {sel_type} @ ₹{sel_price}" if sel_side == "BUY" else f"🔴 SELL {tab} {sel_strike} {sel_type} @ ₹{sel_price}"
    if st.button(btn_label, use_container_width=True, type="primary"):
        if any(o["status"] == "OPEN" for o in st.session_state["orders"]):
            st.warning("Ek Order Pehle Se Open Hai - Pehle Usko Exit Karo, Fir Naya Lo!")
        elif total_cost > st.session_state["balance"] and sel_side == "BUY":
            st.error(f"Paisa Kam Hai! Chahiye ₹{total_cost:.2f}, Hai ₹{st.session_state['balance']:.2f} - Lot Kam Karo!")
        else:
            st.session_state["orders"].append({
                "symbol": tab, "strike": sel_strike, "type": sel_type, "side": sel_side,
                "entry": sel_price, "qty": total_qty, "target": tgt, "stoploss": sl,
                "status": "OPEN", "time": datetime.now().strftime("%d-%m %H:%M"), "pnl": 0.0
            })
            st.success(f"✅ Paper Order Lag Gaya! {tab} {sel_strike} {sel_type} {sel_side} Entry ₹{sel_price} Qty {total_qty} - Paisa Real Nahi Kata, Sirf Paper Hai!")
            st.rerun()

# ============ ORDERS / POSITIONS / HISTORY - ANGEL JESA ============
st.markdown('<div class="card"><b>📋 Orders • Positions • Day P&L</b></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🟢 Open Positions", "✅ History"])

with tab1:
    opens = [o for o in st.session_state["orders"] if o["status"] == "OPEN"]
    if not opens:
        st.write("Koi Open Order Nahi Hai - Upar Se Option Chain Se Order Lo")
    for idx, o in enumerate(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        # Live price se PnL - chain se
        cur = o["entry"]
        if chain_data:
            r = [x for x in chain_data["chain"] if x["strike"] == o["strike"]]
            if r:
                cur = r[0]["ce"] if "CE" in o["type"] else r[0]["pe"]
        pnl = (cur - o["entry"]) * o["qty"] if o["side"] == "BUY" else (o["entry"] - cur) * o["qty"]
        pnl_color = "green" if pnl >= 0 else "red"
        st.markdown(f"""
        <div class="card">
        <b>{o['symbol']} {o['strike']} {o['type']} {o['side']}</b> • Qty {o['qty']} • {o['time']}<br>
        Entry ₹{o['entry']} → Abhi ₹{cur} • Target ₹{o['target']} • SL ₹{o['stoploss']}<br>
        Live P&L: <span class="{pnl_color}">₹{pnl:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"❌ Square Off Karo - {o['symbol']} {o['strike']} {o['type']} - PnL ₹{pnl:.2f}", key=f"exit_{idx}", use_container_width=True):
            st.session_state["balance"] += pnl
            o["status"] = "CLOSED"
            o["pnl"] = round(pnl, 2)
            o["exit_price"] = cur
            st.success(f"Square Off Ho Gaya! PnL ₹{pnl:.2f} | Naya Balance ₹{st.session_state['balance']:.2f}")
            st.rerun()

with tab2:
    closed = [o for o in st.session_state["orders"] if o["status"] == "CLOSED"]
    if not closed:
        st.write("Abhi Koi Closed Order Nahi Hai")
    else:
        for o in closed:
            c = "green" if o["pnl"] >= 0 else "red"
            st.markdown(f"""<div class="card">{o['symbol']} {o['strike']} {o['type']} {o['side']} • Entry ₹{o['entry']} → Exit ₹{o.get('exit_price','-')} • P&L <span class="{c}">₹{o['pnl']}</span></div>""", unsafe_allow_html=True)
        st.write(f"**Total Day P&L: ₹{st.session_state['balance'] - st.session_state['start_balance']:.2f}**")

if st.button("🔄 Sab Reset Karo - Balance 10000", use_container_width=True):
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["chain"] = {}
    st.rerun()

# Bottom Nav jesa dikhane ke liye
st.markdown("""
<div class="bottom-nav"><span>🏠 HOME</span><span>👀 WATCHLIST</span><span>💼 PORTFOLIO</span><span>📋 ORDERS</span><span>👤 ACCOUNT</span></div>
<div style="height:40px;"></div>
""", unsafe_allow_html=True)
st.caption("💡 Ye PAPER Hai - Real Paisa Nahi Katega! Real Order Ke Liye Upstox Place Order API Lagana Padega - Pehle Paper Me Practice Karo!")
