from Strategy import *



class TestStrategy(Strategy):

	def init(self):
		print "Inside TestStrategy 'init'"

	def day(self, dayNumber):
		print "Inside TestStrategy 'day' %i" % dayNumber
