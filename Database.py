'''
@author: michaelstecklein
'''

import os
import warnings
import MySQLdb
import Log
import RSI
import StockData







""" -----------------------------------------------------------------------------------------------------------
        This sections defines the structures for setting up and storing the database and its tables.
----------------------------------------------------------------------------------------------------------- """


class Database:
    
    __PRINT_ALL_QUERIES = True

    def __init__(self, name, username, password):
        self.name = name
        self.__username = username
        self.__password = password
        self.tables = []
        warnings.filterwarnings('ignore', category=MySQLdb.Warning) # ignore warnings
        self.__startup()
        Log.log_segment("Updating/creating database")
        self.__create()
        Log.log("Done updating/creating database")
        
    def createTable(self, table):
        self.tables.append(table)
        if not isinstance(table, Table):
            raise TypeError("'table' must be of type Table")
        contents = table.build()
        qry = "CREATE TABLE IF NOT EXISTS {0}({1});".format(table.name,contents)
        self.query(qry)
        return self # for chaining calls
        
    def __startup(self):
        os.system("mysql.server start")
        
    def __create(self):
        self.query("CREATE DATABASE IF NOT EXISTS {0};".format(self.name)) 
        self.query("USE {0};".format(self.name)) 
    
    def __shutdown(self):
        os.system("mysql.server stop")
        
    def query(self,qry):
        if self.__PRINT_ALL_QUERIES:
            print qry
        try:
            connection = MySQLdb.connect("localhost", self.__username, self.__password, self.name);
        except MySQLdb.Error, e:
            Log.log_error("Error occurred when connecting to database {0}\n{1}".format(self.name, e), shutdown=True)
        try:
            cursor = connection.cursor()
            cursor.execute(qry)
            if "INSERT" or "UPDATE" in qry:
                connection.commit()
            return cursor.fetchall()
        except MySQLdb.Error, e:
            Log.log_error("""Error occurred when executing command "{0}"\n{1}""".format(qry, e), shutdown=True)



# Attribute types:
def VARCHAR(size):
    return "VARCHAR({})".format(size)
def CHAR(size):
    return "CHAR({})".format(size)
def SET(lst):
    contents = ""
    comma = ""
    for l in lst:
        contents += "{}'{}'".format(comma,l)
        comma = ","
    return "SET({})".format(contents)
def ENUM(lst):
    contents = ""
    comma = ""
    for l in lst:
        contents += "{}'{}'".format(comma,l)
        comma = ", "
    return "ENUM({})".format(contents)
TINYINT = "TINYINT"
SMALLINT = "SMALLINT"
MEDIUMINT = "MEDIUMINT"
BIGINT = "BIGINT"
INT = "INT"
FLOAT = "FLOAT"
DATE = "DATE"
TIMESTAMP = "TIMESTAMP"

class Attribute:
    
    def __init__(self, name, typee, notnull=False, default=None, unsigned=False, primarykey=False, autoincrement=False):
        self.name = name
        self.typee = typee
        self.notnull = notnull
        self.default = default
        self.unsigned = unsigned
        self.primarykey = primarykey
        self.autoincrement = autoincrement
        
    def build(self):
        props = []
        props.append(self.name)
        props.append(self.typee)
        props.append("UNSIGNED" if self.unsigned else None)
        props.append("NOT NULL" if self.notnull else "NULL")
        props.append("DEFAULT " + str(self.default) if self.default != None else None)
        props.append("PRIMARY KEY" if self.primarykey else None)
        props.append("AUTO_INCREMENT" if self.autoincrement else None)
        attr = ""
        for p in props:
            if p != None:
                attr += " " + p
        return attr
    
    def __str__(self):
        return self.build()
        


