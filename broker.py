# BASE BROKER - Har Broker Ke Liye Ek Jaisa Socket

class BaseBroker:
    def __init__(self, name):
        self.name = name

    def login(self):
        raise NotImplementedError("login() har broker me alag hoga")

    def get_option_chain(self, symbol):
        raise NotImplementedError

    def place_order(self, symbol, option_type, strike, qty, order_type="BUY"):
        raise NotImplementedError

    def get_order_status(self, order_id):
        raise NotImplementedError
