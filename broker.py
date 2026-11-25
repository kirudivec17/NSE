# BASE BROKER - Har Broker Ko Ye 4 Kaam Aane Hi Chahiye

class BaseBroker:
    def __init__(self, name):
        self.name = name

    def login(self):
        # Login karna - Har broker apne hisab se karega
        raise NotImplementedError("login() har broker me alag hoga")

    def get_option_chain(self, symbol):
        # NIFTY / BANKNIFTY / SENSEX ki Option Chain dena
        raise NotImplementedError

    def place_order(self, symbol, option_type, strike, qty, order_type="BUY"):
        # Order lagana - PAPER me nakli, REAL me asli
        raise NotImplementedError

    def get_order_status(self, order_id):
        # Order ka status batana
        raise NotImplementedError
