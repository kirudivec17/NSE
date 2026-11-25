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

    risk = RiskManager()
    if not risk.can_trade():
        print("System Band Hai - Risk Limit Cross!")
        return

    broker = UpstoxBroker()
    if config.MODE == "REAL":
        if not broker.login():
            print("Broker Login Fail - REAL Mode Me Bina Login Ke Nahi Chalega!")
            return
    else:
        print("PAPER MODE - Broker Login Ki Zarurat Nahi - Nakli Order Chalega")
        broker.login()

    strategy = Strategy()
    paper = PaperEngine()

    print("\nSystem Ready Hai - Trading Shuru...")
    print("Rokne ke liye Ctrl + C Dabao\n")

    try:
        round_no = 1
        while True:
            print(f"--- Round {round_no} ---")

            if not risk.can_trade():
                print("Risk Limit Cross - System Band Kar Raha Hu!")
                break

            for symbol in config.SYMBOLS:
                chain = broker.get_option_chain(symbol)
                signal = strategy.get_signal(symbol, chain)
                print(f"{symbol} -> Signal: {signal} | Mode: {strategy.get_mode()}")

                if signal in ["BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]:
                    strike = 25000
                    qty = 25
                    price = 100
                    order_id = paper.place_order(symbol, signal, strike, qty, price)
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
