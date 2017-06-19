'''
@author: michaelstecklein
'''
import Database
import StockData
import Scraper
import MiscInfo
import RSI




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
    if last_update is not None:
        dates = dates[1:] # first date is already in database
    for date in dates:
        Database.add_market_date(date)
        
def __update_prices(stocks):
    for stock in stocks:
        price_history = Scraper.scrape_dailydata(stock)
        for dailydata in price_history:
            Database.add_dailydata(dailydata)
        if stock.first_data_date is None or stock.first_data_date is "0000-00-00": # update first_data_date if needed
            Database.set_first_data_date(stock, price_history[0].date)
        Database.set_last_update(stock, Database.get_last_market_date()) # update last_update

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
    for fund in funds:
        Database.set_on_watchlist(fund, fund.ticker in MiscInfo.WATCHLIST)

def update_portfolio():
    '''Update the portfolio status for all stocks and index funds.'''
    stocks = Database.get_stocks()
    for stock in stocks:
        Database.set_in_portfolio(stock, stock.ticker in MiscInfo.PORTFOLIO)
    funds = Database.get_indexfunds()
    for fund in funds:
        Database.set_in_portfolio(fund, fund.ticker in MiscInfo.PORTFOLIO)

def update_indicators():
    RSI.update_RSI()