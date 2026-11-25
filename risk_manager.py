# RISK MANAGER - Paisa Bachane Wala Guard

import config

class RiskManager:
    def __init__(self):
        self.capital = config.CAPITAL
        self.balance = config.CAPITAL
        self.day_pnl = 0
        self.total_pnl = 0
        self.shutdown = False

    def can_trade(self):
        # 7000 pe aate hi band
        if self.balance <= config.SHUTDOWN_BALANCE:
            self.shutdown = True
            print(f"SHUTDOWN! Balance {self.balance} - 30% Loss Ho Gaya!")
            return False
        # Din ka 1000 loss ho gaya to band
        if self.day_pnl <= -config.MAX_LOSS_PER_DAY:
            print(f"Daily Loss Limit! Aaj Band!")
            return False
        if self.shutdown:
            return False
        return True

    def update_pnl(self, pnl):
        self.balance += pnl
        self.day_pnl += pnl
        self.total_pnl += pnl
        print(f"Balance: {self.balance} | Day PnL: {self.day_pnl} | Total PnL: {self.total_pnl}")
        return self.can_trade()
