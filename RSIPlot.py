'''
Created on Jun 15, 2017

@author: michaelstecklein
'''


import Database
import RSI
import StockData
import matplotlib.pyplot as plt

#Database.rsi_add_default_entries()

rsis = RSI.get_RSIs(Database.get_stock("AAPL"), StockData.createSDate("2017-01-01"), StockData.createSDate("2017-06-22"))
plt.plot(rsis)
plt.plot((0, len(rsis)), (70, 70), 'r-')
plt.plot((0, len(rsis)), (30, 30), 'g-')
plt.ylabel('RSI')
plt.show()

print "\ndone"