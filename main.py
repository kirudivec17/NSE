# MAIN - FINAL VERSION - Paper + Risk + Upstox + Strategy Sab Ek Saath

import config
import time
from risk_manager import RiskManager
from strategy import Strategy
from paper_engine import PaperEngine
from upstox import UpstoxBroker

def main():
    print("==========================================")
    print("=== FNO PAPER TRADING SYSTEM - FINAL ===")
    print("==========================================")
    print(f"Mode: {config.MODE}")
    print(f"Broker: {config.BROKER_NAME}")
    print(f"Capital: {config.CAPITAL}")
    print(f"Max Loss: {config.MAX_LOSS_AMOUNT} (30%)")
    print(f"Shutdown Balance: {config.SHUTDOWN_BALANCE}")
    print(f"Symbols: {config.SYMBOLS}")
    print("==========================================")

    # 1. RISK GUARD ON KARO
    risk = RiskManager()
    if not risk.can_trade():
        print("System Band Hai - Risk Limit Cross!")
        return

    # 2. BROKER CONNECT KARO - PAPER ME SIRF CHECK HOGA
    broker = UpstoxBroker()
    if config.MODE == "REAL":
        # REAL me hi asli login chahiye
        # PAPER me login fail bhi ho to chalega
        if not broker.login():
            print("Broker Login Fail - REAL Mode Me Bina Login Ke Nahi Chalega!")
            return
    else:
        print("PAPER MODE - Broker Login Ki Zarurat Nahi - Nakli Order Chalega")
        broker.login()  # Try karega, fail hua to bhi chalega

    # 3. STRATEGY + PAPER ENGINE ON KARO
    strategy = Strategy()
    paper = PaperEngine()

    print("\nSystem Ready Hai - Trading Shuru...")
    print("Rokne ke liye Ctrl + C Dabao\n")

    # 4. LOOP - Har Symbol Pe Signal Check Karo
    try:
        round_no = 1
        while True:
            print(f"--- Round {round_no} ---")

            # Risk check - Har round pe
            if not risk.can_trade():
                print("Risk Limit Cross - System Band Kar Raha Hu!")
                break

            for symbol in config.SYMBOLS:
                # Option Chain lao - Abhi dummy hai
                chain = broker.get_option_chain(symbol)

                # Strategy se signal lo
                # Abhi Strategy NO_TRADE degi - Tumhari wali aate hi trade hoga
                signal = strategy.get_signal(symbol, chain)

                print(f"{symbol} -> Signal: {signal}")

                # Agar signal aaya to Paper Order lagao
                if signal in ["BUY_CE", "BUY_PE"]:
                    # Example values - Baad me asli Strike / Price aayega
                    option_type = "CE" if signal == "BUY_CE" else "PE"
                    strike = 25000  # TODO: Strategy se asli strike aayega
                    qty = 25  # NIFTY Lot - BANKNIFTY me 15, SENSEX me 10
                    price = 100  # TODO: Asli premium aayega

                    order_id = paper.place_order(symbol, option_type, strike, qty, price)

                    # Dummy exit - Test ke liye - Baad me asli exit logic aayega
                    # Abhi test: 105 pe exit karke PnL dekho
                    # pnl = paper.exit_order(order_id, 105)
                    # risk.update_pnl(pnl)

                elif signal == "NO_TRADE":
                    print(f"{symbol} me Abhi Trade Nahi Hai - Wait Kar Raha Hu...")

            print(f"Balance: {risk.balance} | Day PnL: {risk.day_pnl}")
            print("5 sec wait...\n")
            time.sleep(5)
            round_no += 1

    except KeyboardInterrupt:
        print("\nTumne Roka - System Band Kar Raha Hu...")
        print(f"Final Balance: {risk.balance}")
        print(f"Total PnL: {risk.total_pnl}")
        print(f"Total Paper Orders: {len(paper.orders)}")

if __name__ == "__main__":
    main()
