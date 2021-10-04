from Strategy import Golden_Cross,Golden_Vertex, Golden_Vertex_Greedy
from Traider import Trader
from SystemClock import SystemClock
from Market import Market

from pandas.tseries.offsets import BDay, CustomBusinessDay
from time import time as timer
from datetime import date, datetime, timedelta
import PySide2.QtWidgets as qtw
import pyqtgraph as pg

class Setter():
	def __init__(self, vitals, plot, stock_watch, portfolioBlock):
		self.clock = SystemClock(datetime(2019, 1, 3), datetime.today())

		self.market_input_method = ["dir", "yahoo"]
		self.market_list = ["^OMX"]
		self.strategy_list = ["Golden Cross", "Golden Vertex", "Golden Vertex (Greedy)"]

		self.vitals = vitals
		self.plot = plot
		self.stock_watch = stock_watch
		self.portfolioBlock = portfolioBlock

		self.market_source = self.market_input_method[0]
		self.market_name = self.market_list[0]
		self.strategy_name = self.strategy_list[0]
		self.strategy_arg = [2,15]
		self.cash = 100000

		self.traider = None
		self.market = None
		self.strategy = None

		self.traiderPlot = plot.create_plot()
		self.traiderCurves = []

		self.init_strategy()
		self.init_traider()


	def init_market(self):
		time = timer()
		market_obj = None
		if self.market_source == "dir":
			market_obj = Market.from_dir(self.clock, self.market_name, "Skr")
		elif self.market_source == "yahoo":
			market_obj = Market.from_source(self.clock, self.market_name, "Skr")
		run_time = timer() - time 
		print(f"Data read in {run_time}sec")
		self.market = market_obj
		self.stock_watch.init_stock_watch(self, self.clock.start)

	def init_strategy(self):
		shortStep = self.strategy_arg[0]
		longStep = self.strategy_arg[1]
		strategy_obj = None
		if self.strategy_name == "Golden Cross":
			strategy_obj = Golden_Cross(shortStep, longStep)
		elif self.strategy_name == "Golden Vertex":
			strategy_obj= Golden_Vertex(shortStep, longStep)
		elif self.strategy_name == "Golden Vertex (Greedy)":
			strategy_obj= Golden_Vertex_Greedy(shortStep, longStep)
		self.strategy = strategy_obj

	def init_traider(self):
		self.traider = Trader(self.clock, int(self.cash), self.strategy, self.market)

	def initTraderPlot(self):
		lc = ['r', 'g', 'c', 'm', 'y', 'w', 'b']
		
		if len(self.traiderPlot.curves) == 0:
			self.traiderPlot.addItem(pg.PlotDataItem(pen=lc[0], name = f"{self.market} normalized-index"))
		color = lc[len(self.traiderPlot.curves)]
		self.traiderPlot.addItem(pg.PlotDataItem(pen=color, name = f"Total value with {self.strategy}"))

	def update_traiderPlot(self):
		time = self.clock.time
		portf = self.traider.portfolio
		portf.update()
		x_axis = portf.performance.loc[:time].index.astype("int")//10**9
		tot_axis = portf.performance["Total"].loc[:time]
		indx_axis = portf.performance["norm_Close"].loc[:time]

		self.traiderPlot.curves[0].setData(x_axis, indx_axis)
		self.traiderPlot.curves[-1].setData(x_axis, tot_axis)
	
	def initStockPlot(self,stock):
		#self.plot_obj.clear()
		plot = self.stock_watch.plots[stock]
		if len(plot.curves) == 0:
			#self.curves[stock] += [self.plots[stock].plot(name=stock.ticker, pen= "b")]
			plot.addItem(pg.PlotDataItem(name=stock.ticker, pen= "b"))
			plot.addItem(pg.PlotDataItem(name=self.strategy.short_step_tag, pen="r"))
			plot.addItem(pg.PlotDataItem(name=self.strategy.long_step_tag, pen="g"))
			#plot.addItem(pg.PlotDataItem(name="Trades", pen=None ,symbol="d", symbolBrush=('g'), symbolSize=10))
			#self.curves += [self.plot_obj.plot(name= "Buy", pen=None ,symbol="d", symbolBrush=('g'), symbolSize=10)]
			#self.curves += [self.plot_obj.plot(name= "Sell", pen=None, symbol="d", symbolBrush=('r'), symbolSize=10)]
			#self.curves += [self.plot_obj.plot(name= "Miss", pen=None, symbol="d", symbolBrush=('w'), symbolSize=10)]
		#try:
		#	self.curves += [self.plot_obj.plot(name= self.buy_sell_flag.columns.values[6], pen="r")]
		#	self.curves += [self.plot_obj.plot(name= self.buy_sell_flag.columns.values[7], pen="g")]
		#except AttributeError:
		#	print("No strategy data")
		self.updateStockPlot()

	def updateStockPlot(self, price_type="Close"):
		for stock in self.stock_watch.plots.keys():
			try:
				time = stock.clock.time
				start = stock.clock.start
				curves = self.stock_watch.plots[stock].curves
				#filt = self.traider.portfolio.history["Security"] == stock
				#portf = self.traider.portfolio.history.loc[filt]["Price"].loc[start:time]
				#print(portf)
				time_axis = stock.data.loc[start:time].index.astype("int")//10**9
				curves[0].setData(time_axis, stock.data["Close"].loc[start:time])
				curves[1].setData(time_axis, stock.data[f"{self.strategy.short_step_tag}"].loc[start:time])
				curves[2].setData(time_axis, stock.data[self.strategy.long_step_tag].loc[start:time])
				#curves[3].setData(time_axis, portf)
			#self.curves[1].setData(time_axis, self.buy_sell_flag["Buy"])
			#self.curves[2].setData(time_axis, self.buy_sell_flag["Sell"])
			#self.curves[3].setData(time_axis, self.buy_sell_flag["Miss"])
			#self.curves[4].setData(time_axis, self.buy_sell_flag[self.buy_sell_flag.columns.values[6]])
			#self.curves[5].setData(time_axis, self.buy_sell_flag[self.buy_sell_flag.columns.values[7]])
			except KeyError:
				print(f"Key Error: {KeyError}")
				pass
			except IndexError:
				print(f"Index Error: {IndexError}")
				pass

	def reset_traider(self):
		print(self.clock.start)
		self.traider.starting_balance = self.cash
		self.traider.strategy = self.strategy
		self.traider.market = self.market
		self.traider.new_portfolio()
		self.initTraderPlot()

	def run(self):
		self.clock.update(self.clock.start)
		self.reset_traider()

		run_timer = timer()
		comparisons = 0
		for time in self.market.market_index.data.loc[self.clock.start:self.clock.end].index:
			#self.traider.time = time
			self.clock.update(time)
			comparisons += self.traider.trade()
			
			self.portfolioBlock.update(self.traider)
			self.stock_watch.update()
			self.vitals.update(self.traider)
			self.update_traiderPlot()
			self.updateStockPlot()
			#self.update_plots()
			qtw.QApplication.processEvents()
		run_time_end = timer() - run_timer
		print(f"Done {comparisons} comparisons in {run_time_end:,} sec at {(comparisons/run_time_end):,.2f} comparisons/sec")
		self.traider.portfolio.evaluate()