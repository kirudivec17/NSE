# MAIN - Yaha Se System Chalega

import config
from risk.risk_manager import RiskManager
from strategy.strategy import Strategy

print("=== FNO Paper Trading System ON ===")
print(f"Mode: {config.MODE}")
print(f"Capital: {config.CAPITAL}")
print(f"Shutdown Balance: {config.SHUTDOWN_BALANCE}")
print(f"Symbols: {config.SYMBOLS}")
print(f"Broker: {config.BROKER_NAME}")

risk = RiskManager()
strategy = Strategy()

if not risk.can_trade():
    print("System Band Hai - Risk Limit Cross!")
else:
    print("System Ready Hai - Strategy Signal Ka Wait Kar Raha Hai...")
    # Yaha se loop chalega - Price aayega -> Signal aayega -> Paper Trade hoga
