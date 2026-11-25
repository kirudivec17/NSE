# MAIN - REAL PAPER - Koi Fake Price / Fake Exit Nahi

import config
import time
from risk_manager import RiskManager
from strategy import Strategy
from paper_engine import PaperEngine
from upstox import UpstoxBroker

def main():
    print("==========================================")
    print("=== FNO PAPER TRADING - REAL PRICE ===")
    print("==========================================")
    print(f"Mode: {config.MODE} (Paper = Real Price, Nakli Paisa)")
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
    broker.login()

    strategy = Strategy()
    paper = PaperEngine()

    print("\nSystem Ready Hai - Sirf REAL Data Pe Chalega...\n")

    try:
        round_no = 1
        while True:
            print(f"--- Round {round_no} ---")
            if not risk.can_trade():
                print("Risk Limit Cross - System Band!")
                break

            for symbol in config.SYMBOLS:
                # 1. Pehle asli data lao
                chain = broker.get_option_chain(symbol)
                if chain is None:
                    print(f"{symbol} - Data nahi mila, skip - Fake trade nahi karenge")
                    continue

                # 2. Agar order khula hai to uska LIVE price check karo - Exit ke liye
                open_orders = [o for o in paper.get_open_orders() if o["symbol"] == symbol]
                if open_orders:
                    o = open_orders[0]
                    # Us option ka asli live price - CE hai to CE price, PE hai to PE price
                    live_price = chain["ce_price"] if o["type"] == "CE" else chain["pe_price"]
                    print(f"{symbol} OPEN Order ID {o['id']} Entry {o['entry_price']} Live {live_price} Target {o['target']} SL {o['stoploss']}")
                    pnl = paper.check_exit(o, live_price)
                    if pnl is not None:
                        risk.update_pnl(pnl)
                    else:
                        print(f"{symbol} - Abhi Target / SL nahi aaya - Hold")
                    continue

                # 3. Koi order nahi khula to naya signal lo
                signal = strategy.get_signal(symbol, chain)
                print(f"{symbol} -> Signal: {signal} | Mode: {strategy.get_mode()}")

                if signal in ["BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]:
                    # Asli price - Signal ke hisab se CE ya PE
                    real_price = chain["ce_price"] if "CE" in signal else chain["pe_price"]
                    real_strike = chain["strike"]
                    if not real_price or real_price <= 0:
                        print(f"{symbol} - Asli price 0 hai - Trade nahi karenge")
                        continue
                    paper.place_order(symbol, signal, real_strike, 25, real_price)

            print(f"Balance: {risk.balance} | Day PnL: {risk.day_pnl} | Open: {len(paper.get_open_orders())}")
            print("10 sec wait - Real price ke liye...\n")
            time.sleep(10)
            round_no += 1

    except KeyboardInterrupt:
        print("\nTumne Roka - System Band...")
        print(f"Final Balance: {risk.balance}")
        print(f"Total PnL: {risk.total_pnl}")
        print(f"Total Paper Orders: {len(paper.orders)}")

if __name__ == "__main__":
    main()
