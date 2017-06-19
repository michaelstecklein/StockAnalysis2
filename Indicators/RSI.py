'''
@author: michaelstecklein
'''
import datetime
import Database
import StockData
import MiscInfo

# http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index_rsi

DEFAULT_VALUE = -1
NULL_VALUE = -2


__N = 14

def update_RSI():
    '''Updates RSI values for all market dates.'''
    Database.rsi_add_default_entries()
    stocks = Database.get_stocks()
    for stock in stocks:
        defaultdates = Database.rsi_get_defaults(stock)
        # 'get_RSI' will automatically update default dates, so retrieving the last date value will result in updating
        #    all previous RSI values
        get_RSI(stock,defaultdates[len(defaultdates)-1])
    
def get_RSI(stock, date):
    '''Returns the RSI value for the provided stock and date. Will calculate the value if necessary.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of type Stock")
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of type SDate")
    rsi = Database.rsi_get(stock,date)
    if rsi != DEFAULT_VALUE:
        return rsi
    # else must update value:
    count = Database.rsi_get_previous_count(stock,date)
    if count < __N: # one of first N entries
        metadata = Metadata(stock,date,NULL_VALUE,NULL_VALUE,NULL_VALUE)
    if count == __N: # first RSI value
        metadata = __calculate_first_RSI(stock,date)
    else:
        metadata = __calculate_RSI(stock,date)
    Database.rsi_set_metadata(metadata)
    return metadata.rsi
   
def __calculate_first_RSI(stock,date):
    closes = __get_close_history(stock,date,__N+1)
    avg_gain = 0
    avg_loss = 0
    for i in range(1,len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            avg_gain += diff
        else:
            avg_loss += diff*-1
    avg_gain /= __N
    avg_loss /= __N
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    return Metadata(stock,date,rsi,avg_gain,avg_loss)

def __calculate_RSI(stock,date): # not first RSI value
    prev_date = date.getPrevious()
    get_RSI(stock, prev_date) # force previous RSI's calculation
    prev_meta = Database.rsi_get_metadata(stock,prev_date)
    closes = __get_close_history(stock, date, 2)
    diff = closes[0]-closes[1]
    if diff > 0:
        curr_gain = diff
        curr_loss = 0
    else:
        curr_gain = 0
        curr_loss = diff
    avg_gain = (prev_meta.avg_gain * (__N-1) + curr_gain) / __N
    avg_loss = (prev_meta.avg_loss * (__N-1) + curr_loss) / __N
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    return Metadata(stock,date,rsi,avg_gain,avg_loss)

def __get_close_history(stock, date, num_days):
    dd = Database.get_dailydata(stock)
    ln = len(dd)
    closes = []
    for i in range (ln-1,ln-1-num_days,-1):
        closes.append(dd[i].close)
    return closes
    
    
    
class Metadata():
    '''Container for RSI data and metadata.'''
    def __init__(self,stock,date,rsi,avg_gain,avg_loss):
        self.ticker = str(stock)
        self.date = date
        self.rsi = rsi
        self.avg_gain = avg_gain
        self.avg_loss = avg_loss
        
        
        
        
        
        
        
class RSIResults():
    __USE_SPACES_INSTEAD_TABS = True
    __HIGH_RSI = 70
    __LOW_RSI = 30
    __WARN_HIGH_RSI = 65
    __WARN_LOW_RSI = 35

    RESULT = ""
    
    def __header(self, title):
        SZ = 44
        l = len(title)
        self.RESULT += "{} ".format(title)
        self.RESULT += "-" * (SZ - l)
        self.RESULT += "\n"

    def __warn(self, ticker, rsi, msg):
        t = "{}".format(ticker)
        r = "{}".format(rsi)
        m = "{}".format(msg)
        if self.__USE_SPACES_INSTEAD_TABS:
            FIRST_SPACING = 7
            SECOND_SPACING = 20
            self.RESULT += str(t)
            self.RESULT += " " * (FIRST_SPACING - len(t))
            self.RESULT += str(r)
            self.RESULT += " " * (SECOND_SPACING - len(r))
            self.RESULT += str(m)
        else:
            self.RESULT += "{}\t{}\t{}".format(t,r,m)
        self.RESULT += "\n"

    def __check_rsi(self, ticker, rsi):
        if rsi >= self.__HIGH_RSI:
            self.__warn(ticker, rsi, "high")
        elif rsi <= self.__LOW_RSI:
            self.__warn(ticker, rsi, "LOW")
        elif rsi <= self.__WARN_LOW_RSI:
            self.__warn(ticker, rsi, "l")
        elif rsi >= self.__WARN_HIGH_RSI:
            self.__warn(ticker, rsi, "h")

    def __run_ticker_list(self, ticker_list, title):
        self.__header(title)
        for ticker in ticker_list:
            rsi = get_RSI(StockData.Stock(ticker,""), Database.get_last_market_date())
            self.__check_rsi(ticker, rsi)

    def get_results(self):
        self.RESULT = ""
        self.__run_ticker_list(MiscInfo.PORTFOLIO, "Portfolio")
        self.__run_ticker_list(MiscInfo.WATCHLIST, "Watchlist")
        self.__run_ticker_list(MiscInfo.INDEXFUNDS, "Index Funds")
        stocks = Database.get_stocks()
        tickers = []
        for stock in stocks:
            tickers.append(stock.ticker)
        self.__run_ticker_list(tickers, "All Stocks")
        return self.RESULT