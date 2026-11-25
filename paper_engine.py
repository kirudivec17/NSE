# PAPER ENGINE - FINAL - BUY + SELL Dono Samjhega

class PaperEngine:
    def __init__(self):
        self.orders = []
        self.order_id = 1000

    def has_open_order(self, symbol):
        # Is symbol ka koi order pehle se khula hai kya?
        for o in self.orders:
            if o["symbol"] == symbol and o["status"] == "PAPER - OPEN":
                return True
        return False

    def place_order(self, symbol, signal, strike, qty, price):
        # Pehle check karo - Agar pehle se khula hai to naya mat lagao
        if self.has_open_order(symbol):
            print(f"SKIP: {symbol} ka order pehle se khula hai - Naya nahi lagayenge")
            return None

        self.order_id += 1

        if signal.startswith("BUY"):
            side = "BUY"
            option_type = signal.replace("BUY_", "")
        elif signal.startswith("SELL"):
            side = "SELL"
            option_type = signal.replace("SELL_", "")
        else:
            side = "BUY"
            option_type = "CE"

        order = {
            "id": self.order_id,
            "symbol": symbol,
            "side": side,
            "type": option_type,
            "strike": strike,
            "qty": qty,
            "entry_price": price,
            "status": "PAPER - OPEN"
        }
        self.orders.append(order)
        print(f"PAPER ORDER: {side} {symbol} {option_type} {strike} @ {price} Qty {qty} | ID: {self.order_id}")
        return self.order_id

    def exit_order(self, order_id, exit_price):
        for o in self.orders:
            if o["id"] == order_id and o["status"] == "PAPER - OPEN":
                if o["side"] == "BUY":
                    pnl = (exit_price - o["entry_price"]) * o["qty"]
                else:
                    pnl = (o["entry_price"] - exit_price) * o["qty"]

                o["status"] = "CLOSED"
                o["exit_price"] = exit_price
                o["pnl"] = pnl
                print(f"PAPER EXIT: ID {order_id} {o['side']} {o['type']} @ {exit_price} | PnL: {pnl}")
                return pnl
        return 0

    def get_open_orders(self):
        return [o for o in self.orders if o["status"] == "PAPER - OPEN"]

    def get_total_pnl(self):
        return sum([o.get("pnl", 0) for o in self.orders if o["status"] == "CLOSED"])
