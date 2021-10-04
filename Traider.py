
from Poertfolio import Portfolio, PortfolioManager

class Trader():
	def __init__(self, clock, starting_balance, strategy, market):
		self.clock = clock
		self.strategy = strategy
		self.market = market
		self.starting_balance = starting_balance

		self.portfolio = None
		self.manager = None

		self.plot_obj = None
		self.curves = []

		#self.start_time = start_time

	def new_portfolio(self):
		self.portfolio = Portfolio(self.clock, self.starting_balance, self.market)
		self.manager = PortfolioManager(self.clock, self.portfolio)

	def trade(self):
		self.comparisons = 0
		print(self.clock.time.date())
		list(map(self.trade_security, self.market.securitys))
		#with concurrent.futures.ThreadPoolExecutor() as executor:
		#	executor.map(self.trade_security, self.market.securitys)
		#self.update_plot()
		return self.comparisons

	def trade_security(self, security):
		#security.update(self.clock.time)
		try:
			price = security.close
			flag = self.strategy.main(security, price)
			if flag == "Buy" or flag =="Sell":
				self.manager.order(security, price, flag)
			#if len(security.curves) != 0:
			#	security.update_plot()
		except KeyError:
			print(f"KeyError, {security}")
		self.comparisons += 1
