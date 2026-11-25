# PAPER ENGINE - Nakli Order - Asli Hisab

class PaperEngine:
    def __init__(self):
        self.orders = []
        self.order_id = 1000

    def place_order(self, symbol, option_type, strike, qty, price):
        # Asli order nahi jayega - sirf copy pe likhega
        self.order_id += 1
        order = {
            "id": self.order_id,
            "symbol": symbol,
            "type": option_type,
            "strike": strike,
            "qty": qty,
            "buy_price": price,
            "status": "PAPER - OPEN"
        }
        self.orders.append(order)
        print(f"PAPER ORDER: {symbol} {option_type} {strike} @ {price} Qty {qty} | ID: {self.order_id}")
        return self.order_id

    def exit_order(self, order_id, exit_price):
        for o in self.orders:
            if o["id"] == order_id:
                pnl = (exit_price - o["buy_price"]) * o["qty"]
                o["status"] = "CLOSED"
                o["exit_price"] = exit_price
                o["pnl"] = pnl
                print(f"PAPER EXIT: ID {order_id} @ {exit_price} | PnL: {pnl}")
                return pnl
        return 0
