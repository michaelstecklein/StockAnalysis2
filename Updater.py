'''
@author: michaelstecklein
'''
import os.path
import csv
import Database
import StockData
import Scraper
import MiscInfo
import RSI
import Log




def update_index_stocks():
    '''Update the list of stocks in the database to include all stocks in the
        DJI, S&P500, NASDAQ, NYSE, etc... and update those stocks to have the
        correct list of indices associated with them.'''
    indices = []
    sp500 = Scraper.scrape_SP500()
    dji = Scraper.scrape_DJI()
    #nasdaq = Scraper.scrape_NASDAQ()
    misc = Scraper.scrape_misc()
    indices.append(sp500)
    indices.append(dji)
    #indices.append(nasdaq)
    indices.append(misc)
    if MiscInfo.SHOULD_SCRAPE_NYSE:
        nyse = Scraper.scrape_NYSE()
        indices.append(nyse)
    # add to list of stocks
    for index in indices:
        for stock in index:
            Database.add_stock(stock)
    # update indices listing for stock
    stocks = Database.get_stocks()
    for stock in stocks: # TODO check stock in ""
        Database.set_indices(stock,"S&P500",stock in sp500)
        Database.set_indices(stock,"DJI",stock in dji)
        #Database.set_indices(stock,"NASDAQ",stock in nasdaq)

def update_stock_dates():
    '''Update the list of dates that the stock market was open to include all dates
        up to today.'''
    last_update = Database.get_last_market_date()
    dates = Scraper.scrape_market_dates(start_date=last_update)
    if dates is None:
        return
    if last_update is not None:
        dates = dates[1:] # first date is already in database
    for date in dates:
        Database.add_market_date(date)
        
def __update_prices(stocks):
    for stock in stocks:
        price_history = Scraper.scrape_dailydata(stock)
        if price_history is None:
            continue
        Log.log("Updating prices for {}".format(stock))
        for dailydata in price_history:
            Database.add_dailydata(dailydata)
        if stock.first_data_date is None or stock.first_data_date is "0000-00-00": # update first_data_date if needed
            Database.set_first_data_date(stock, price_history[0].date)
        Database.set_last_update(stock, Database.get_last_market_date()) # update last_update
        
def assert_stock_prices():
    '''Make sure that all market dates after the first data date for any stock have data for that stock. The scraper often
        leaves holes in the data. If a hole is found, look for manually downloaded data in the old Yahoo database and in
        ./manualdata/<ticker>.csv. If doesn't exist, fill in data as Yahoo does and print an error.'''
    stocks = Database.get_stocks()
    last_assertion_day = StockData.createSDate("2017-07-25")
    market_dates = Database.get_market_dates()
    for stock in stocks:
        for date in market_dates:
            if last_assertion_day >= date:
                continue
            if date.day_number >= stock.first_data_date.day_number:
                if Database.get_dailydata(stock, date=date) is None:
                    dd = Scraper.scrape_dailydata(stock, date, date) # try scraper again
                    if dd is not None:
                        if len(dd) != 0:
                            dd = dd[0] # take it out of array
                        else:
                            dd = None # no data found
                    if dd is None: # try old Yahoo database
                        dd = Database.get_Yahoo_dailydata(stock,date)
                    if dd is None: # try manual csv's
                        dd = Scraper.get_manual_dailydata(stock,date)
                    if dd is None: # nothing left to try, throw error
                        # add the previous day's close to all values and volume to 0. This is what Yahoo does.
                        prev = Database.get_dailydata(stock, date.getPrevious())
                        dd = StockData.SDailyData(stock, date, prev.close, prev.close, prev.close, prev.close, 0)
                        Log.log_error("No data found for {} on {}. Added pseudo values copied from previous day. Check manually to make sure daily data doesn't exist.".format(stock,date))
                    Database.add_dailydata(dd)

def update_stock_prices():
    '''Update the daily data for all stocks on all market dates.'''
    stocks = Database.get_stocks()
    __update_prices(stocks)

def update_indexfund_prices():
    '''Update the daily data for all index funds on all market dates. If an index fund is not listed
        in the database, it will be added.'''
    funds = []
    for ticker in MiscInfo.INDEXFUNDS:
        Database.add_indexfund(StockData.Stock(ticker,""))
        fund = Database.get_ticker_info(ticker)
        Database.add_indexfund(fund)
        funds.append(fund)
        __update_prices([fund])

def update_watchlist():
    '''Update the watchlist status for all stocks and index funds.'''
    stocks = Database.get_stocks()
    for stock in stocks:
        Database.set_on_watchlist(stock, stock.ticker in MiscInfo.WATCHLIST)
    funds = Database.get_indexfunds()
    if funds is None:
        return
    for fund in funds:
        Database.set_on_watchlist(fund, fund.ticker in MiscInfo.WATCHLIST)

def update_portfolio():
    '''Update the portfolio status for all stocks and index funds.'''
    stocks = Database.get_stocks()
    for stock in stocks:
        Database.set_in_portfolio(stock, stock.ticker in MiscInfo.PORTFOLIO)
    funds = Database.get_indexfunds()
    if funds is None:
        return
    for fund in funds:
        Database.set_in_portfolio(fund, fund.ticker in MiscInfo.PORTFOLIO)

def update_indicators():
    RSI.update_RSI()
