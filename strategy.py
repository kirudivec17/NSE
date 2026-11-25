# STRATEGY - SAHI WALA - Pichle Din Ka Move Dekh Ke Signal
# Aaj ka Move Subah Pata Nahi Hota - Isliye Pichla Din Use Karenge

class Strategy:
    def __init__(self):
        self.mode = "WAIT"
        self.prev_move = 0.0

    def get_mode(self):
        return self.mode

    def get_signal(self, symbol, chain):
        # chain me ab 'move' = Aaj ka Move hai - Live me ye galat hoga
        # Isliye hum yaha 'prev_move' use karenge - Jo main.py se aayega
        # Agar main.py ne prev_move nahi bheja toh chain ka move use kar lo
        move = chain.get("prev_move", chain.get("move", 0))
        delta = chain.get("delta", 0)
        gamma = chain.get("gamma", 0)
        theta = chain.get("theta", 0)

        # MODE 1 - DELTA - Pichle Din Market Tez Hila Tha
        if move > 0.3:
            self.mode = "MODE 1 - DELTA"
            return "BUY_CE"
        if move < -0.3:
            self.mode = "MODE 1 - DELTA"
            return "BUY_PE"

        # MODE 3 - THETA - Market Shant Tha
        # Gamma wala Mode 2 hata diya - Kyuki Backtest me wo loss de raha tha
        self.mode = "MODE 3 - THETA"
        return "SELL_CE"
