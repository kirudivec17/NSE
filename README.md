# FNO Paper Trading System

**Sirf NIFTY / BANKNIFTY / SENSEX - Sirf F&O - Sirf Paper Trade**

## Kya Hai Ye System?

Ye ek auto-trading system hai jo kisi bhi broker ke API se connect ho jata hai.
Pehle sirf PAPER TRADE karega - asli paisa nahi lagega.
Jab strategy jeetne lagegi, tabhi REAL mode ON karenge.

## Features

- **Koi Bhi Broker:** Tradejini / Zerodha / Angel / Dhan - Sirf API daalo, connect ho jayega
- **Sirf Index F&O:** NIFTY, BANKNIFTY, SENSEX ke Options hi trade honge
- **Paper Trade Mode:** Nakli order - Asli market price - Asli hisab
- **Risk Control:** Capital 10,000 - Max Loss 30% (3,000) - 7,000 pe aate hi Shutdown
- **Per Trade Loss:** Max 500 Rs
- **Daily Loss:** Max 1,000 Rs - Us din band

## Capital & Risk Rule

| Rule | Value |
| --- | --- |
| Capital | 10,000 Rs |
| Max Loss | 30% = 3,000 Rs |
| Shutdown Balance | 7,000 Rs |
| Per Trade Loss | 500 Rs |
| Daily Loss | 1,000 Rs |
| Profit Limit | No Limit - Jitna Nikal Sake |

## Files

- `main.py` - System yaha se chalega
- `config.py` - Capital, Mode, Broker setting
- `risk_manager.py` - 30% Shutdown wala guard
- `broker.py` - Har broker ke liye ek jaisa socket
- `strategy.py` - Trading strategy
- `paper_engine.py` - Nakli order - Asli hisab

## Kaise Chalaye?

1. `config.py` me apna Broker aur MODE = "PAPER" rakho
2. `main.py` chalao
3. System signal ka wait karega

## Mode

- `MODE = "PAPER"` - Nakli trade, asli hisab (Abhi yehi chal raha hai)
- `MODE = "REAL"` - Asli trade, asli paisa (Baad me jab strategy jeetegi)

## Note

Pehle strategy ko Paper me prove karo.
Paper me 15-20 din jeet gayi to hi Real pe jana hai.