class Table:
    
    def __init__(self, name):
        self.name = name
        self.attributes = []
        self.comboprimarykey = []
        
    def addAttribute(self, name, typee, notnull=False, default=None, unsigned=False, primarykey=False, autoincrement=False, comboprimarykey=False):
        attr = Attribute(name,typee,notnull=notnull,default=default,
                    unsigned=unsigned,primarykey=primarykey,autoincrement=autoincrement)
        if comboprimarykey:
            self.comboprimarykey.append(attr)
        self.attributes.append(attr)
        return self # for chaining calls
    
    def __createPrimaryKey(self):
        contents = ""
        comma = ""
        for k in self.comboprimarykey:
            contents += comma + str(k.name)
            comma = ","
        return "PRIMARY KEY({})".format(contents)
    
    def build(self):
        contents = ""
        comma = ""
        # special case for combination primary keys
        if len(self.comboprimarykey) != 0:
            contents = self.__createPrimaryKey()
            comma = ","
        for attr in self.attributes:
            contents += comma + str(attr)
            comma = ","
        return contents
    
    def __str__(self):
        return self.build()
        
        
""" -----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------- """









""" -----------------------------------------------------------------------------------------------------------
        This sections runs when this module is imported and constructs the database.
----------------------------------------------------------------------------------------------------------- """

__DATABASE_NAME = 'StockData2'
__USERNAME = 'python_user'
__PASSWORD = 'password'
__DAILYDATA_TABLE_NAME = 'DailyData'
__MARKETDATES_TABLE_NAME = 'MarketDates'
__STOCKS_TABLE_NAME = 'Stocks'
__INDEXFUNDS_TABLE_NAME = 'IndexFunds'


database = None

if database == None:

    # Stocks table
    stocksTable = Table(__STOCKS_TABLE_NAME)
    stocksTable \
        .addAttribute('ticker', VARCHAR(5), notnull=True, primarykey=True ) \
        .addAttribute('company_name', VARCHAR(30) ) \
        .addAttribute('indices', SET(['NASDAQ','S&P500','DJI']), default='NULL' ) \
        .addAttribute('on_watchlist', ENUM(['True','False']), default="'False'" ) \
        .addAttribute('in_portfolio', ENUM(['True','False']), default="'False'" ) \
        .addAttribute('first_data_date', DATE ) \
        .addAttribute('last_update_date', DATE )

    # MarketDates table
    marketDatesTable = Table(__MARKETDATES_TABLE_NAME)
    marketDatesTable \
        .addAttribute('date', DATE, notnull=True) \
        .addAttribute('day_number', INT, unsigned=True, notnull=True, primarykey=True, autoincrement=True)

    # DailyData table
    dailyDataTable = Table(__DAILYDATA_TABLE_NAME)
    dailyDataTable \
        .addAttribute('ticker', VARCHAR(5), notnull=True, comboprimarykey=True) \
        .addAttribute('date', DATE, notnull=True, comboprimarykey=True) \
        .addAttribute('open', FLOAT, notnull=True) \
        .addAttribute('high', FLOAT, notnull=True) \
        .addAttribute('low', FLOAT, notnull=True) \
        .addAttribute('close', FLOAT, notnull=True) \
        .addAttribute('volume', BIGINT, default='-1')

    # IndexFunds table
    indexFundsTable = Table(__INDEXFUNDS_TABLE_NAME)
    indexFundsTable \
        .addAttribute('ticker', VARCHAR(25), notnull=True, primarykey=True) \
        .addAttribute('on_watchlist', ENUM({'True','False'}), default="'False'") \
        .addAttribute('in_portfolio', ENUM({'True','False'}), default="'False'") \
        .addAttribute('first_data_date', DATE) \
        .addAttribute('last_update_date', DATE)

    # database
    database = Database(__DATABASE_NAME, __USERNAME, __PASSWORD)
    database.createTable(stocksTable)       \
            .createTable(marketDatesTable)  \
            .createTable(dailyDataTable)    \
            .createTable(indexFundsTable)
        
    # Other indicator specific tables

    # RSI table
    __RSI_TABLE_NAME = "RSIs"
    rsiTable = Table(__RSI_TABLE_NAME)
    rsiTable \
        .addAttribute('ticker', VARCHAR(5), notnull=True, comboprimarykey=True) \
        .addAttribute('date', DATE, notnull=True, comboprimarykey=True) \
        .addAttribute('RSI', FLOAT, default=RSI.DEFAULT_VALUE) \
        .addAttribute('avg_gain', FLOAT, default=RSI.DEFAULT_VALUE) \
        .addAttribute('avg_loss', FLOAT, default=RSI.DEFAULT_VALUE)
    database.createTable(rsiTable)
        
