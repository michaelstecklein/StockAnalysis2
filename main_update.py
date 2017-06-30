'''
@author: michaelstecklein
'''
import Email
import Log
import Updater
import Database
from RSI import RSIResults


# Populate Stocks table
Log.log_segment("Updating Stocks table")
Updater.update_index_stocks()

# Populate MarketDates table
Log.log_segment("Updating MarketDates table")
Updater.update_stock_dates()

# Update watchlist, portfolio, and indices
Log.log_segment("Updating IndexFunds table and updating index funds data in DailyData")
Updater.update_indexfund_prices()
Log.log_segment("Updating watchlist")
Updater.update_watchlist()
Log.log_segment("Updating portfolio")
Updater.update_portfolio()

# Populate DailyData table
Log.log_segment("Updating dailydata table")
Updater.update_stock_prices()

# Update indicators
Log.log_segment("Updating indicators")
Updater.update_indicators()

# Email RSI results
rsi_results = RSIResults().get_results()
Log.log(rsi_results)
Email.send_update_email(Database.get_last_market_date(), rsi_results)
errors = Log.get_errors_str()
if errors is not "":
    Email.send_errors_email(errors)

Log.log("Done")
