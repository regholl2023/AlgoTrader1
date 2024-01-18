import pandas
import yfinance
from api import getBalance, getSecurity, placeBuyOrder
from sheets import log
from training import train
from testing import test, predictTomorrow
from trading import startLoop

log("Starting process...")

startLoop()

timesteps = 40 # 40 works well
days = 365 * 10 # 10 years works well
trainingRatio = 1 # What % of data to use for training, 0.8 is standard
offsetDays = 0
symbol = "BAC" # Symbols with 20% - 30% returns over 5Y seem to work best, such as KO, CVX, PM, BAC (v. well!), INTC, WFC (v. well!)

# Get historical data
today = pandas.Timestamp.today()
today = today - pandas.Timedelta(days=offsetDays)
start_date = today - pandas.Timedelta(days=days)

print("Downloading data from " + start_date.strftime("%Y-%m-%d") + " to " + today.strftime("%Y-%m-%d") + "...")
data = pandas.DataFrame(yfinance.download(symbol, start=start_date, end=today))
print("Done!")

print("Data length: " + str(len(data)))

# Check TensorFlow configuration
# print("TensorFlow configuration:")
# print("CPUs:", tensorflow.config.list_physical_devices('CPU'))
# print("GPUs:", tensorflow.config.list_physical_devices('GPU'))

# Be really careful with : placement here!
model = train(data[:int(len(data) * trainingRatio)], timesteps)

# Test model
# test(model, data[int(len(data) * trainingRatio):], timesteps)

print("Predicted Tmr:", predictTomorrow(model, data, timesteps))