""" -----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------- """









""" -----------------------------------------------------------------------------------------------------------
        This sections exposes public static methods for accessing the database.
----------------------------------------------------------------------------------------------------------- """

    
def add_market_date(date):
    '''Adds the date to the list of dates that the market was open if the date
        does not already exist.'''
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of type SDate")
    __reset_autoincrement(__MARKETDATES_TABLE_NAME)
    __insert(__MARKETDATES_TABLE_NAME, "'{}',NULL".format(date.getDate()))

def add_stock(stock):
    '''Adds the stock to the list of stocks in the database if the stock does
        not already exist.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of type Stock")
    __insert(__STOCKS_TABLE_NAME, '''"{}","{}","{}","{}","{}","{}","{}"'''.format(
        stock.ticker,stock.company,stock.indices,stock.on_watchlist,stock.in_portfolio,
        stock.first_data_date,stock.last_update))
    
def add_indexfund(fund):
    '''Adds the index fund to the list of index funds if the fund does not
        already exist.'''
    if not isinstance(fund, StockData.Stock):
        raise TypeError("'fund' must be of type Stock")
    __insert(__INDEXFUNDS_TABLE_NAME, '''"{}","{}","{}","{}","{}"'''.format(fund.ticker,
        fund.on_watchlist,fund.in_portfolio,fund.first_data_date,fund.last_update))

def add_dailydata(dd):
    '''Adds the daily data info to the database of stock data.'''
    if not isinstance(dd, StockData.SDailyData):
        raise TypeError("parameter must be of time SDailyData")
    __insert(__DAILYDATA_TABLE_NAME,'''"{0}","{1}",{2},{3},{4},{5},{6}'''.format(
            dd.stock.ticker,dd.date,dd.openn,dd.high,dd.low,dd.close,dd.volume))
    
def get_stock(ticker):
    '''Returns a Stock object provided the stock's of index fund's ticker.'''
    table = __get_stockindexfund_table(ticker)
    res = __select_all(table,where="ticker='{}'".format(ticker))[0]
    if table is __STOCKS_TABLE_NAME:
        return __format_stock_res(res)
    else:
        return __format_indexfund_res(res)
    
def get_stocks():
    '''Returns a list of stocks tracked in the database'''
    ret = __select_all(__STOCKS_TABLE_NAME, None)
    stocks = []
    for entry in ret:
        stocks.append(__format_stock_res(entry))
    return stocks
    
def get_indexfunds():
    '''Returns a list of index funds tracked in the database'''
    ret = __select_all(__INDEXFUNDS_TABLE_NAME, None)
    funds = []
    for entry in ret:
        funds.append(__format_indexfund_res(entry))
    return funds

def get_dailydata(stock,date=None):
    '''Returns a list of SDailyData for the provided Stock, ordered by date ascending. If a date is provided,
        then only one SDailyData object is returned.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    if date != None and not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of type SDate")
    where = "ticker='{}' ".format(stock.ticker)
    if date is not None:
        where += "date='{}'".format(date)
    res = __select_all(__DAILYDATA_TABLE_NAME, where=where, restrictions="ORDER BY date ASC")
    dd = []
    for entry in res:
        print "ENTRY ",entry
        dd.append(StockData.SDailyData(get_stock(entry[0]),StockData.createSDate(entry[1]),entry[2],
                                       entry[3],entry[4],entry[5],entry[6]))
    if date != None:
        return dd[0]
    return dd
    
def get_first_market_date():
    '''Returns the first SDate for which the market was open'''
    res = __single(__select('date',__MARKETDATES_TABLE_NAME,restrictions='ORDER BY day_number ASC LIMIT 1'))
    return StockData.createSDate(str(res))
    
def get_last_market_date():
    '''Returns the last SDate for which the market was open'''
    res = __single(__select('date',__MARKETDATES_TABLE_NAME,restrictions='ORDER BY day_number DESC LIMIT 1'))
    if res is None:
        return None
    return StockData.createSDate(str(res))

