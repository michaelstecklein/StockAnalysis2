import datetime
from WatchlistPortfolioIndices import *
from Database import *
from Indicators import *
from SDate import *




class Strategy:
	'''
	This class can be extended to implement various trading strategies.
	The following class methods can be used to write to strategies:

	getPrice(ticker)
	getStockDay(ticker)
	getDate()
	getCash()
	getHoldings(ticker)
	getPortfolio()
	buy(ticker,amount)
	sell(ticker,amount)
	addCash(amount)
	'''

	def __init__(self):
		# defaults
		self.length = 100;
		self.startDate = SDate("1/1/2005")
		self.endDate = SDate("1/1/2006")
		self.__dayNumber = 0;
		self.__run()

	def __str__(self):
		return "Strategy class"
	
	def __run(self):
		self.init()
		for i in range(0,self.length):
			self.__dayNumber += 1
			self.day(self.__dayNumber)

	def init(self):
		''' Called once at the beginning of the strategy run. Should
		set the strategy length (in days), the start date, and the 
		end date. '''
		raise NotImplementedError

	def day(self, dayNumber):
		''' Called once at the end of each day for the length of the
		strategy. '''
		raise NotImplementedError

