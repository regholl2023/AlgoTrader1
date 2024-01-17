from alpaca.trading.client import TradingClient
from alpaca.common import RawData
from alpaca.broker.client import Asset
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import yfinance
from env import alpacaId, alpacaSecret

# Init client
print("Initializing Alpaca client...")
tradingClient = TradingClient(alpacaId, alpacaSecret, paper=True)

def getBalance() -> float:
    return float(tradingClient.get_account().cash)

def getPosition(symbol: str) -> float:
    allPositions = tradingClient.get_all_positions()
    for position in allPositions:
        if(position.symbol == symbol):
            return float(position.qty)
    return 0

def getSecurity(symbol: str) -> Asset | RawData:
    return tradingClient.get_asset(symbol)

def placeBuyOrder(symbol: str, shares: float) -> bool:
    print("Attempting to place order for " + str(shares) + " shares of " + symbol + "...")

    # Check if shares is valid
    if(shares <= 0):
        print("Invalid number of shares!")
        return False

    # Check if we can trade this security
    security = getSecurity(symbol)
    if(not security.tradable):
        print("Security " + symbol + " is not tradable!")
        return False
    
    # Fetch the price from yfinance
    price = float(yfinance.Ticker(symbol).info['ask'])

    orderCost = price * shares
    print("Order cost: $" + str(round(orderCost, 2)) + " ($" + str(round(price, 2)) + " * " + str(shares) + ")")

    # Check if we have enough money
    balance = getBalance()
    print("Balance: $" + str(balance))
    if(balance < orderCost):
        print("Insufficient funds!")
        return False
    
    # Place order
    print("Placing order for " + str(shares) + " shares of " + symbol + " for a total cost of $" + str(orderCost) + "...")
    
    # Generate order data
    # GTC is Good Til Cancelled
    # We use DAY so we can have fractional orders
    orderData = MarketOrderRequest(symbol=symbol, qty=shares, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)

    # Submit order
    tradingClient.submit_order(orderData)
    
    print("Order placed!")
    return True

def placeSellOrder(symbol: str, shares: float) -> bool:
    print("Attempting to place order for " + str(shares) + " shares of " + symbol + "...")

    if(shares <= 0):
        print("Invalid number of shares!")
        return False

    security = getSecurity(symbol)
    if(not security.tradable):
        print("Security " + symbol + " is not tradable!")
        return False
    
    # Check if we have enough shares
    position = getPosition(symbol)
    print("Position: " + str(position))
    if(position < shares):
        print("Insufficient shares!")
        return False
    
    # Fetch price
    price = int(yfinance.Ticker(symbol).info['bid'])
    
    # Place order
    print("Placing order for " + str(shares) + " shares of " + symbol + " for a total value of $" + str(round(price * shares, 2)) + "...")

    # Generate order data
    # GTC is Good Til Cancelled
    # We use DAY so we can have fractional orders
    orderData = MarketOrderRequest(symbol=symbol, qty=shares, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)

    # Submit order
    tradingClient.submit_order(orderData)

    print("Order placed!")
    return True