def get_day_number(date, floor=False):
    num = __single(__select('day_number',__MARKETDATES_TABLE_NAME,where="date='{}'".format(date)))
    if num is None:
        if not floor:
            return None
        else: # round to the previous day
            num = __single(__select('day_number',__MARKETDATES_TABLE_NAME,where="date<='{}'".format(date),restrictions="ORDER BY date DESC LIMIT 1"))
    return int(num)

def get_day_for_day_number(day_number):
    return __single(__select("date",__MARKETDATES_TABLE_NAME,where="day_number='{}'".format(day_number)))

def get_ticker_info(ticker):
    '''Returns a Stock object for the provided ticker. May either be a stock or index fund.'''
    if not isinstance(ticker, str):
        raise TypeError("'ticker' must be of time 'str'")
    if __contains(__STOCKS_TABLE_NAME, "ticker='{}'".format(ticker)):
        res = __select_all(__STOCKS_TABLE_NAME,"ticker='{}'".format(ticker))[0]
        stock = StockData.Stock(ticker, company=res[1], indices=res[2], on_watchlist=res[3], 
                in_portfolio=res[4], first_data_date=res[5],last_update=res[6])
    elif __contains(__INDEXFUNDS_TABLE_NAME, "ticker='{}'".format(ticker)):
        res = __select_all(__INDEXFUNDS_TABLE_NAME,"ticker='{}'".format(ticker))[0]
        stock = StockData.Stock(ticker,on_watchlist=res[1],in_portfolio=res[2],first_data_date=StockData.createSDate(res[3]),
                last_update=StockData.createSDate(res[4]))
    else:
        raise Exception("{} not found in IndexFunds or Stocks tables".format(ticker))
    return stock
    
def set_first_data_date(stock, date):
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of time SDate")
    table = __get_stockindexfund_table(stock.ticker)
    __update(table,"first_data_date='{}'".format(date),"ticker='{}'".format(stock.ticker))
    
def set_indices(stock,index,truefalse): # TODO check this method!
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    res = __single(__select('indices',__STOCKS_TABLE_NAME,where="ticker='{}'".format(stock.ticker)))
    if res is None:
        return
    indices = res # comes packed in two tuples
    if truefalse and index not in indices:
        indices += "," + index
    if not truefalse and index in indices:
        indices.replace(index,"")
        indices.replace(",,",",")
    if indices is not None and indices is not "" and indices[0] == ',':
        indices = indices[1:]
    __set_stockindexfund_value(stock,'indices',indices)
    
def set_on_watchlist(stock, value):
    __set_stockindexfund_value(stock,'on_watchlist',value)
    
def set_in_portfolio(stock, value):
    __set_stockindexfund_value(stock,'in_portfolio',value)

def set_last_update(stock, date):
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of time SDate")
    __set_stockindexfund_value(stock,'last_update_date',date)
    
    
# private access methods
def __insert(table, value):
    database.query("INSERT IGNORE INTO {0} VALUES({1});".format(table,value))
    
def __select(attrs, table, where=None, restrictions=None):
    if restrictions is None:
        restrictions = ""
    if attrs==None or attrs=="":
        attrs = '*'
    if where==None or where=="":
        res = database.query("SELECT {} FROM {} {};".format(attrs,table,restrictions))
    else:
        res = database.query("SELECT {} FROM {} WHERE {} {};".format(attrs,table,where,restrictions))
    return __check_empty_query(res)
    
def __select_all(table, where=None, restrictions=None):
    return __select('*',table,where=where,restrictions=restrictions)

def __update(table, set_attr, where):
    database.query("UPDATE {} SET {} WHERE {};".format(table,set_attr,where))
    
def __contains(table, condition):
    res = __select_all(table,where=condition)
    return res != None

def __get_stockindexfund_table(ticker):
    if __contains(__STOCKS_TABLE_NAME, "ticker='{}'".format(ticker)):
        return __STOCKS_TABLE_NAME
    elif __contains(__INDEXFUNDS_TABLE_NAME, "ticker='{}'".format(ticker)):
        return __INDEXFUNDS_TABLE_NAME
    else:
        raise Exception("{} not found in IndexFunds or Stocks tables".format(ticker))

