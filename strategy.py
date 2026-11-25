# STRATEGY - DELTA + GAMMA + THETA - 1 Fail Toh 2, 2 Fail Toh 3

class Strategy:
    def __init__(self):
        self.name = "Greeks Fallback Strategy"
        self.current_mode = "NONE"

    def get_signal(self, symbol, price_data):
        # price_data me abhi dummy hai - Baad me Upstox se asli Greeks aayenge
        # Yaha hum 3 mode try karenge - Ek ek karke

        # Tumhare hisab se values - Baad me tune kar lenge
        # Ye values example hai - Asli market se aayengi
        delta = price_data.get("delta", 0) if isinstance(price_data, dict) else 0
        gamma = price_data.get("gamma", 0) if isinstance(price_data, dict) else 0
        theta = price_data.get("theta", 0) if isinstance(price_data, dict) else 0
        market_move = price_data.get("move", 0) if isinstance(price_data, dict) else 0

        # --- MODE 1: DELTA - Direction ---
        # Agar market 0.3% se zyada hil gaya -> Direction pakdo
        if abs(market_move) > 0.3:
            self.current_mode = "MODE 1 - DELTA"
            if market_move > 0:
                print(f"MODE 1 DELTA: Market UP {market_move}% -> BUY_CE")
                return "BUY_CE"
            else:
                print(f"MODE 1 DELTA: Market DOWN {market_move}% -> BUY_PE")
                return "BUY_PE"

        # MODE 1 FAIL - Market slow hai - Ab MODE 2 try karo

        # --- MODE 2: GAMMA - Speed ---
        # Agar gamma high hai - Matlab option tez bhagega
        if gamma > 0.001:
            self.current_mode = "MODE 2 - GAMMA"
            # Gamma me direction nahi dekhte - Jo side tez hai usko pakdo
            # Yaha pe market ka chhota move bhi kaafi hai
            if market_move >= 0:
                print(f"MODE 2 GAMMA: Gamma High {gamma} -> BUY_CE (Fast)")
                return "BUY_CE"
            else:
                print(f"MODE 2 GAMMA: Gamma High {gamma} -> BUY_PE (Fast)")
                return "BUY_PE"

        # MODE 2 FAIL - Gamma bhi low hai - Ab MODE 3 try karo

        # --- MODE 3: THETA - Sideways ---
        # Market shant hai - Kuch nahi ho raha - Theta se kamao
        # Yaha BUY nahi - SELL karna hai - Paper me hum SELL ko alag se dikhayenge
        # Abhi ke liye signal SELL_CE de rahe hai - Paper engine me isko handle karenge
        self.current_mode = "MODE 3 - THETA"
        print(f"MODE 3 THETA: Market Shant - Theta {theta} -> SELL_CE (Time Decay)")
        return "SELL_CE"

    def get_mode(self):
        return self.current_mode
