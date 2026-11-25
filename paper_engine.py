# PAPER ENGINE - REAL - Koi Fake Exit Nahi

class PaperEngine:
    def __init__(self):
        self.orders = []
        self.order_id = 1000

    def has_open_order(self, symbol):
        for o in self.orders:
            if o["symbol"] == symbol and o["status"] == "PAPER - OPEN":
                return True
        return False

    def place_order(self, symbol, signal, strike, qty, price):
        if self.has_open_order(symbol):
            print(f"SKIP: {symbol} ka order pehle se khula hai")
            return None
        if not price or price <= 0:
            print(f"SKIP: {symbol} ka asli price nahi mila - Fake price pe trade nahi karenge")
            return None

        self.order_id += 1
        if signal.startswith("BUY"):
            side = "BUY"
            option_type = signal.replace("BUY_", "")
        elif signal.startswith("SELL"):
            side = "SELL"
            option_type = signal.replace("SELL_", "")
        else:
            return None

        # REAL Stoploss / Target - Price se hi banega, haath se nahi
        # BUY me: Target = +20%, SL = -10%
        # SELL me: Target = -20% (price girega to profit), SL = +10%
        if side == "BUY":
            target = price * 1.20
            stoploss = price * 0.90
        else:
            target = price * 0.80
            stoploss = price * 1.10

        order = {
            "id": self.order_id,
            "symbol": symbol,
            "side": side,
            "type": option_type,
            "strike": strike,
            "qty": qty,
            "entry_price": price,
            "target": round(target, 2),
            "stoploss": round(stoploss, 2),
            "status": "PAPER - OPEN"
        }
        self.orders.append(order)
        print(f"PAPER ORDER: {side} {symbol} {option_type} {strike} @ REAL {price} Qty {qty} | Target: {round(target,2)} SL: {round(stoploss,2)} | ID: {self.order_id}")
        return self.order_id

    def check_exit(self, order, live_price):
        # Live price Target ya SL ko chhuye tabhi exit - warna NO EXIT
        if not live_price or live_price <= 0:
            return None
        if order["side"] == "BUY":
            if live_price >= order["target"]:
                return self.exit_order(order["id"], live_price, "TARGET HIT")
            if live_price <= order["stoploss"]:
                return self.exit_order(order["id"], live_price, "STOPLOSS HIT")
        else: # SELL
            if live_price <= order["target"]:
                return self.exit_order(order["id"], live_price, "TARGET HIT")
            if live_price >= order["stoploss"]:
                return self.exit_order(order["id"], live_price, "STOPLOSS HIT")
        return None

    def exit_order(self, order_id, exit_price, reason="MANUAL"):
        for o in self.orders:
            if o["id"] == order_id and o["status"] == "PAPER - OPEN":
                if o["side"] == "BUY":
                    pnl = (exit_price - o["entry_price"]) * o["qty"]
                else:
                    pnl = (o["entry_price"] - exit_price) * o["qty"]
                o["status"] = "CLOSED"
                o["exit_price"] = exit_price
                o["pnl"] = pnl
                o["exit_reason"] = reason
                print(f"PAPER EXIT: ID {order_id} {o['side']} {o['type']} @ REAL {exit_price} | {reason} | PnL: {pnl}")
                return pnl
        return 0

    def get_open_orders(self):
        return [o for o in self.orders if o["status"] == "PAPER - OPEN"]

    def get_total_pnl(self):
        return sum([o.get("pnl", 0) for o in self.orders if o["status"] == "CLOSED"])
