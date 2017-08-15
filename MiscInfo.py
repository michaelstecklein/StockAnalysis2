'''
@author: michaelstecklein
'''


SP500 = "S&P500"
DJI = "DJI"
NASDAQ = "NASDAQ"

SHOULD_SCRAPE_NYSE = False

misc_stocks = {
	('TSLA', "Tesla")
}


WATCHLIST = 	[
		'FB',
# 		'USO',
# 		'UCO',
		'AAPL',
		'GOOG',
		'TSLA',
		'F',
		'TXN',
		'LMT',
		'BAC',
		'AYI',
		'CRM',
		];

PORTFOLIO = 	[
# 		'USO',
# 		'UCO',
		'F',
		];

INDEXFUNDS =	[
		# These don't work with Google as of now, may be able to write more advanced scraping system to parse the HTML
		#'INDEXSP:.INX', # S&P500, ^GSPC
		#'^IXIC', # NASDAQ composite
		#'^DJI',  # DOW 30
		#'^VIX',# volatility (S&P500)
# 		'SPY', # S&P500 ETF trust
# 		'USO', # oil ETF
# 		'UCO', # short-term oil ETF
# 		'EDV', # long-term treasury ETF
# 		'BND', # total bond ETF
# 		'VTI', # total market ETF
# 		'VOO', # S&P500 ETF
# 		'VO',  # medium cap ETF
# 		'VB',  # small cap ETF
# 		'VXUS',# total international ETF
# 		'XIV', # inverse ^VIX
# 		'USL', # US oil long
# 		'VHT', # health care ETF
# 		'XLE'  # energy ETF
		];
		
FIRST_MARKET_DATE = "1978-01-03" # first date recorded by google finance
MARKET_DATE_REFERENCE_STOCKS = ('IBM','KO','GE')
