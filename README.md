# DHAN - TRIPLE FILTER AI SYSTEM 🚀

**ORB + VWAP + Supertrend + PCR + Greeks - Teen Strategy Ek Saath**

> SEBI Data: 87.7% F&O Traders Loss Karte Hai. Ye System Loss Rokne Ke Liye Bana Hai, Profit Baad Me.

---

## 🎯 Strategy Kya Hai?

Teen Best Strategy ko Merge kiya hai:

| Filter | Kya Karta Hai? | Rule |
| :--- | :--- | :--- |
| **1. ORB** | Entry Timing | 9:15-9:30 ka High/Low Tootne Pe Hi Trade |
| **2. VWAP + Supertrend + PCR** | Direction | Price > VWAP + Supertrend Green + PCR > 1.2 = BUY CE |
| **3. Greeks + OI** | Strike Selection | Sirf Delta 0.50-0.65 wala Strike, Theta < 20 |

**Agar 5 me se 5 Condition HAAN, Tabhi Trade. Ek bhi NA = NO TRADE.**

---

## 🛡️ Risk Management

- **Per Trade SL:** 40% Premium (100 ka liya toh 60 pe Exit)
- **Target 1:** 50% Profit pe 50% Book
- **Target 2:** 100% Profit pe Baaki Book
- **Time SL:** 20 Min me Trade nahi bhaaga toh Exit - Theta kha jayega
- **Daily Max Loss:** -₹5,000 pe System Band
- **Daily Max Profit:** +₹10,000 pe System Band
- **Max Trades:** 2 / Day
- **Auto Square-Off:** 3:15 PM

---

## 📦 Installation

```bash
git clone https://github.com/TUMHARA_NAAM/dhan-triple-filter-ai.git
cd dhan-triple-filter-ai
pip install -r requirements.txt
