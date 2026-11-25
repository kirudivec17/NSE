# MAIN - REAL PAPER - Koi Fake Price / Fake Exit Nahi
# Market Band Ho Toh NO TRADE - Sirf 9:15 - 3:30 Me Chalega

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

    print("\nSystem Ready Hai - Sirf REAL Data Pe Chalega...")
    print("Market Band Hai Toh Naya Trade Nahi Hoga - Sirf Hold Dikhayega\n")

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

                # 2. Market band hai toh NAYA order mat lo
                # Lekin purana khula hua order hai toh usko check karte raho
                is_open = chain.get("market_open", True)
                open_orders = [o for o in paper.get_open_orders() if o["symbol"] == symbol]

                if is_open == False and not open_orders:
                    print(f"{symbol} - Market BAND hai - Naya Trade Nahi Karenge - Kal 9:15 Pe Chalayenge")
                    continue

                if is_open == False and open_orders:
                    print(f"{symbol} - Market BAND hai - Naya Trade Nahi, Bas Purana Order Dekh Rahe Hai")
                    # Neeche exit check pe jane do, naya order mat lo

                # 3. Agar order khula hai to uska LIVE price check karo - Exit ke liye
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

                # 4. Market band hai toh yaha tak aane ke baad bhi naya order mat lo
                if is_open == False:
                    continue

                # 5. Koi order nahi khula + Market khula hai to naya signal lo
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
                else:
                    print(f"{symbol} - Koi Signal Nahi - Wait Kar Rahe Hai")

            print(f"Balance: {risk.balance} | Day PnL: {risk.day_pnl} | Open: {len(paper.get_open_orders())}")
            print("10 sec wait - Real price ke liye...\n")
            time.sleep(10)
            round_no += 1

    except KeyboardInterrupt:
        print("\nTumne Roka - System Band...")
        print(f"Final Balance: {risk.balance}")
        print(f"Total PnL: {risk.total_pnl}")
        print(f"Total Paper Orders: {len(paper.orders)}")
        # Saare khule order dikhao
        for o in paper.get_open_orders():
            print(f"OPEN: {o['symbol']} {o['side']} {o['type']} @ {o['entry_price']} Target {o['target']} SL {o['stoploss']}")

if __name__ == "__main__":
    main()
