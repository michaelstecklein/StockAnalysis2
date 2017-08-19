import datetime
import Database
import Log
from StockData import Stock, SDate, SDailyData, createSDate




class Strategy:
	'''
	This class can be extended to implement various trading strategies.
	The following methods must be overridden by implementing classes:

	init(self)
	day(self, dayNumber)

	The following class methods can be used to write to strategies:

	getPrice(ticker)
	getStockData(ticker)
	getDate()
	getCash()
	getHoldings(ticker)
	getPortfolio()
	buy(ticker,amount)
	sell(ticker,amount)
	addCash(amount)
	'''

	def __init__(self):
		__defaults()
		self.__cash = 0
		self.__portfolio = {} # dictionary
		self.__error_log = [] # list of error messages
		self.__dayNumber = 0;
		self.__run() # strategy is run upon creation

	def __str__(self):
		return "Strategy class"

	def __defaults(self):
		# default start date, length, and end date, to be changed by implementer
		self.startDate = SDate("1/1/2005")
		self.length = -1;
		self.endDate = SDate("1/1/2006") # inclusive
	
	def __run(self):
		self.init()
		self.__pre_run()
		for i in range(0,self.length):
			self.__dayNumber += 1
			self.day(self.__dayNumber)

	def __pre_run(self):
		''' Tasks to do before running but after initialization. '''
		# setup lenth and end date to match each other
		if self.length <= 0:
			# calculate length
			startDayNum = self.startDate.day_number
			endDayNum = self.endDate.day_number
			if endDayNum < startDayNum:
				Log.log_error("End date is before start date", shutdown=True)
			self.length = endDayNum - startDayNum + 1;
		else:
			# calculate end date given length
			startDayNum = self.startDate.day_number
			endDayNum = startDayNum + length - 1
			self.endDate = createSDate(endDayNum)
		# setup Log
		Log.start(str(self))


	### Methods to be overridden by implementing strategies ###

	def init(self):
		''' Called once at the beginning of the strategy run. Should
		set the strategy start date and either the length (in days), or
		the end date. Should also initialize anything relevant to the
		strategy, such as starting cash or starting portfolio holdings.
		Start and end dates are inclusive. '''
		raise NotImplementedError

	def day(self, dayNumber):
		''' Called once at the end of each day for the duration of the
		strategy. '''
		raise NotImplementedError


	### Helper methods for implementing strategies ###

	def getPrice(self, ticker):
		''' Get the closing price for the provided ticker for the current
		day. '''
		return self.getStockData(ticker).close

	def getStockData(self, ticker):
		''' Get a StockData object for the provided ticker for today's
		prices. '''
		stock = Database.get_stock(ticker)
		return Database.get_dailydata(stock, date=self.getDate())

	def getDate(self):
		''' Get the current SDate. '''
		market_day_num = self.startDate.day_number + self.__dayNumber - 1
		return createSDate(market_day_num)

	def getCash(self):
		''' Get the current amount of cash available in the strategy. '''
		return self.__cash

	def getHoldings(self, ticker):
		''' Get the number of shares of the provided ticker currently held
		in the strategy's portfolio. '''
		return self.__portfolio.get(ticker, default=0)

	def getPortfolio(self):
		''' Returns a dictionary, where ticker strings are keys and quantity
		of shares are values.  All tickers not listed have zero as a quantity,
		i.e. they are not part of the portfolio. 
		Ex:  { 'AAPL':10, 'FB':3, 'SCI':20, ... }  '''
		return self.__portfolio

	def buy(self, ticker, num):
		''' 'Buys' the provided quantity of the provided stock for the strategy.
		This will reduce cash and add to the portfolio the respective amounts. '''
		value = getPrice(ticker) * num
		if value > self.__cash:
			Log.log_error("Buying more of {} on {} than is available in cash:::  value:%i cash:%i".format(ticker,self.getDate(),value,self.__cash))
		self.__cash -= value
		holdings = getHoldings(ticker)
		self.__portfolio[ticker] = holdings + num

	def sell(self, ticker, num):
		''' 'Sells' the provided quantity of the provided stock for the stragetgy.
		This will increase cash and remove form the porfolio the respective amounts.'''
		holdings = getHoldings(ticker)
		if holdings < num:
			Log.log_error("Selling more of {} on {} than is in portfolio:::  num:%i holdings:%i".format(ticker,self.getDate(),num,holdings))
		value = getPrice(ticker) * num
		self.__cash += value
		self.__portfolio[ticker] = holdings - num

	def addCash(self, amount):
		''' Adds cash of the provided amount to the cash-on-hand available to the
		strategy. '''
		self.__cash += amount


	### Private helper methods for this class ###

	# TODO

