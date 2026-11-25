# STRATEGY - Sirf F&O Index Ke Liye

class Strategy:
    def __init__(self):
        self.name = "FNO Index Strategy"

    def get_signal(self, symbol, price_data):
        # Yaha Tumhari Strategy Aayegi
        # Abhi ke liye simple - Baad me tumhari wali daal denge
        # Return: "BUY_CE" / "BUY_PE" / "NO_TRADE"
        # Example:
        # Agar price up ja raha hai -> BUY_CE
        # Agar price down ja raha hai -> BUY_PE
        # Nahi to NO_TRADE

        # TODO: Tumhari purani strategy yaha daalni hai
        return "NO_TRADE"
