# MAIN - FINAL VERSION - Fixed - Ek Symbol Pe Ek Hi Order

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
            print("Broker Login Fail!")
            return
    else:
        print("PAPER MODE - Broker Login Ki Zarurat Nahi")
        broker.login()

    strategy = Strategy()
    paper = PaperEngine()

    print("\nSystem Ready Hai - Trading Shuru...\n")

    try:
        round_no = 1
        while True:
            print(f"--- Round {round_no} ---")

            if not risk.can_trade():
                print("Risk Limit Cross - System Band!")
                break

            for symbol in config.SYMBOLS:
                # Agar is symbol ka order pehle se khula hai - To naya signal mat lo
                if paper.has_open_order(symbol):
                    print(f"{symbol} -> Pehle se OPEN hai - Wait kar rahe hai exit ke liye")
                    continue

                chain = broker.get_option_chain(symbol)
                signal = strategy.get_signal(symbol, chain)
                print(f"{symbol} -> Signal: {signal} | Mode: {strategy.get_mode()}")

                if signal in ["BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]:
                    strike = 25000
                    qty = 25
                    price = 100
                    paper.place_order(symbol, signal, strike, qty, price)

            # Test ke liye - Har 3rd round pe saare open order band karke PnL dekho
            # Asli me ye exit Stoploss / Target pe hoga
            if round_no % 3 == 0:
                for o in list(paper.get_open_orders()):
                    # SELL wale me 90 pe exit = (100-90)*25 = +250 profit
                    # BUY wale me 110 pe exit = (110-100)*25 = +250 profit
                    exit_price = 90 if o["side"] == "SELL" else 110
                    pnl = paper.exit_order(o["id"], exit_price)
                    risk.update_pnl(pnl)

            print(f"Balance: {risk.balance} | Day PnL: {risk.day_pnl} | Open: {len(paper.get_open_orders())}")
            print("5 sec wait...\n")
            time.sleep(5)
            round_no += 1

    except KeyboardInterrupt:
        print("\nTumne Roka - System Band...")
        print(f"Final Balance: {risk.balance}")
        print(f"Total PnL: {risk.total_pnl}")
        print(f"Total Paper Orders: {len(paper.orders)}")

if __name__ == "__main__":
    main()
