'''
@author: michaelstecklein
'''
import requests
import csv
import time
from bs4 import BeautifulSoup
import StockData
import MiscInfo
import Database
import Log



def scrape_SP500():
    '''Scrapes a list of Stocks in the S&P500.'''
    page = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(page.text,"lxml")
    table = soup.find_all('table')[0]
    stocks = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        ticker = cols[0].a.text
        company_name = cols[1].a.text
        stocks.append(StockData.Stock(ticker,company_name))
    return stocks

def scrape_DJI():
    '''Scrapes a list of Stocks in the DJI.'''
    page = requests.get('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    soup = BeautifulSoup(page.text,"lxml")
    table = soup.find_all('table')[1]
    stocks = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        ticker = cols[2].a.text
        company_name = cols[0].a.text
        stocks.append(StockData.Stock(ticker,company_name))
    return stocks

def scrape_NASDAQ():
    '''Scrapes a list of Stocks in the NASDAQ.'''
    pass

def scrape_misc():
    '''Scrapes a list of Stocks list as 'misc'.'''
    stocks = []
    for stock_info in MiscInfo.misc_stocks:
        ticker = stock_info[0]
        company_name = stock_info[1]
        stocks.append(StockData.Stock(ticker,company_name))
    return stocks

def scrape_NYSE():
    '''Scrapes a list of Stocks in the NYSE.'''
    page = requests.get('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download')
    reader = csv.reader(page.text.splitlines())
    stocks = []
    for entry in reader:
        ticker = entry[0]
        company_name = entry[1]
        stocks.append(StockData.Stock(ticker,company_name))

def scrape_market_dates(start_date=MiscInfo.FIRST_MARKET_DATE):
    '''Scrapes the SDates for which the stock market was open using several old
        reference stocks. Returns list in ascending order.'''
    dates = []
    today = StockData.createSDate(time.strftime("%Y-%m-%d"))
    # populate dates with first stock
    dd = scrape_dailydata(StockData.Stock(MiscInfo.MARKET_DATE_REFERENCE_STOCKS[0],""),start_date=start_date,end_date=today)
    for day in dd:
        dates.append(day.date)
    # assert that other stocks' dates agree
    for ticker in MiscInfo.MARKET_DATE_REFERENCE_STOCKS[1:]:
        stock = StockData.Stock(ticker,"")
        dd = scrape_dailydata(stock,start_date=start_date,end_date=today)
        for day in dd:
            if day.date not in dates:
                Log.log_error("market date {} not in agreement between reference stocks {}".format(day.date,MiscInfo.MARKET_DATE_REFERENCE_STOCKS),shutdown=True)
    return dates

def scrape_dailydata(stock, start_date=None, end_date=Database.get_last_market_date()):
    '''Scrapes the daily data for the provided stock between the provided start and end dates, inclusive. Returns
        the data in an array of DailyData by date ascending.'''
    if not isinstance(stock, StockData.Stock):
        raise TypeError("'stock' must be of type Stock")
    if start_date is not None and not isinstance(start_date, StockData.SDate):
        raise TypeError("'start_date' must be of type SDate")
    if not isinstance(end_date, StockData.SDate):
        raise TypeError("'end_date' must be of type SDate")
    if start_date is None:
        if stock.last_update is None:
            start_date = MiscInfo.FIRST_MARKET_DATE
        else:
            start_date = stock.last_update
    return __google_scrape_dailydata(stock, start_date, end_date)


# Google will be used to scrape stock data

google_date_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'} 
def __google_format_date(date_in):
    spl = date_in.split("-")
    date = spl[0]
    month = google_date_dict[spl[1]]
    year = spl[2]
    if int(year) < 50:
        year = "20{}".format(year)
    else:
        year = "19{}".format(year)
    strDate = "{}-{}-{}".format(year,month,date)
    return StockData.createSDate(strDate)

def __google_scrape_dailydata(stock, start_date, end_date):
    years = range(start_date.year, end_date.year+1)
    dailydata = []
    for i in range(len(years)): # scrape year by year, since google acts weird if we don't
        thisyearsdata = []
        year = years[i]
        start_day = 1
        start_mon = 1
        end_day = 31
        end_mon = 12
        if i is 0: # first year may have different start date
            start_day = start_date.day
            start_mon = start_date.month
        if i is len(years)-1: # last year may have different end date
            end_day = end_date.day
            end_mon = end_date.month
        stock.ticker = __google_encode_chars(stock.ticker)
        url = "https://www.google.com/finance/historical?output=csv&q={0}&startdate={1}+{2}+{3}&enddate={4}+{5}+{6}".format(stock.ticker,start_mon,start_day,year,end_mon,end_day,year)
        print "URL ",url
        page = requests.get(url)
        prices = csv.reader(page.text.splitlines())
        skipfirst = True
        for p in prices:
            if skipfirst:
                skipfirst = False
                continue
            p = __google_replace_dashes(p)
            days_price = StockData.SDailyData(stock,__google_format_date(p[0]),float(p[1]),float(p[2]),float(p[3]),float(p[4]),int(p[5]))
            thisyearsdata.append(days_price)
        thisyearsdata.reverse() # data comes descending by date
        dailydata.extend(thisyearsdata)
    return dailydata

def __google_replace_dashes(price):
    '''If data is unavailable, Google places a '-' in its place. Replace these with zeros.'''
    ret = []
    for p in price:
        if p is '-':
            Log.log_error("Missing data for scraped price: {}".format(price))
            ret.append('0')
        else:
            ret.append(p)
    return ret

def __google_encode_chars(url):
    '''Special characters need to be encoded for URLs.'''
    url = url.replace(":","%3A")
    return url