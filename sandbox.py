import csv
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

TRADES_FILE = "trades.csv"

class VirtualWallet:
    def __init__(self, initial_usd=10000.0, fee_rate=0.001):
        self.balance = {"USD": initial_usd}
        self.fee_rate = fee_rate # 0.1% standard exchange fee
        self.history = []
        self._load_history()

    def _load_history(self):
        """Loads trade history and reconstructs portfolio state."""
        if not os.path.exists(TRADES_FILE):
            self._init_trade_log()
            return

        with open(TRADES_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Reconstruct balances if needed, or just keep history
                # For simplicity in this script, we trust the CSV or current state
                # Ideally, we should replay the CSV to get the current balance
                pass
        
        # NOTE: For a persistent wallet, we'd need to save/load the 'balance' dictionary 
        # to a separate JSON file (wallet_state.json). 
        # For now, we'll start fresh or assume in-memory for the session.

    def _init_trade_log(self):
        with open(TRADES_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "action", "asset", "quantity", "price", "fee_usd", "total_cost", "usd_balance_after"])

    def get_net_worth(self, current_prices):
        """Calculates total value (USD + Assets * CurrentPrice)."""
        total_value = self.balance["USD"]
        
        for asset, qty in self.balance.items():
            if asset == "USD": continue
            
            price = current_prices.get(asset, 0)
            if price > 0:
                asset_val = qty * price
                total_value += asset_val
                
        return total_value

    def buy(self, asset, price_usd, amount_usd):
        """Executes a Virtual Buy."""
        if self.balance["USD"] < amount_usd:
            logger.warning(f"  [!] Insufficient Funds for BUY {asset}. Have: ${self.balance['USD']:.2f}")
            return False
            
        # Fee Calculation
        fee = amount_usd * self.fee_rate
        actual_spend = amount_usd - fee
        quantity = actual_spend / price_usd
        
        # Update Balance
        self.balance["USD"] -= amount_usd
        self.balance[asset] = self.balance.get(asset, 0) + quantity
        
        # Log Trade
        self._log_trade("BUY", asset, quantity, price_usd, fee, amount_usd)
        
        logger.info(f"  [PAPER TRADE] BOUGHT {quantity:.4f} {asset.upper()} @ ${price_usd:,.2f} | Fee: ${fee:.2f}")
        return True

    def sell(self, asset, price_usd, quantity_percent=1.0):
        """Executes a Virtual Sell (percent of holdings)."""
        qty_held = self.balance.get(asset, 0)
        if qty_held <= 0:
            return False
            
        qty_to_sell = qty_held * quantity_percent
        gross_return = qty_to_sell * price_usd
        fee = gross_return * self.fee_rate
        net_return = gross_return - fee
        
        # Update Balance
        self.balance[asset] -= qty_to_sell
        self.balance["USD"] += net_return
        
        # Log Trade
        self._log_trade("SELL", asset, qty_to_sell, price_usd, fee, net_return)
        
        logger.info(f"  [PAPER TRADE] SOLD {qty_to_sell:.4f} {asset.upper()} @ ${price_usd:,.2f} | PnL: +${net_return:.2f}")
        return True

    def _log_trade(self, action, asset, quantity, price, fee, total):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(TRADES_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, action, asset, quantity, price, fee, total, self.balance["USD"]])

if __name__ == "__main__":
    # Test the Wallet
    wallet = VirtualWallet()
    print(f"Initial Balance: ${wallet.balance['USD']}")
    
    # Simulate Prices
    prices = {"bitcoin": 95000.0, "ethereum": 3500.0}
    
    # Buy 0.1 BTC ($9,500 worth usually, but let's buy $5000 worth)
    wallet.buy("bitcoin", 95000.0, 5000.0)
    
    print(f"Post-Buy Balance: ${wallet.balance['USD']:.2f}")
    print(f"BTC Held: {wallet.balance['bitcoin']:.6f}")
    
    # Calculate Net Worth
    nw = wallet.get_net_worth(prices)
    print(f"Net Worth (Immediate): ${nw:.2f} (Loss due to fees)")
    
    # Simulate Price Pump (BTC goes to 100k)
    new_prices = {"bitcoin": 100000.0}
    nw_pump = wallet.get_net_worth(new_prices)
    print(f"Net Worth (BTC @ 100k): ${nw_pump:.2f}")
    
    # Sell All
    wallet.sell("bitcoin", 100000.0)
    print(f"Final Balance: ${wallet.balance['USD']:.2f}")
