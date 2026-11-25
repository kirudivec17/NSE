# STRATEGY - DELTA + GAMMA + THETA - 1 Fail Toh 2, 2 Fail Toh 3

class Strategy:
    def __init__(self):
        self.name = "Greeks Fallback Strategy"
        self.current_mode = "NONE"

    def get_signal(self, symbol, price_data):
        # price_data dict hai - Upstox se aayega
        if not isinstance(price_data, dict):
            price_data = {}

        delta = price_data.get("delta", 0)
        gamma = price_data.get("gamma", 0)
        theta = price_data.get("theta", 0)
        market_move = price_data.get("move", 0)

        # --- MODE 1: DELTA - Direction ---
        if abs(market_move) > 0.3:
            self.current_mode = "MODE 1 - DELTA"
            if market_move > 0:
                print(f"MODE 1 DELTA: Market UP {market_move}% -> BUY_CE")
                return "BUY_CE"
            else:
                print(f"MODE 1 DELTA: Market DOWN {market_move}% -> BUY_PE")
                return "BUY_PE"

        # --- MODE 2: GAMMA - Speed ---
        if gamma > 0.001:
            self.current_mode = "MODE 2 - GAMMA"
            if market_move >= 0:
                print(f"MODE 2 GAMMA: Gamma High {gamma} -> BUY_CE (Fast)")
                return "BUY_CE"
            else:
                print(f"MODE 2 GAMMA: Gamma High {gamma} -> BUY_PE (Fast)")
                return "BUY_PE"

        # --- MODE 3: THETA - Sideways ---
        self.current_mode = "MODE 3 - THETA"
        print(f"MODE 3 THETA: Market Shant - Theta {theta} -> SELL_CE (Time Decay)")
        return "SELL_CE"

    def get_mode(self):
        return self.current_mode
