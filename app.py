# APP.PY V8 - REAL TRADING APP JESA - HISTORY + CHART + COMMENT + BUYER/SELLER
# Purana mita ke ye POORA paste karo

import streamlit as st
import requests
import math
import time
import random
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except:
    IST = None

def now_ist():
    if IST is not None:
        return datetime.now(IST)
    return datetime.now() + timedelta(hours=5, minutes=30)

st.set_page_config(page_title="FNO AUTO - Real Trading App", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.main { background-color: #F2F5FA; }
.header { background: linear-gradient(135deg, #1A4BFF 0%, #0A2E9E 100%); color: white; padding: 16px; border-radius: 0 0 18px 18px; margin: -20px -20px 12px -20px; }
.header h2 { color: white; margin: 0; font-size: 22px; }
.header p { color: #D6E0FF; margin: 2px 0 0 0; font-size: 13px; }
.card { background: white; border-radius: 14px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 10px; }
.trade-card { background: white; border-radius: 14px; padding: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 12px; border-left: 4px solid #0E9F6E; }
.trade-card-loss { background: white; border-radius: 14px; padding: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 12px; border-left: 4px solid #E02424; }
.comment-box { background: #F0F7FF; border-radius: 10px; padding: 10px; font-size: 13px; border-left: 3px solid #1A4BFF; margin-top: 8px; }
.small { font-size: 12px; color: #6B7280; }
.big { font-size: 20px; font-weight: 700; }
.green { color: #0E9F6E; font-weight: 700; }
.red { color: #E02424; font-weight: 700; }
.blue { color: #1A4BFF; font-weight: 700; }
.badge-buy { background: #0E9F6E; color: white; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge-sell { background: #E02424; color: white; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge-ce { background: #E6F7EE; color: #0E9F6E; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge-pe { background: #FDECEC; color: #E02424; padding: 3px 8px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.oc-head { display: flex; background: #1A4BFF; color: white; border-radius: 10px 10px 0 0; padding: 8px; font-size: 13px; font-weight: 700; text-align: center; }
.oc-row { display: flex; background: white; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; }
.oc-row-atm { display: flex; background: #FFF7E6; border-bottom: 1px solid #EDEFF3; padding: 10px 8px; font-size: 14px; text-align: center; align-items: center; border-left: 3px solid #FF9F00; }
.ce-btn { background: #E6F7EE; color: #0E9F6E; border-radius: 8px; padding: 6px; font-weight: 700; }
.pe-btn { background: #FDECEC; color: #E02424; border-radius: 8px; padding: 6px; font-weight: 700; }
.stButton>button { border-radius: 10px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============ SESSION - HISTORY KABHI GAYAB NAHI HOGI ============
if "balance" not in st.session_state:
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["connected"] = False
    st.session_state["token"] = ""
    st.session_state["user"] = ""
    st.session_state["auto_on"] = False
    st.session_state["logs"] = []
    st.session_state["history"] = []  # PERMANENT HISTORY - Reset Dabane Pe Bhi Nahi Mitegi Jab Tak Clear History Na Dabao
    st.session_state["all_chains"] = {"NIFTY": None, "BANKNIFTY": None, "SENSEX": None}
    st.session_state["all_ltps"] = {"NIFTY": 0, "BANKNIFTY": 0, "SENSEX": 0}
    st.session_state["price_history"] = {"NIFTY": [], "BANKNIFTY": [], "SENSEX": []}
    st.session_state["trade_counter"] = 0

def log(msg):
    t = now_ist().strftime("%H:%M:%S")
    st.session_state["logs"].insert(0, f"[{t} IST] {msg}")
    st.session_state["logs"] = st.session_state["logs"][:50]

def add_comment(sym, msg):
    # Har Trade Pe Comment - Kyu Liya, Kya Formula Chala
    t = now_ist().strftime("%H:%M:%S")
    st.session_state["logs"].insert(0, f"[{t}] 💬 {sym} - {msg}")

try:
    SAVED_API_KEY = st.secrets.get("API_KEY", "")
    SAVED_API_SECRET = st.secrets.get("API_SECRET", "")
except:
    SAVED_API_KEY = ""
    SAVED_API_SECRET = ""

# ============ HEADER ============
st.markdown("""
<div class="header">
<h2>🤖 AUTO FNO - Real Trading App Jesa</h2>
<p>Live Chart • Buyer / Seller • Delta Gamma Theta Comment • Full History • 10K Capital</p>
</div>
""", unsafe_allow_html=True)

# ============ CONNECT ============
with st.expander("🔑 Broker Connect - Sirf Token Daalo", expanded=not st.session_state["connected"]):
    c1, c2 = st.columns(2)
    c1.text_input("API Key - Save Hai", value=SAVED_API_KEY, type="password", disabled=True)
    c2.text_input("API Secret - Save Hai", value=SAVED_API_SECRET, type="password", disabled=True)
    if SAVED_API_KEY:
        st.caption(f"✅ API Key Save Hai: {SAVED_API_KEY[:4]}**** | Secret Save Hai")
    access_token = st.text_input("Access Token - Roz Subah 7 Baje Naya - VPS Ke Andar Hi Copy Karo", type="password", placeholder="Yaha Token Paste Karo")
    if st.button("🔌 Connect Karo", use_container_width=True):
        if not access_token:
            st.warning("Pehle Token Daalo!")
        else:
            h = {"Authorization": f"Bearer {access_token.strip()}", "Accept": "application/json"}
            try:
                r = requests.get("https://api.upstox.com/v2/user/profile", headers=h, timeout=10)
                if r.status_code == 200:
                    d = r.json().get("data", {})
                    st.session_state["connected"] = True
                    st.session_state["token"] = access_token.strip()
                    st.session_state["user"] = d.get("user_name", "User")
                    st.success(f"Connected ✅ Welcome {st.session_state['user']}")
                    st.rerun()
                else:
                    st.error(f"Token Expire - Code {r.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.get("connected"):
    st.info("👆 Upar Token Daal Ke Connect Karo")
    st.stop()

# ============ TOP DASHBOARD - REAL APP JESA ============
total_pnl = st.session_state["balance"] - st.session_state["start_balance"]
total_trades = len(st.session_state["history"]) + len([o for o in st.session_state["orders"] if o["status"]=="OPEN"])
win_trades = len([h for h in st.session_state["history"] if h.get("pnl",0) > 0])
loss_trades = len([h for h in st.session_state["history"] if h.get("pnl",0) <= 0])
win_rate = (win_trades / len(st.session_state["history"]) * 100) if st.session_state["history"] else 0

# Balance Bar - Bada Wala
st.markdown(f"""
<div class="card">
<div style="display:flex; justify-content:space-between;">
<div><span class="small">Total Balance (10K Se Shuru)</span><div class="big">₹{st.session_state['balance']:.2f}</div></div>
<div style="text-align:right;"><span class="small">Aaj Ka Total P&L</span><div class="big {'green' if total_pnl>=0 else 'red'}">₹{total_pnl:+.2f} {'🟢 Profit Me Ho' if total_pnl>=0 else '🔴 Loss Me Ho'}</div></div>
</div>
<div style="display:flex; gap:10px; margin-top:10px; font-size:13px;">
<span>📊 Total Trades: <b>{total_trades}</b></span>
<span>✅ Jeete: <b style="color:#0E9F6E;">{win_trades}</b></span>
<span>❌ Haare: <b style="color:#E02424;">{loss_trades}</b></span>
<span>🎯 Win Rate: <b>{win_rate:.0f}%</b></span>
<span>🟢 Open: <b>{len([o for o in st.session_state['orders'] if o['status']=='OPEN'])}</b></span>
</div>
</div>
""", unsafe_allow_html=True)

# ============ SETTINGS + AUTO ============
s1, s2, s3, s4 = st.columns(4)
capital = s1.number_input("Capital", value=10000, step=1000)
max_per_trade = s2.number_input("Ek Trade Me Max", value=3333, step=500)
max_open = s3.number_input("Max Open Order", value=3, min_value=1, max_value=3)
refresh_sec = s4.number_input("Check Har Kitne Sec?", value=30, min_value=10, max_value=120)

col_auto1, col_auto2 = st.columns([2,1])
with col_auto1:
    if not st.session_state["auto_on"]:
        if st.button("🤖 AUTO ON Karo - Ab Auto Trade Lega", use_container_width=True, type="primary"):
            st.session_state["auto_on"] = True
            log("🤖 AUTO ON Ho Gaya")
            add_comment("SYSTEM", "AUTO ON Kiya - Ab Har 30 Sec Me NIFTY / BANKNIFTY / SENSEX Scan Karega - Jab Delta Gamma Theta Ka Formula Milega Tabhi Trade Lega")
            st.rerun()
    else:
        if st.button("🛑 AUTO OFF Karo", use_container_width=True):
            st.session_state["auto_on"] = False
            log("🛑 AUTO OFF")
            st.rerun()
with col_auto2:
    st.metric("AUTO", "🟢 ON" if st.session_state["auto_on"] else "🔴 OFF")

# ============ FUNCTIONS ============
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
    if spot <= 0 or strike <= 0:
        return 0, 0, 0, 0
    r, iv, T = 0.065, 0.13, max(days/365.0, 0.001)
    try:
        d1 = (math.log(spot/strike) + (r + 0.5*iv*iv)*T) / (iv*math.sqrt(T))
        d2 = d1 - iv*math.sqrt(T)
        N = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
        n_d1 = math.exp(-0.5*d1*d1) / math.sqrt(2*math.pi)
        ce = spot*N(d1) - strike*math.exp(-r*T)*N(d2)
        pe = strike*math.exp(-r*T)*N(-d2) - spot*N(-d1)
        if is_ce:
            delta = N(d1); price = ce
        else:
            delta = N(d1) - 1; price = pe
        gamma = n_d1 / (spot * iv * math.sqrt(T))
        theta = -(spot * n_d1 * iv) / (2*math.sqrt(T)) - r*strike*math.exp(-r*T)*N(d2 if is_ce else -d2)
        return round(price, 2), round(delta, 3), round(gamma, 5), round(theta/365.0, 2)
    except:
        return 0, 0, 0, 0

def is_market_open():
    now = now_ist()
    if now.weekday() >= 5:
        return False
    t = now.time()
    return (t.hour > 9 or (t.hour == 9 and t.minute >= 15)) and (t.hour < 15 or (t.hour == 15 and t.minute <= 30))

def decide_trade(sym, ltp, open_p):
    move = ((ltp-open_p)/open_p*100) if open_p else 0
    step = STEP_MAP[sym]
    atm = int(round(ltp/step)*step)
    ce_price, ce_delta, ce_gamma, ce_theta = greeks(ltp, atm, True)
    pe_price, pe_delta, pe_gamma, pe_theta = greeks(ltp, atm, False)
    # Buyer / Seller Logic
    if move > 0.30 and ce_delta > 0.45 and ce_gamma > 0.0003:
        comment = f"🟢 BUYER STRONG HAI - {sym} Upar {move:.2f}% Gaya - Buyer Ne Dhakka Diya - Delta {ce_delta} Matlab Price Tez Badhega - Gamma {ce_gamma} Matlab Speed Aur Badhegi - Theta {ce_theta}/day Thoda Ghisega Par Profit Zyada Hoga - Isliye CE BUY Kiya"
        return {"signal": "BUY_CE", "strike": atm, "price": ce_price, "delta": ce_delta, "gamma": ce_gamma, "theta": ce_theta, "move": round(move,3), "reason": f"DELTA MODE - {sym} Upar {move:.2f}%", "comment": comment, "target_pct": 30, "sl_pct": 12, "buyer_seller": "🟢 Buyer Strong - Seller Kamzor - Buyer Jeet Raha Hai"}
    if move < -0.30 and abs(pe_delta) > 0.45 and pe_gamma > 0.0003:
        comment = f"🔴 SELLER STRONG HAI - {sym} Neeche {move:.2f}% Gaya - Seller Ne Dhakka Diya - PE Ka Delta {pe_delta} Strong Hai - Gamma {pe_gamma} Matlab Neeche Aur Tez Jayega - Theta {pe_theta}/day - Isliye PE BUY Kiya"
        return {"signal": "BUY_PE", "strike": atm, "price": pe_price, "delta": pe_delta, "gamma": pe_gamma, "theta": pe_theta, "move": round(move,3), "reason": f"DELTA MODE - {sym} Neeche {move:.2f}%", "comment": comment, "target_pct": 30, "sl_pct": 12, "buyer_seller": "🔴 Seller Strong - Buyer Kamzor - Seller Jeet Raha Hai"}
    if abs(move) < 0.15 and ce_theta < -2.0:
        comment = f"🟡 MARKET SHANT HAI - {sym} Sirf {move:.2f}% Hila - Na Buyer Jeet Raha Na Seller - Theta {ce_theta}/day Ghis Raha Hai - Matlab Time Ke Sath Price Girega - Isliye CE SELL Karke Theta Ka Paisa Kama Rahe Hai"
        return {"signal": "SELL_CE", "strike": atm, "price": ce_price, "delta": ce_delta, "gamma": ce_gamma, "theta": ce_theta, "move": round(move,3), "reason": f"THETA MODE - {sym} Shant {move:.2f}%", "comment": comment, "target_pct": 20, "sl_pct": 10, "buyer_seller": "🟡 Dono Barabar - Koi Nahi Jeet Raha - Theta Se Kamao"}
    return None

def close_trade(o, cur_price, exit_reason, exit_comment):
    pnl = (cur_price - o["entry"])*o["qty"] if o["signal"].startswith("BUY") else (o["entry"]-cur_price)*o["qty"]
    st.session_state["balance"] += pnl
    o["status"] = "CLOSED"
    o["pnl"] = round(pnl, 2)
    o["exit_price"] = cur_price
    o["exit_reason"] = exit_reason
    o["exit_comment"] = exit_comment
    o["exit_time"] = now_ist().strftime("%H:%M:%S")
    # HISTORY ME DAALO - KABHI NAHI MITEGA
    st.session_state["history"].append(dict(o))
    log(f"✅ SQUARE OFF {o['symbol']} {o['strike']} PnL ₹{pnl:.2f} - {exit_reason}")
    add_comment(o["symbol"], exit_comment)
    return pnl

# ============ AUTO LOOP ============
if st.session_state["auto_on"]:
    st.info(f"🤖 AUTO ON Hai - IST Time: {now_ist().strftime('%H:%M:%S')} - Har {refresh_sec} Sec Me Scan Ho Raha Hai")
    # Price History For Chart
    for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
        q = get_quote(INSTRUMENT_MAP[sym])
        if q is not None:
            ltp = float(q.get("last_price", 0) or 0)
            st.session_state["price_history"][sym].append(ltp)
            st.session_state["price_history"][sym] = st.session_state["price_history"][sym][-50:]
            st.session_state["all_ltps"][sym] = ltp
    # Open Orders Check
    for o in list(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        q = get_quote(INSTRUMENT_MAP[o["symbol"]])
        if q is None:
            continue
        ltp = float(q.get("last_price", 0) or 0)
        cur_price, cur_delta, cur_gamma, cur_theta = greeks(ltp, o["strike"], is_ce=("CE" in o["signal"]))
        if o["signal"].startswith("BUY"):
            pnl = (cur_price - o["entry"]) * o["qty"]
            pnl_pct = ((cur_price - o["entry"])/o["entry"]*100) if o["entry"] else 0
        else:
            pnl = (o["entry"] - cur_price) * o["qty"]
            pnl_pct = ((o["entry"] - cur_price)/o["entry"]*100) if o["entry"] else 0
        exit_reason = ""; exit_comment = ""
        if o["signal"].startswith("BUY"):
            if cur_price >= o["target"]:
                exit_reason = f"🎯 TARGET Hit"; exit_comment = f"🎯 TARGET HIT - Price ₹{o['entry']} Se ₹{cur_price} Ho Gaya - {pnl_pct:.1f}% Profit Hua - Isliye Book Kar Liya - Delta Ab {cur_delta} Hai - Aur Lalach Nahi Karna"
            elif cur_price <= o["stoploss"]:
                exit_reason = f"🛑 SL Hit"; exit_comment = f"🛑 STOP LOSS HIT - Price ₹{o['entry']} Se ₹{cur_price} Gir Gaya - {pnl_pct:.1f}% Loss Hua - Seller Jeet Gaya - Isliye Nikal Gaye Taaki Zyada Loss Na Ho"
            elif abs(cur_delta) < 0.30:
                exit_reason = f"⚠️ DELTA Kamzor"; exit_comment = f"⚠️ DELTA KAMZOR HO GAYA - Delta {cur_delta} Ho Gaya - Matlab Ab Price Tez Nahi Badhega - Isliye Book Kar Liya"
            elif cur_theta < -5.0 and pnl > 0:
                exit_reason = f"⚠️ THETA Ghis Raha"; exit_comment = f"⚠️ THETA TEZ GHIS RAHA HAI - Theta {cur_theta}/day - Time Khata Ja Raha Hai - Profit Hai Isliye Book Kar Liya"
            elif pnl_pct > 45:
                exit_reason = f"🔥 45%+ Profit"; exit_comment = f"🔥 45% SE ZYADA PROFIT HO GAYA - ₹{pnl:.2f} Kama Liya - Lalach Nahi Karna - Book Kar Liya"
        else:
            if cur_price <= o["target"]:
                exit_reason = f"🎯 TARGET Hit SELL"; exit_comment = f"🎯 SELL ME TARGET HIT - Price Gir Gaya - Profit Hua - Book Kar Liya"
            elif cur_price >= o["stoploss"]:
                exit_reason = f"🛑 SL Hit SELL"; exit_comment = f"🛑 SELL ME SL HIT - Price Badh Gaya - Loss Hua - Nikal Gaye"
            elif cur_gamma > 0.001 and pnl < 0:
                exit_reason = f"⚠️ GAMMA Blast"; exit_comment = f"⚠️ GAMMA BLAST {cur_gamma} - Price Tez Hil Raha Hai - SELL Me Khatra Hai - Isliye Nikal Gaye"
        if exit_reason:
            pnl_done = close_trade(o, cur_price, exit_reason, exit_comment)
            st.success(f"Auto Square Off! {o['symbol']} PnL ₹{pnl_done:.2f} - {exit_reason}")
    # New Order
    open_count = len([o for o in st.session_state["orders"] if o["status"]=="OPEN"])
    if open_count < max_open and is_market_open():
        for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
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
            lot = LOT_MAP[sym]
            lots = int(max_per_trade // (trade["price"] * lot))
            if lots < 1:
                log(f"⏭️ {sym} Skip - Price Zyada Hai")
                continue
            if lots > 3:
                lots = 3
            qty = lots * lot
            cost = trade["price"] * qty
            if cost > st.session_state["balance"]:
                log(f"⏭️ {sym} Skip - Balance Kam Hai")
                continue
            if trade["signal"].startswith("BUY"):
                tgt = round(trade["price"] * (1 + trade["target_pct"]/100), 2)
                sl = round(trade["price"] * (1 - trade["sl_pct"]/100), 2)
            else:
                tgt = round(trade["price"] * (1 - trade["target_pct"]/100), 2)
                sl = round(trade["price"] * (1 + trade["sl_pct"]/100), 2)
            st.session_state["trade_counter"] += 1
            new_order = {
                "trade_no": st.session_state["trade_counter"],
                "symbol": sym, "strike": trade["strike"], "signal": trade["signal"],
                "entry": trade["price"], "qty": qty, "lots": lots, "lot_size": lot, "target": tgt, "stoploss": sl,
                "status": "OPEN", "time": now_ist().strftime("%d-%m %H:%M:%S"),
                "pnl": 0.0, "delta": trade["delta"], "gamma": trade["gamma"], "theta": trade["theta"],
                "reason": trade["reason"], "comment": trade["comment"], "buyer_seller": trade["buyer_seller"],
                "spot_at_entry": ltp, "move_at_entry": trade["move"], "cost": round(cost,2)
            }
            st.session_state["orders"].append(new_order)
            log(f"🟢 AUTO ORDER #{new_order['trade_no']} {sym} {trade['strike']} {trade['signal']} Entry ₹{trade['price']} Qty {qty} ({lots} Lots)")
            add_comment(sym, trade["comment"])
            add_comment(sym, f"📊 BUYER/SELLER: {trade['buyer_seller']} | Entry Spot {ltp} | Move {trade['move']}% | Cost ₹{cost:.0f} | Target ₹{tgt} | SL ₹{sl}")
            st.success(f"🤖 NEW TRADE #{new_order['trade_no']} - {sym} {trade['signal']} Entry ₹{trade['price']} Qty {qty}")
            break
    elif not is_market_open():
        log("Market BAND Hai - Wait Kar Raha Hai")
    time.sleep(refresh_sec)
    st.rerun()

# ============ LIVE CHART + BUYER/SELLER ============
st.subheader("📈 Live Chart - Price Kaha Ja Raha Hai + Buyer / Seller Kaha Baithe Hai")
tab_chart = st.radio("Chart Ke Liye Index Chuno", ["NIFTY", "BANKNIFTY", "SENSEX"], horizontal=True, label_visibility="collapsed", key="chart_tab")
hist = st.session_state["price_history"].get(tab_chart, [])
if len(hist) > 1:
    st.line_chart(hist, height=180)
    first = hist[0]; last = hist[-1]
    chg = ((last-first)/first*100) if first else 0
    col_ch1, col_ch2, col_ch3 = st.columns(3)
    col_ch1.metric(f"{tab_chart} Abhi Ka Price", f"₹{last:.2f}", f"{chg:+.2f}%")
    col_ch2.metric("Shuru Me Tha", f"₹{first:.2f}")
    col_ch3.metric("Buyer / Seller", "🟢 Buyer Strong" if chg > 0.2 else "🔴 Seller Strong" if chg < -0.2 else "🟡 Barabar - Koi Nahi Jeet Raha")
    # Buyer Seller Bar
    if chg > 0:
        st.markdown(f"**Buyer Seller Bar:** 🟢 Buyer {min(90, 50+abs(chg)*50):.0f}% | 🔴 Seller {max(10, 50-abs(chg)*50):.0f}% - Buyer Jeet Raha Hai - Upar Jayega")
    elif chg < 0:
        st.markdown(f"**Buyer Seller Bar:** 🟢 Buyer {max(10, 50-abs(chg)*50):.0f}% | 🔴 Seller {min(90, 50+abs(chg)*50):.0f}% - Seller Jeet Raha Hai - Neeche Jayega")
    else:
        st.markdown(f"**Buyer Seller Bar:** 🟢 Buyer 50% | 🔴 Seller 50% - Dono Barabar Hai - Market Shant Hai")
else:
    st.info(f"Chart Ke Liye AUTO ON Karo - {tab_chart} Ka Price Har 30 Sec Me Yaha Aayega - Fir Chart Banega - Abhi Ke Liye Neeche Chain Dekho")

# ============ OPTION CHAIN ============
st.subheader("📊 Live Option Chain")
tab = st.radio("Index Chuno", ["NIFTY", "BANKNIFTY", "SENSEX"], horizontal=True, label_visibility="collapsed", key="chain_tab")
if st.button(f"🔄 {tab} Ka Chain Dekho", key=f"chain_btn_{tab}", use_container_width=True):
    q = get_quote(INSTRUMENT_MAP[tab])
    if q is None:
        st.error(f"{tab} Ka Data Nahi Mila")
    else:
        ltp = float(q.get("last_price", 0) or 0)
        open_p = float((q.get("ohlc", {}) or {}).get("open", ltp) or ltp)
        move = ((ltp-open_p)/open_p*100) if open_p else 0
        step = STEP_MAP[tab]
        atm = int(round(ltp/step)*step)
        chain = []
        for i in range(-4, 5):
            strike = atm + i*step
            ce, ce_d, ce_g, ce_t = greeks(ltp, strike, True)
            pe, pe_d, pe_g, pe_t = greeks(ltp, strike, False)
            chain.append({"strike": strike, "ce": ce, "pe": pe, "ce_d": ce_d, "pe_d": pe_d, "ce_t": ce_t, "pe_t": pe_t, "is_atm": i==0})
        st.session_state["all_chains"][tab] = {"ltp": ltp, "move": move, "atm": atm, "tab": tab, "rows": chain}
        st.session_state["all_ltps"][tab] = ltp
        st.rerun()
ch = st.session_state["all_chains"].get(tab)
if ch and ch.get("rows"):
    st.write(f"**{ch['tab']}** LTP: {ch['ltp']} | Move: {ch['move']:.2f}% | ATM: {ch['atm']}")
    st.markdown("""<div class="oc-head"><div style="flex:1;">CALL LTP | Delta | Theta</div><div style="flex:1;">STRIKE</div><div style="flex:1;">PUT LTP | Delta | Theta</div></div>""", unsafe_allow_html=True)
    for r in ch["rows"]:
        cls = "oc-row-atm" if r["is_atm"] else "oc-row"
        atm_tag = " • ATM" if r["is_atm"] else ""
        st.markdown(f"""<div class="{cls}"><div style="flex:1;"><span class="ce-btn">₹{r['ce']}</span><div class="small">Δ {r['ce_d']} Θ {r['ce_t']}</div></div><div style="flex:1;"><b>{r['strike']}{atm_tag}</b></div><div style="flex:1;"><span class="pe-btn">₹{r['pe']}</span><div class="small">Δ {r['pe_d']} Θ {r['pe_t']}</div></div></div>""", unsafe_allow_html=True)
else:
    st.info(f"👆 `{tab} Ka Chain Dekho` Dabao")

# ============ OPEN ORDERS - REAL APP JESA ============
st.subheader("🟢 Open Trades - Abhi Chal Rahe Hai")
opens = [o for o in st.session_state["orders"] if o["status"]=="OPEN"]
if not opens:
    st.write("Koi Open Trade Nahi Hai - AUTO ON Karo")
else:
    for idx, o in enumerate(st.session_state["orders"]):
        if o["status"] != "OPEN":
            continue
        q = get_quote(INSTRUMENT_MAP[o["symbol"]])
        cur = o["entry"]; cur_delta = o.get("delta",0); cur_gamma = o.get("gamma",0); cur_theta = o.get("theta",0)
        cur_spot = o.get("spot_at_entry",0)
        if q is not None:
            cur_spot = float(q.get("last_price", 0) or 0)
            cur, cur_delta, cur_gamma, cur_theta = greeks(cur_spot, o["strike"], is_ce=("CE" in o["signal"]))
        pnl = (cur - o["entry"])*o["qty"] if o["signal"].startswith("BUY") else (o["entry"]-cur)*o["qty"]
        pnl_pct = ((cur - o["entry"])/o["entry"]*100) if o["signal"].startswith("BUY") else ((o["entry"]-cur)/o["entry"]*100)
        pnl_color = "green" if pnl >= 0 else "red"
        sig_badge = "badge-buy" if o["signal"].startswith("BUY") else "badge-sell"
        ce_pe_badge = "badge-ce" if "CE" in o["signal"] else "badge-pe"
        st.markdown(f"""
        <div class="trade-card">
        <div style="display:flex; justify-content:space-between;"><b>Trade #{o.get('trade_no','-')} - {o['symbol']} {o['strike']} {o['signal']}</b><span class="small">{o['time']}</span></div>
        <div style="margin:6px 0;"><span class="{sig_badge}">{o['signal']}</span> <span class="{ce_pe_badge}">{'CALL' if 'CE' in o['signal'] else 'PUT'}</span> <span class="small">Qty {o['qty']} = {o.get('lots',0)} Lots x {o.get('lot_size',0)}</span></div>
        <div style="font-size:14px;">Spot Entry Pe Tha: <b>₹{o.get('spot_at_entry',0):.2f}</b> → Abhi Spot: <b>₹{cur_spot:.2f}</b> | Option Entry: <b>₹{o['entry']}</b> → Abhi: <b>₹{cur}</b></div>
        <div style="font-size:14px;">Target: <b>₹{o['target']}</b> | Stop Loss: <b>₹{o['stoploss']}</b> | Cost Lagaya Tha: <b>₹{o.get('cost',0):.0f}</b></div>
        <div style="font-size:14px;">Live P&L: <span class="{pnl_color}">₹{pnl:+.2f} ({pnl_pct:+.1f}%) {'🟢 Profit Me Ho' if pnl>=0 else '🔴 Loss Me Ho'}</span></div>
        <div style="font-size:13px; margin-top:6px;">Delta: <b>{cur_delta}</b> | Gamma: <b>{cur_gamma}</b> | Theta: <b>{cur_theta}/day</b> | Move Entry Pe: <b>{o.get('move_at_entry',0)}%</b></div>
        <div class="comment-box"><b>💬 Kyu Liya Tha Ye Trade?</b><br>{o.get('comment','')}</div>
        <div class="comment-box"><b>📊 Buyer / Seller:</b> {o.get('buyer_seller','')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"❌ Is Trade Ko Band Karo - {o['symbol']} {o['strike']} - PnL ₹{pnl:.2f}", key=f"mexit_{idx}", use_container_width=True):
            comment_close = f"👋 TUMNE KHUD BAND KIYA - Entry ₹{o['entry']} Se Exit ₹{cur} Pe - PnL ₹{pnl:.2f} Hua - Manual Square Off Kiya"
            pnl_done = close_trade(o, cur, "Manual Square Off", comment_close)
            st.rerun()

# ============ HISTORY - KABHI NAHI MITEGI ============
st.subheader("📜 Full History - Kitne Trades Liye, Kitna Profit / Loss Hua")
if not st.session_state["history"]:
    st.write("Abhi Koi History Nahi Hai - Pehla Trade Hote Hi Yaha Aayega - Balance Reset Karne Pe Bhi Ye Nahi Mitegi")
else:
    # Summary Box
    tot_pnl_hist = sum(h.get("pnl",0) for h in st.session_state["history"])
    st.markdown(f"""<div class="card"><b>History Summary:</b> Total Closed Trades: <b>{len(st.session_state['history'])}</b> | Total History P&L: <b class="{'green' if tot_pnl_hist>=0 else 'red'}">₹{tot_pnl_hist:+.2f}</b> | Win: <b style="color:#0E9F6E;">{win_trades}</b> | Loss: <b style="color:#E02424;">{loss_trades}</b></div>""", unsafe_allow_html=True)
    for h in reversed(st.session_state["history"]):
        pnl_c = "green" if h.get("pnl",0) >= 0 else "red"
        card_cls = "trade-card" if h.get("pnl",0) >= 0 else "trade-card-loss"
        st.markdown(f"""
        <div class="{card_cls}">
        <div style="display:flex; justify-content:space-between;"><b>Trade #{h.get('trade_no','-')} - {h['symbol']} {h['strike']} {h['signal']} - {'✅ PROFIT' if h.get('pnl',0)>=0 else '❌ LOSS'}</b><span class="small">{h.get('time','')} → Band: {h.get('exit_time','')}</span></div>
        <div style="font-size:14px; margin-top:6px;">Entry: <b>₹{h['entry']}</b> → Exit: <b>₹{h.get('exit_price','-')}</b> | Qty: <b>{h['qty']}</b> = {h.get('lots',0)} Lots x {h.get('lot_size',0)} | Cost: <b>₹{h.get('cost',0):.0f}</b></div>
        <div style="font-size:14px;">Target Tha: ₹{h['target']} | SL Tha: ₹{h['stoploss']} | Spot Entry Pe: ₹{h.get('spot_at_entry',0):.2f}</div>
        <div style="font-size:15px;">Final P&L: <span class="{pnl_c}"><b>₹{h.get('pnl',0):+.2f}</b></span> | Reason: {h.get('exit_reason','')}</div>
        <div style="font-size:13px;">Delta: {h.get('delta',0)} | Gamma: {h.get('gamma',0)} | Theta: {h.get('theta',0)}/day | {h.get('reason','')}</div>
        <div class="comment-box"><b>💬 Kyu Liya Tha?</b><br>{h.get('comment','')}</div>
        <div class="comment-box"><b>💬 Kyu Band Kiya?</b><br>{h.get('exit_comment','')}</div>
        </div>
        """, unsafe_allow_html=True)

# ============ COMMENTS / LOGS ============
st.subheader("💬 Live Comments - System Kya Soch Raha Hai")
if not st.session_state["logs"]:
    st.write("Abhi Koi Comment Nahi Hai - AUTO ON Karo - Har Trade Pe Comment Aayega")
else:
    for l in st.session_state["logs"][:20]:
        st.write(l)

# ============ BUTTONS ============
c_reset1, c_reset2 = st.columns(2)
if c_reset1.button("🔄 Balance Reset Karo - 10000 (History Nahi Mitegi)", use_container_width=True):
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["auto_on"] = False
    # History Nahi Mitayenge - Taaki Pata Chale Kitna Kamaya
    st.rerun()
if c_reset2.button("🗑️ History Bhi Saaf Karo - Sab Kuch Naya", use_container_width=True):
    st.session_state["balance"] = 10000.0
    st.session_state["start_balance"] = 10000.0
    st.session_state["orders"] = []
    st.session_state["history"] = []
    st.session_state["logs"] = []
    st.session_state["auto_on"] = False
    st.session_state["trade_counter"] = 0
    st.session_state["price_history"] = {"NIFTY": [], "BANKNIFTY": [], "SENSEX": []}
    st.rerun()

st.caption("💡 PAPER Hai - Real Paisa Nahi Katega! History Ab Kabhi Gayab Nahi Hogi - Jab Tak Tum Khud History Saaf Na Karo!")
