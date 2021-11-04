import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as qtw

import pyqtgraph as pg

from SystemClock import SystemClock

from Setter import Setter
import sys
from collections import defaultdict

class MainWindow(qtw.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		self.setWindowTitle("The Backtrading Machine")
		self.setGeometry(200,200,1000,800)
		self.centralwidget = qtw.QWidget()
		self.centralwidget.setLayout(qtw.QGridLayout())
		self.layout().setSpacing(0)
		self.setCentralWidget(self.centralwidget)

		#self.setLayout(qtw.QVBoxLayout())
		self.assemble()

	def assemble(self):
		self.vitals_block = VitalsBlock()
		self.plot_pad = PlotPad()
		self.stock_watch = StockWatch(self.plot_pad)
		self.portfolio_block = PortfolioBlock() 

		self.setter = Setter(self.vitals_block, self.plot_pad, self.stock_watch, self.portfolio_block)

		self.settings_group = SettingsGroup(self.plot_pad, self.setter, self.stock_watch)
		
		# Add elements to central-widget
		self.vitals_block.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
		#self.plot_pad.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)
		self.settings_group.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
		self.stock_watch.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum)
		self.portfolio_block.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum)

		self.centralwidget.layout().addWidget(self.vitals_block,0,0,1,1)
		self.centralwidget.layout().addWidget(self.plot_pad,1,0,3,3)
		self.centralwidget.layout().addWidget(self.settings_group,4,0,1,1)
		self.centralwidget.layout().addWidget(self.stock_watch,0,4,4,1)
		self.centralwidget.layout().addWidget(self.portfolio_block,4,1,1,2)

class PlotPad(pg.GraphicsLayoutWidget):
	def __init__(self):
		super (PlotPad, self).__init__()
		#self.plot_dict = None

	def create_plot(self):
		date_axis = pg.DateAxisItem(orientation='bottom')
		plot_obj = pg.PlotItem(axisItems = {'bottom': date_axis})
		plot_obj.addLegend()
		self.addItem(plot_obj, row=self.nextRow())
		return plot_obj

	def remove_plot(self, plot_obj):
		self.removeItem(plot_obj)

	def clear_plot(self):
		self.clear()
	

class StockWatch(qtw.QScrollArea):
	def __init__(self, plot):
		super(StockWatch, self).__init__()
		self.plot = plot
		self.setter = None
		self.setMinimumWidth(160)
		self.setMaximumWidth(160)
		self.setWidgetResizable(True)
		self.setLayout(qtw.QVBoxLayout())


		self.cb = defaultdict()
		self.plots = defaultdict()

	def init_stock_watch(self, setter, start_date):
		self.setter = setter
		if len(self.cb.keys()) != 0:
			for button in self.cb.values():
				button.setParent(None)
		#self.layout().clearLayout()
		for security in setter.market:
			try:
				self.cb[security] = qtw.QCheckBox(f"{security}: {security.last_known():,.2f}")
			except:
				self.cb[security] = qtw.QCheckBox(f"{security}: Nan")
			finally:
				self.cb[security].stateChanged.connect(lambda _, state=self.cb[security], stock=security : self.btn_state(state, stock))
				self.layout().addWidget(self.cb[security])

	def update(self):
		for stock, button in self.cb.items():
			#self.updateStockPlot()
			try:
				button.setText(f"{stock}: {stock.last_known():,.2f}")
			except KeyError:
				#print("No price")
				continue

	def btn_state(self, state, stock):
		if state.isChecked():
			self.plots[stock] = self.plot.create_plot()
			#self.curves[stock] = []
			self.setter.initStockPlot(stock)
			self.setter.updateStockPlot()
		else:
			print("Unchecked")
			self.plot.remove_plot(self.plots[stock])
			del self.plots[stock]