def __set_stockindexfund_value(stock, attr, value):
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    table = __get_stockindexfund_table(stock.ticker)
    __update(table,"{}='{}'".format(attr,value),"ticker='{}'".format(stock.ticker))

def __format_stock_res(res):
    return StockData.Stock(res[0],company=res[1],indices=res[2],on_watchlist=res[3],
                in_portfolio=res[4],first_data_date=StockData.createSDate(res[5]),last_update=StockData.createSDate(res[6]))
    
def __format_indexfund_res(res):
    return StockData.Stock(res[0],on_watchlist=res[1],in_portfolio=res[2],
            first_data_date=StockData.createSDate(res[3]),last_update=StockData.createSDate(res[4]))
    
def __reset_autoincrement(table):
    database.query("ALTER TABLE {0} AUTO_INCREMENT = 1;".format(table))
    
def __single(res):
    if res is None:
        return None
    return res[0][0]
        
def __check_empty_query(qry):
    if len(qry)==0:
        return None
    return qry


""" -----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------- """









""" -----------------------------------------------------------------------------------------------------------
        Indicator specific database content. Will need to be adjusted for new non-memoryless indicators.
----------------------------------------------------------------------------------------------------------- """

def rsi_add_default_entries():
    '''Insert default entries for all market dates that are not represented in the RSI table.'''
    database.query("INSERT IGNORE INTO {} (ticker, date, RSI, avg_gain, avg_loss) SELECT ticker, date, {}, {}, {} FROM {};".format(
            __RSI_TABLE_NAME,RSI.DEFAULT_VALUE,RSI.DEFAULT_VALUE,RSI.DEFAULT_VALUE,__DAILYDATA_TABLE_NAME))
    
def rsi_get_defaults(stock):
    '''Return a list of all SDates who RSI value is the default value for the provided stock, sorted ascending.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    res = __select("date", __RSI_TABLE_NAME, where="RSI='{}' AND ticker='{}'".format(RSI.DEFAULT_VALUE,stock.ticker), restrictions="ORDER BY date ASC")
    if res is None:
        return res
    dates = []
    for date in res:
        dates.append(StockData.createSDate(date[0]))
    return dates

def rsi_get(stock,date):
    '''Returns the RSI value for the provided Stock and SDate.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of type Stock")
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of type SDate")
    res = __single(__select("RSI", __RSI_TABLE_NAME, where="ticker='{}' AND date='{}'".format(stock.ticker,date), restrictions="ORDER BY date DESC LIMIT 1"))
    if res is None:
        return None
    return float(res)

def rsi_get_previous_count(stock,date):
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of time Stock")
    if not isinstance(date, StockData.SDate):
        raise TypeError("'date' must be of type SDate")
    res = __single(__select("COUNT(*)", __RSI_TABLE_NAME, where="ticker='{}' AND date<'{}'".format(stock.ticker,date)))
    return int(res)

def rsi_get_close_history(stock, date, num_days_preceding):
    res = __select("close",__DAILYDATA_TABLE_NAME,where="ticker='{}' AND date<='{}'".format(stock.ticker,date),restrictions="ORDER BY date DESC LIMIT {}".format(num_days_preceding))
    closes = []
    for i in range(num_days_preceding):
        closes.append(res[i][0])
    return closes

def rsi_get_metadata(stock,date):
    '''Returns a RSI.Metadata object for the given Stock and SDate.'''
    res = __select_all(__RSI_TABLE_NAME,where="ticker='{}' AND date='{}'".format(stock,date))[0]
    return RSI.Metadata(res[0],res[1],res[2],res[3],res[4])

def rsi_set_metadata(metadata):
    '''Sets the entry for the given Stock and SDate with the provided metadata.'''
    __update(__RSI_TABLE_NAME, "RSI='{}', avg_gain='{}', avg_loss='{}'".format(metadata.rsi,metadata.avg_gain,metadata.avg_loss),
             "ticker='{}' AND date='{}'".format(metadata.ticker,metadata.date))

""" -----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------- """