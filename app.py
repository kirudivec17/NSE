# APP.PY V5 - AUTO TRADING - ANGEL ONE BLUE + DELTA GAMMA THETA AUTO
# Purana mita ke ye poora paste karo
# VPS pe chalane ke liye bana hai - Hamesha chalega

import streamlit as st
import requests
import math
import time
from datetime import datetime

st.set_page_config(page_title="FNO AUTO - Angel Style", layout="wide", initial_sidebar_state="collapsed")

# ============ BLUE CSS - ANGEL ONE ============
st.markdown("""
<style>
.main { background-color: #F2F5FA; }
.angel-header { background: linear-gradient(135deg, #1A4BFF 0%, #0A2E9E 100%); color: white; padding: 16px; border-radius: 0 0 18px 18px; margin: -20px -20px 12px -20px; }
.angel-header h2 { color: white; margin: 0; font-size: 22px; }
.angel-header p { color: #D6E0FF; margin: 2px 0 0 0; font-size: 13px; }
.card { background: white; border-radius: 14px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 10px; }
.small { font-size: 12px; color: #6B7280; }
.big { font-size: 20px; font-weight: 700; }
.green { color: #0E9F6E; font-weight: 700; }
.red { color: #E02424; font-weight: 700; }
.oc-head { display: flex; background: #1A4BFF; color: white; border-radius: 10px 10px 0 0; padding: 8px; font-size: 13px; font-weight: 700; text-align: center; }
.oc-row { display: flex; background: white; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; }
.oc-row-atm { display: flex; background: #FFF7E6; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; border-left: 3px solid #FF9F00; }
.ce-btn { background: #E6F7EE; color: #0E9F6E; border-radius: 8px; padding: 6px; font-weight: 700; }
.pe-btn { background: #FDECEC; color: #E02424; border-radius: 8px; padding: 6px; font-weight: 700; }
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
    st.session_state["auto_on"] = False
    st.session_state["logs"] = []
    st.session_state["chain"] = {}

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    st.session_state["logs"].insert(0, f"[{t}] {msg}")
    st.session_state["logs"] = st.session_state["logs"][:30]

# ============ HEADER ============
st.markdown("""
<div class="angel-header">
<h2>🤖 AUTO FNO - Options Trading Made Intuitive</h2>
<p>Delta • Gamma • Theta Auto Strategy • VPS Pe Hamesha ON</p>
</div>
""", unsafe_allow_html=True)

# ============ CONNECT ============
with st.expander("🔑 Broker Connect - Upstox - Roz Subah 9:00 Baje Token Daalo", expanded=not st.session_state["connected"]):
    c1, c2, c3 = st.columns(3)
    api_key = c1.text_input("API Key", type="password")
    api_secret = c2.text_input("API Secret", type="password")
    access_token = c3.text_input("Access Token - Roz Naya", type="password")
    if st.button("🔌 Connect Karo", use_container_width=True):
        if not access_token:
            st.warning("Pehle Token Daalo Boss!")
        else:
            h = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
            try:
                r = requests.get("https://api.upstox.com/v2/user/profile", headers=h, timeout=10)
                if r.status_code == 200:
                    d = r.json().get("data", {})
                    st.session_state["connected"] = True
                    st.session_state["token"] = access_token
                    st.session_state["user"] = d.get("user_name", "User")
                    st.success(f"Connected ✅ Welcome {st.session_state['user']}")
                    st.rerun()
                else:
                    st.error(f"Token Expire - Code {r.status_code} - Naya Banao")
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.get("connected"):
    st.info("👆 Upar Connect Karo - Fir AUTO ON Hoga")
    st.stop()

# ============ SETTINGS ============
st.markdown('<div class="card"><b>⚙️ Auto Settings - 10K Capital</b></div>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
capital = s1.number_input("Capital", value=10000, step=1000)
max_per_trade = s2.number_input("Ek Trade Me Max Kitna Lagana Hai?", value=3333, step=500, help="10K / 3 = 3333 - Teeno Symbol Me Ek-Ek Trade - Risk Kam")
max_open = s3.number_input("Ek Saath Max Kitne Order?", value=3, min_value=1, max_value=3)
refresh_sec = s4.number_input("Kitne Sec Me Check Kare?", value=30, min_value=10, max_value=120)

# ============ AUTO ON / OFF BUTTON ============
col_auto1, col_auto2 = st.columns([2, 1])
with col_auto1:
    if not st.session_state["auto_on"]:
        if st.button("🤖 AUTO ON Karo - Ab Auto Trade Lega", use_container_width=True, type="primary"):
            st.session_state["auto_on"] = True
            st.session_state["start_balance"] = st.session_state["balance"]
            log("🤖 AUTO ON Ho Gaya - Ab NIFTY / BANKNIFTY / SENSEX Ko Scan Karega")
            st.rerun()
    else:
        if st.button("🛑 AUTO OFF Karo - Roko", use_container_width=True):
            st.session_state["auto_on"] = False
            log("🛑 AUTO OFF Kar Diya - Ab Naya Order Nahi Lega")
            st.rerun()
with col_auto2:
    st.metric("AUTO Status", "🟢 ON - Chal Raha Hai" if st.session_state["auto_on"] else "🔴 OFF")

# ============ FUNCTIONS - DELTA GAMMA THETA ============
INSTRUMENT_MAP = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank", "SENSEX": "BSE_INDEX|SENSEX"}
STEP_MAP = {"NIFTY": 50, "BANKNIFTY": 100, "SENSEX": 100}
LOT_MAP = {"NIFTY": 25, "BANKNIFTY": 25, "SENSEX": 10}

def get_quote(key):
    h = {"Authorization": f"Bearer {st.session_state['token']}", "Accept": "application/json"}
    try:
        r = requests.get("https://api.upstox.com/v2/market-quote/quotes", headers=h, params={"instrument_key": key}, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json().get("data", {})
        if not data:
            return None
        return list(data.values())[0]
    except:
        return None

def greeks(spot, strike, is_ce=True, days=2):
    """Delta Gamma Theta - Black Scholes se - Asli Formula"""
    if spot <= 0 or strike <= 0:
        return 0, 0, 0, 0
    r, iv, T = 0.065, 0.13, max(days/365.0, 0.001)
    try:
        d1 = (math.log(spot/strike) + (r + 0.5*iv*iv)*T) / (iv*math.sqrt(T))
        d2 = d1 - iv*math.sqrt(T)
        N = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
        n_d1 = math.exp(-0.5*d1*d1) / math.sqrt(2*math.pi)  # PDF
        ce = spot*N(d1) - strike*math.exp(-r*T)*N(d2)
        pe = strike*math.exp(-r*T)*N(-d2) - spot*N(-d1)
        if is_ce:
            delta = N(d1)
            price = ce
        else:
            delta = N(d1) - 1
            price = pe
        gamma = n_d1 / (spot * iv * math.sqrt(T))
        theta = -(spot * n_d1 * iv) / (2*math.sqrt(T)) - r*strike*math.exp(-r*T)*N(d2 if is_ce else -d2)
        # Theta ko per-day me convert
        theta_per_day = theta / 365.0
        return round(price, 2), round(delta, 3), round(gamma, 5), round(theta_per_day, 2)
    except:
        return 0, 0, 0, 0

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.time()
    return (t.hour > 9 or (t.hour == 9 and t.minute >= 15)) and (t.hour < 15 or (t.hour == 15 and t.minute <= 30))

def decide_trade(sym, ltp, open_p):
    """Teeno Symbol Ka Analysis - Delta Gamma Theta Se"""
    move = ((ltp-open_p)/open_p*100) if open_p else 0
    step = STEP_MAP[sym]
    atm = int(round(ltp/step)*step)
    ce_price, ce_delta, ce_gamma, ce_theta = greeks(ltp, atm, True)
    pe_price, pe_delta, pe_gamma, pe_theta = greeks(ltp, atm, False)
    # Strategy Logic - Tumhari Wali
    # MODE 1 - DELTA: Tez Move + Delta Strong + Gamma High = BUY
    # MODE 3 - THETA: Shant Market + Theta Ghis Raha = SELL
    if move > 0.30 and ce_delta > 0.45 and ce_gamma > 0.0003:
        return {
            "signal": "BUY_CE", "strike": atm, "price": ce_price, "delta": ce_delta,
            "gamma": ce_gamma, "theta": ce_theta, "move": round(move,3),
            "reason": f"MODE 1 DELTA - Upar {move:.2f}% Delta {ce_delta} Gamma {ce_gamma} Strong",
            "target_pct": 30, "sl_pct": 12
        }
    if move < -0.30 and abs(pe_delta) > 0.45 and pe_gamma > 0.0003:
        return {
            "signal": "BUY_PE", "strike": atm, "price": pe_price, "delta": pe_delta,
            "gamma": pe_gamma, "theta": pe_theta, "move": round(move,3),
            "reason": f"MODE 1 DELTA - Neeche {move:.2f}% Delta {pe_delta} Gamma {pe_gamma} Strong",
            "target_pct": 30, "sl_pct": 12
        }
    if abs(move) < 0.15 and ce_theta < -2.0:
        # Shant hai - Theta kha raha hai - SELL karke Theta kamao
        return {
            "signal": "SELL_CE", "strike": atm, "price": ce_price, "delta": ce_delta,
            "gamma": ce_gamma, "theta": ce_theta, "move": round(move,3),
            "reason": f"MODE 3 THETA - Shant {move:.2f}% Theta {ce_theta}/day Ghis Raha - SELL Karke Kamao",
            "target_pct": 20, "sl_pct": 10
        }
    return None

# ============ DASHBOARD ============
total_pnl = st.session_state["balance"] - st.session_state["start_balance"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Balance", f"₹{st.session_state['balance']:.2f}")
c2.metric("Day P&L", f"₹{total_pnl:.2f}")
c3.metric("Open Orders", len([o for o in st.session_state["orders"] if o["status"]=="OPEN"]))
c4.metric("Market", "OPEN 🟢" if is_market_open() else "CLOSED 🔴")
st.caption(f"Welcome {st.session_state['user']} | Capital ₹{capital} | Max Per Trade ₹{max_per_trade} | Auto Har {refresh_sec} Sec Me Scan Karega")

# ============ AUTO LOOP - YAHI ASLI KAAM HAI ============
if st.session_state["auto_on"]:
    st.info(f"🤖 AUTO ON Hai - Har {refresh_sec} Sec Me NIFTY / BANKNIFTY / SENSEX Scan Ho Raha Hai - Page Khud Refresh Hoga - VPS Pe Band Mat Karna!")
    # 1. Pehle Open Orders Ka Profit Book Check Karo - Delta Gamma Theta Se
    for o in list(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        q = get_quote(INSTRUMENT_MAP[o["symbol"]])
        if q is None:
            continue
        ltp = float(q.get("last_price", 0) or 0)
        cur_price, cur_delta, cur_gamma, cur_theta = greeks(ltp, o["strike"], is_ce=("CE" in o["signal"]))
        # Live PnL
        if o["signal"].startswith("BUY"):
            pnl = (cur_price - o["entry"]) * o["qty"]
            pnl_pct = ((cur_price - o["entry"])/o["entry"]*100) if o["entry"] else 0
        else:
            pnl = (o["entry"] - cur_price) * o["qty"]
            pnl_pct = ((o["entry"] - cur_price)/o["entry"]*100) if o["entry"] else 0
        # Profit Book Logic - Delta Gamma Theta Se
        exit_reason = ""
        if o["signal"].startswith("BUY"):
            if cur_price >= o["target"]:
                exit_reason = f"🎯 TARGET Hit - Price {cur_price} >= Target {o['target']}"
            elif cur_price <= o["stoploss"]:
                exit_reason = f"🛑 SL Hit - Price {cur_price} <= SL {o['stoploss']}"
            elif abs(cur_delta) < 0.30:
                exit_reason = f"⚠️ DELTA Kamzor Ho Gaya {cur_delta} - Ab Tez Nahi Bhagega - Book Kar Lo"
            elif cur_theta < -5.0 and pnl > 0:
                exit_reason = f"⚠️ THETA Bahut Tez Ghis Raha {cur_theta}/day - Profit Hai Toh Book Kar Lo"
            elif pnl_pct > 45:
                exit_reason = f"🔥 45%+ Profit Ho Gaya - Lalach Mat Karo - Book Kar Lo"
        else: # SELL
            if cur_price <= o["target"]:
                exit_reason = f"🎯 TARGET Hit SELL Me"
            elif cur_price >= o["stoploss"]:
                exit_reason = f"🛑 SL Hit SELL Me"
            elif cur_gamma > 0.001 and pnl < 0:
                exit_reason = f"⚠️ GAMMA Blast Ho Raha {cur_gamma} - SELL Me Khatra - Nikal Jao"
        if exit_reason:
            st.session_state["balance"] += pnl
            o["status"] = "CLOSED"
            o["pnl"] = round(pnl, 2)
            o["exit_price"] = cur_price
            o["exit_reason"] = exit_reason
            log(f"✅ SQUARE OFF {o['symbol']} {o['strike']} {o['signal']} PnL ₹{pnl:.2f} - {exit_reason}")
            st.success(f"Auto Square Off! {o['symbol']} PnL ₹{pnl:.2f} - {exit_reason}")

    # 2. Naye Order Ke Liye Scan Karo - Sirf Agar Jagah Hai
    open_count = len([o for o in st.session_state["orders"] if o["status"]=="OPEN"])
    if open_count < max_open and is_market_open():
        for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
            # Pehle se is symbol me order hai toh skip
            if any(o["symbol"]==sym and o["status"]=="OPEN" for o in st.session_state["orders"]):
                continue
            q = get_quote(INSTRUMENT_MAP[sym])
            if q is None:
                continue
            ltp = float(q.get("last_price", 0) or 0)
            open_p = float((q.get("ohlc", {}) or {}).get("open", ltp) or ltp)
            trade = decide_trade(sym, ltp, open_p)
            if trade is None:
                continue
            # 10K Range Check - Lot Size Ke Hisaab Se
            lot = LOT_MAP[sym]
            # Kitne Lot Le Sakte Hai - Max Per Trade Ke Andar
            lots = int(max_per_trade // (trade["price"] * lot))
            if lots < 1:
                log(f"⏭️ {sym} Skip - Price ₹{trade['price']} x Lot {lot} = ₹{trade['price']*lot:.0f} > Max ₹{max_per_trade} - 10K Range Ke Bahar Hai")
                continue
            if lots > 3:
                lots = 3
            qty = lots * lot
            cost = trade["price"] * qty
            if cost > st.session_state["balance"]:
                log(f"⏭️ {sym} Skip - Balance Kam Hai Cost ₹{cost:.0f} > Balance ₹{st.session_state['balance']:.0f}")
                continue
            # Target / SL
            if trade["signal"].startswith("BUY"):
                tgt = round(trade["price"] * (1 + trade["target_pct"]/100), 2)
                sl = round(trade["price"] * (1 - trade["sl_pct"]/100), 2)
            else:
                tgt = round(trade["price"] * (1 - trade["target_pct"]/100), 2)
                sl = round(trade["price"] * (1 + trade["sl_pct"]/100), 2)
            st.session_state["orders"].append({
                "symbol": sym, "strike": trade["strike"], "signal": trade["signal"],
                "entry": trade["price"], "qty": qty, "target": tgt, "stoploss": sl,
                "status": "OPEN", "time": datetime.now().strftime("%d-%m %H:%M"),
                "pnl": 0.0, "delta": trade["delta"], "gamma": trade["gamma"], "theta": trade["theta"],
                "reason": trade["reason"]
            })
            log(f"🟢 AUTO ORDER {sym} {trade['strike']} {trade['signal']} Entry ₹{trade['price']} Qty {qty} Lot {lots} Target ₹{tgt} SL ₹{sl} - {trade['reason']}")
            st.success(f"🤖 AUTO Order Lag Gaya! {sym} {trade['signal']} Entry ₹{trade['price']} Qty {qty}")
            break  # Ek baar me ek hi order - Agle refresh me dusra
    elif not is_market_open():
        log("Market BAND Hai - Auto Wait Kar Raha Hai - Kal 9:15 Pe Shuru Hoga")
    # Auto Refresh - Har X Sec Me Khud Refresh
    time.sleep(refresh_sec)
    st.rerun()

# ============ MANUAL OPTION CHAIN BHI RAHEGA - DEKHNE KE LIYE ============
st.subheader("📊 Live Option Chain - Dekhne Ke Liye")
tab = st.radio("Index", ["NIFTY", "BANKNIFTY", "SENSEX"], horizontal=True, label_visibility="collapsed")
if st.button(f"🔄 {tab} Ka Chain Dekho", use_container_width=True):
    q = get_quote(INSTRUMENT_MAP[tab])
    if q is None:
        st.error("Data Nahi Mila - Token Check Karo")
    else:
        ltp = float(q.get("last_price", 0) or 0)
        open_p = float((q.get("ohlc", {}) or {}).get("open", ltp) or ltp)
        move = ((ltp-open_p)/open_p*100) if open_p else 0
        step = STEP_MAP[tab]
        atm = int(round(ltp/step)*step)
        st.session_state["chain"] = {"ltp": ltp, "move": move, "atm": atm, "tab": tab}
        chain = []
        for i in range(-4, 5):
            strike = atm + i*step
            ce, ce_d, ce_g, ce_t = greeks(ltp, strike, True)
            pe, pe_d, pe_g, pe_t = greeks(ltp, strike, False)
            chain.append({"strike": strike, "ce": ce, "pe": pe, "ce_d": ce_d, "pe_d": pe_d, "ce_t": ce_t, "pe_t": pe_t, "is_atm": i==0})
        st.session_state["chain"]["rows"] = chain

if st.session_state.get("chain", {}).get("rows"):
    ch = st.session_state["chain"]
    st.write(f"**{ch['tab']}** LTP: {ch['ltp']} | Move: {ch['move']:.2f}% | ATM: {ch['atm']}")
    st.markdown("""<div class="oc-head"><div style="flex:1;">CALL LTP | Delta | Theta</div><div style="flex:1;">STRIKE</div><div style="flex:1;">PUT LTP | Delta | Theta</div></div>""", unsafe_allow_html=True)
    for r in ch["rows"]:
        cls = "oc-row-atm" if r["is_atm"] else "oc-row"
        atm_tag = " • ATM" if r["is_atm"] else ""
        st.markdown(f"""<div class="{cls}"><div style="flex:1;"><span class="ce-btn">₹{r['ce']}</span><div class="small">Δ {r['ce_d']} Θ {r['ce_t']}</div></div><div style="flex:1;"><b>{r['strike']}{atm_tag}</b></div><div style="flex:1;"><span class="pe-btn">₹{r['pe']}</span><div class="small">Δ {r['pe_d']} Θ {r['pe_t']}</div></div></div>""", unsafe_allow_html=True)

# ============ ORDERS ============
st.subheader("📋 Orders • Positions")
tab1, tab2 = st.tabs(["🟢 Open", "✅ History + Logs"])
with tab1:
    opens = [o for o in st.session_state["orders"] if o["status"]=="OPEN"]
    if not opens:
        st.write("Koi Open Order Nahi Hai - AUTO ON Karo, Market Khulte Hi Lega")
    for idx, o in enumerate(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        q = get_quote(INSTRUMENT_MAP[o["symbol"]])
        cur = o["entry"]
        cur_delta = o.get("delta", 0)
        if q is not None:
            ltp = float(q.get("last_price", 0) or 0)
            cur, cur_delta, _, _ = greeks(ltp, o["strike"], is_ce=("CE" in o["signal"]))
        pnl = (cur - o["entry"])*o["qty"] if o["signal"].startswith("BUY") else (o["entry"]-cur)*o["qty"]
        st.markdown(f"""<div class="card"><b>{o['symbol']} {o['strike']} {o['signal']}</b> • Qty {o['qty']} • {o['time']}<br>Entry ₹{o['entry']} → Abhi ₹{cur} • Target ₹{o['target']} • SL ₹{o['stoploss']}<br>Delta {cur_delta} • Live P&L <b>₹{pnl:.2f}</b><br><span class="small">{o.get('reason','')}</span></div>""", unsafe_allow_html=True)
        if st.button(f"❌ Manual Square Off - {o['symbol']} {o['strike']} - PnL ₹{pnl:.2f}", key=f"mexit_{idx}", use_container_width=True):
            st.session_state["balance"] += pnl
            o["status"] = "CLOSED"
            o["pnl"] = round(pnl, 2)
            o["exit_price"] = cur
            o["exit_reason"] = "Manual Square Off"
            log(f"Manual Square Off {o['symbol']} PnL ₹{pnl:.2f}")
            st.rerun()
with tab2:
    st.write("**📜 Auto Logs - Kya-Kya Kiya Auto Ne**")
    for l in st.session_state["logs"]:
        st.write(l)
    st.divider()
    closed = [o for o in st.session_state["orders"] if o["status"]=="CLOSED"]
    if closed:
        for o in closed:
            st.write(f"{o['symbol']} {o['strike']} {o['signal']} Entry ₹{o['entry']} → Exit ₹{o.get('exit_price','-')} PnL ₹{o['pnl']} - {o.get('exit_reason','')}")
        st.write(f"**Total Day P&L: ₹{st.session_state['balance']-st.session_state['start_balance']:.2f}**")
    else:
        st.write("Abhi Koi Closed Nahi Hai")

if st.button("🔄 Sab Reset Karo - Balance 10000", use_container_width=True):
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["logs"] = []
    st.session_state["auto_on"] = False
    st.rerun()

st.caption("💡 PAPER Hai - Real Paisa Nahi Katega! VPS Pe Chalane Ke Liye Neeche Wala Step Dekho!")
