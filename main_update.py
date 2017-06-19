'''
@author: michaelstecklein
'''
import Log
import Email
import Updater
import RSI


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
Log.log_segment("Updating stock data in DailyData table")
Updater.update_stock_prices()

# Database updates done
Log.log_segment("Database setup and update completed")

# Update indicators
Log.log_segment("Updating indicators")
Updater.update_indicators()

# Email RSI results
rsi_results = RSI.RSIResults().get_results()
Log.log(rsi_results)
Email.send_update_email(rsi_results + Log.get_errors_str())

# # Get results
# Log.log_segment("Getting results")
# rsi = RSIResults()
# indicator_results = rsi.get_results()
# log(indicator_results)
# 
# # Send email
# Log.log_segment("Sending email")
# Email.send_update_email(indicator_results+get_errors_str())
Log.log("Done")
