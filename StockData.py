import Database




class Stock:
	'''The Stock class holds all relevant information for a stock (other than pricing data).
		Index funds may also be represented by this class, though not all fields will be relevant.'''
	def __init__(self, ticker, company="", indices="", on_watchlist=False, in_portfolio=False,
				first_data_date=None,last_update=None):
		self.ticker = ticker
		self.company = company
		self.indices = indices
		self.on_watchlist = on_watchlist
		self.in_portfolio = in_portfolio
		if first_data_date is not None and not isinstance(first_data_date, SDate):
			raise TypeError("'first_data_date' must be of type SDate")
		if last_update is not None and not isinstance(last_update, SDate):
			raise TypeError("'last_update' must be of type SDate")
		self.first_data_date = first_data_date
		self.last_update = last_update
		
	def __str__(self):
		return str(self.ticker)
	
	def __eq__(self,other):
		return self.ticker == other.ticker




class SDate:
	'''The SDate class represents a date for which the market was open. It encapsulates both
		the date (YYYY-MM-DD) and the 'stock day', which is the day number since the beginning
		of the database's memory.'''
	def __init__(self, month, day, year):
		self.month = month
		self.day = day
		self.year = year
		self.day_number = Database.get_day_number(self.getDate(), floor=True)
		
	def __str__(self):
		return self.getDate()
	
	def __eq__(self, other):
		return (self.day==other.day) and (self.month==other.month) and (self.year==other.year)
	
	def getDate(self):
		'''Returns the date in a String formated YYYY-MM-DD (for databases).'''
		day_str = str(self.day)
		if self.day <= 9:
			day_str = "0" + day_str
		mon_str = str(self.month)
		if self.month <= 9:
			mon_str = "0" + mon_str
		return "{}-{}-{}".format(self.year,mon_str,day_str)
	
	def getDayNumber(self):
		return self.day_number
	
	def getPrevious(self,num=1):
		'''Returns previous SDate. If 'num' is provided, returns previous num SDates in
			___ order.'''
		prev_daynum = self.day_number - num
		if prev_daynum < 1:
			return None
		return createSDate(prev_daynum)




class SDailyData:
	'''The SDailyData class encapsulates the open, high, close, low, and volume
		for a Stock on a given SDate.'''
	def __init__(self, stock, date, openn, high, low, close, volume):
		if not isinstance(stock, Stock):
			raise TypeError("'stock' must be of type Stock")
		if not isinstance(date, SDate):
			raise TypeError("'date' must be of type SDate")
		self.stock = stock
		self.date = date
		self.openn = openn
		self.high = high
		self.close = close
		self.low = low
		self.volume = volume
	
	
	
	
# ----- MODULE METHODS -----

def createSDate(date):
	'''Given a string YYYY-MM-DD or an integer day number, creates the respective SDate object.'''
	if date is None:
		return None
	date = str(date)
	if '-' in date: # YYYY-MM-DD str
		splt = date.split('-')
		year = int(splt[0])
		month = int(splt[1])
		day = int(splt[2])
		return SDate(month,day,year)
	else: # day number
		daynum = int(date)
		strDate = Database.get_day_for_day_number(daynum)
		return createSDate(strDate)