class SettingsGroup(qtw.QWidget):
	def __init__(self, plotPad, setter, stock_watch):
		super(SettingsGroup, self).__init__()
		self.plot_pad = plotPad
		self.setter = setter
		self.stock_watch = stock_watch
		self.setLayout(qtw.QGridLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(0,0,0,0)

		self.date_pad = DatePad(self.setter)
		self.market_pad = MarketPad(self.setter)
		self.strategy_block = StrategyPad(self.setter)
		self.key_pad = KeyPad(self.plot_pad, self.setter, self.stock_watch)
		
		self.layout().addWidget(self.date_pad,0,0,1,1)
		self.layout().addWidget(self.market_pad,1,0,1,1)

		self.layout().addWidget(self.strategy_block,0,1,1,1)
		self.layout().addWidget(self.key_pad,1,1,1,1)


class KeyPad(qtw.QWidget):
	def __init__(self, plotPad, setter, stock_watch):
		super(KeyPad, self).__init__()
		self.plot_pad = plotPad
		self.setter = setter 
		self.stock_watch = stock_watch
		self.setLayout(qtw.QHBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(0,0,0,0)


		self.btn_run = qtw.QPushButton("run", clicked = lambda: self.setter.run())
		self.btn_clear_plot = qtw.QPushButton("Clear Plot", clicked = self.plot_pad.clear_plot)

		self.layout().addWidget(self.btn_run)
		self.layout().addWidget(self.btn_clear_plot)


class MarketPad(qtw.QWidget):
	def __init__(self, setter):
		super(MarketPad, self).__init__()
		self.setter = setter
		self.setLayout(qtw.QGridLayout())
		self.layout().setSpacing(0)
	#	self.layout().setContentsMargins(0,0,0,0)

		market_block = qtw.QWidget()
		market_block.setLayout(qtw.QGridLayout())

		self.market_from = qtw.QComboBox()
		self.market_from.addItems(self.setter.market_input_method)
		self.market_from.currentTextChanged.connect(self.set_market)

		self.market_select = qtw.QComboBox()
		self.market_select.addItems(self.setter.market_list)
		self.market_select.currentTextChanged.connect(self.set_market)

		btn_get_market = qtw.QPushButton("Get market", clicked = self.get_market)
		btn_save_market = qtw.QPushButton("Save market to csv", clicked = self.save_market)

		self.layout().addWidget(self.market_from,0,0)
		self.layout().addWidget(self.market_select,0,1)
		self.layout().addWidget(btn_get_market,1,0)
		self.layout().addWidget(btn_save_market,1,1)

	def set_market(self):
		self.setter.market_name = self.market_select.currentText()
		self.setter.market_source = self.market_from.currentText()
		print(f"Setting market {self.setter.market_name} {self.setter.market_source}")

	def get_market(self):
		self.setter.init_market()

	def save_market(self):
		print(f"Saving {self.setter.market.market} to dir")
		self.setter.market.save_to_dir()


class DatePad(qtw.QWidget):
	def __init__(self, setter):
		super(DatePad, self).__init__()
		self.setter = setter
		self.setLayout(qtw.QGridLayout())
		self.layout().setSpacing(0)
		
	  # Start Date
		de_start_label = qtw.QLabel("Start Date")
		self.de_start = qtw.QDateEdit(displayFormat=("yyyy-MM-d"))
		self.de_start.setDate(QtCore.QDate(self.setter.clock.start))
		self.de_start.setCalendarPopup(True)
		self.de_start.dateChanged.connect(self.set_date)

	 	# End date
		de_end_label = qtw.QLabel("End Date")
		self.de_end = qtw.QDateEdit(displayFormat=("yyyy-MM-d"))
		self.de_end.setDate(QtCore.QDate(self.setter.clock.end))
		self.de_end.setCalendarPopup(True)
		self.de_end.dateChanged.connect(self.set_date)

	 	# Add to block
		self.layout().addWidget(de_start_label,0,0)
		self.layout().addWidget(self.de_start,0,1)
		self.layout().addWidget(de_end_label,1,0)
		self.layout().addWidget(self.de_end,1,1)

	def set_date(self):
		self.setter.clock.start = self.de_start.dateTime().toPython()
		self.setter.clock.end = self.de_end.dateTime().toPython()
		print(f"Setting start date to:{self.setter.clock.start} and end date to:{self.setter.clock.end}")


class StrategyPad(qtw.QWidget):
	def __init__(self, setter):
		super(StrategyPad,self).__init__()
		self.setter = setter
		self.setLayout(qtw.QVBoxLayout())

		self.layout().setSpacing(0)

		self.layout().addWidget(self.init_strategy_select())
		self.layout().addWidget(self.init_strategy_setting())	

	def init_strategy_select(self):
		strategy_select_block = qtw.QWidget()
		strategy_select_block.setLayout(qtw.QHBoxLayout())

		self.sb_cash = qtw.QSpinBox()
		self.sb_cash.setRange(0, 1000000000)
		self.sb_cash.setValue(self.setter.cash)
		self.sb_cash.valueChanged.connect(self.set_strategy)

		self.strategy_select = qtw.QComboBox()
		self.strategy_select.addItems(self.setter.strategy_list)
		self.strategy_select.currentTextChanged.connect(self.set_strategy)

		strategy_select_block.layout().addWidget(self.strategy_select)
		strategy_select_block.layout().addWidget(self.sb_cash)
		return strategy_select_block

	def init_strategy_setting(self):
		strategy_setting_block = qtw.QWidget()
		strategy_setting_block.setLayout(qtw.QGridLayout())

		shortStep_label = qtw.QLabel("Short Step")
		self.sb_shortStep = qtw.QSpinBox()
		self.sb_shortStep.setRange(0, 720)
		self.sb_shortStep.setValue(self.setter.strategy_arg[0])
		self.sb_shortStep.valueChanged.connect(self.set_strategy)

		longStep_label = qtw.QLabel("Long Step")
		self.sb_longStep = qtw.QSpinBox()
		self.sb_longStep.setRange(0, 720)
		self.sb_longStep.setValue(self.setter.strategy_arg[1])
		self.sb_longStep.valueChanged.connect(self.set_strategy)

		strategy_setting_block.layout().addWidget(shortStep_label,0,0)
		strategy_setting_block.layout().addWidget(self.sb_shortStep,0,1)
		strategy_setting_block.layout().addWidget(longStep_label,1,0)
		strategy_setting_block.layout().addWidget(self.sb_longStep,1,1)
		return strategy_setting_block

	def set_strategy(self, strategy):
		self.setter.cash = self.sb_cash.value()
		self.setter.strategy_name = self.strategy_select.currentText()
		self.setter.strategy_arg = [self.sb_shortStep.value(), self.sb_longStep.value()]
		print(self.setter.cash, self.setter.strategy_name, self.setter.strategy_arg)
		self.setter.init_strategy()

class VitalsBlock(qtw.QWidget):
	def __init__(self):
		super(VitalsBlock, self).__init__()
		self.setLayout(qtw.QGridLayout())

		self.datetime_label = qtw.QLabel("Time:")
		self.balance_label = qtw.QLabel("Balance:")
		self.total_value_label = qtw.QLabel("Total Value:")
		self.CAGR_label = qtw.QLabel("CAGR:")

		self.layout().addWidget(self.datetime_label,0,0)
		self.layout().addWidget(self.balance_label,0,1)
		self.layout().addWidget(self.total_value_label,0,2)
		self.layout().addWidget(self.CAGR_label,0,3)

	def update(self, traider):
		time = traider.clock.time.date() 
		balance = traider.portfolio.balance
		total_value = traider.portfolio.total_value
		CAGR = traider.portfolio.performance.CAGR(traider.clock.start, traider.clock.time)

		self.datetime_label.setText(f"Time:{time}")
		self.balance_label.setText(f"Balance:{balance:,.2f}")
		self.total_value_label.setText(f"Total Value:{total_value:,.2f}")
		self.CAGR_label.setText(f"CAGR:{CAGR:.2f}%")

		self.datetime_label.adjustSize()
		self.balance_label.adjustSize()
		self.total_value_label.adjustSize()
		self.CAGR_label.adjustSize()
		#qtw.QApplication.processEvents()


class PortfolioBlock(qtw.QScrollArea):
	def __init__(self):
		super(PortfolioBlock, self).__init__()
		self.setLayout(qtw.QVBoxLayout())
		self.setWidgetResizable(True)
		self.layout().setSpacing(0)
		self.potrf = defaultdict(int)

	def update(self, traider):
		for label in self.potrf.values():
			label.setParent(None)

		self.potrf = defaultdict()
		for stock, owned in traider.portfolio.owned.items():
			text = f"{owned} * {stock} at value {owned*stock.last_known():,.2f}"
			self.potrf[stock] = qtw.QLabel(text)
			self.layout().addWidget(self.potrf[stock])

class main():
	def __init__(self):
		self.window()

	def window(self):
		app = qtw.QApplication(sys.argv)
		app.setStyle("Fusion")
		palette = QtGui.QPalette()
		palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
		palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
		palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
		palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
		palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
		palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
		palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
		palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
		palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
		palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
		palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
		palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
		palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
		app.setPalette(palette)
		win = MainWindow()
		win.show()
		sys.exit(app.exec_())

main()