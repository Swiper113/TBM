from pprint import pprint
import numpy as np
#from numpy import nanmean, float64, isnan, array, int32, int64, empty, nan
from datetime import datetime, timedelta

from pandas import DataFrame, read_csv, to_datetime, bdate_range, Timestamp
from pandas.tseries.offsets import BDay, CustomBusinessDay
from pandas.tseries.holiday import Easter
from pandas_datareader import DataReader 

class Security():
	def __init__(self, clock, ticker, data):
		self.clock = clock
		self.type = "Security"
		self.ticker = ticker
		self.name = ticker
		self.data = data

		self.time = None
		self.price = None
		self.last_price = None

	def __repr__(self):
		return self.ticker

	def __str__(self):
		return self.name

	@property
	def data_start(self):
		return self.data.index.min()

	@property
	def data_end(self):
		return self.data.index.max()

	@property
	def var(self):
		return self.data["Close"].loc[self.clock.time - timedelta(days=365):self.clock.time].var()

	@property
	def std(self):
		return self.data["Close"].loc[self.clock.time - timedelta(days=365):self.clock.time].std()

	@property
	def alpha(self):
		pass
	
	@property
	def beta(self):
		pass

	@property
	def last_known_price(self):
		try:
			self.last_price = self.close
		except KeyError:
			pass
		return self.last_price

	@property
	def close(self):
		return self.data.at[self.clock.time, "Close"]

	@classmethod
	def from_source(cls, clock, ticker, source="yahoo"):
		print(f"Getting:{ticker}, from source:{source}\n", end="")
		start = clock.start
		end = clock.end
		security_df = DataReader(ticker, data_source=source, start=start, end=end)
		security_df.index = to_datetime(security_df.index, infer_datetime_format=True)
		security_df = security_df.dropna()
		return cls(clock, ticker, security_df)

	@classmethod
	def from_dir(cls, clock, filename):
		ticker = filename.split("/")[-1].strip(".csv")
		print(f"Getting:{ticker}, from:{filename}\n", end="")
		security_df = read_csv(filename, index_col="Date", parse_dates=True, infer_datetime_format= True)
		return cls(clock, ticker, security_df)

	def get_price(self, time, price_type="Close"):
		return self.data.at[time, price_type]
	
	def calcSmva(self, time, slice_len, price_type="Close"):
		i_time = self.data.index.get_loc(time)
		smva = self.data[price_type].iloc[(i_time - slice_len):i_time+1].mean()
		self.data.at[time, f"AVL:{slice_len}"] = smva
		return smva
	
	def smva(self, time, slice_len, price_type="Close"):
		try:
			smva = self.data.at[time, f"AVL:{slice_len}"]
			if(np.isnan(smva)):
				return self.calcSmva(time, slice_len, price_type="Close")
			return smva
		except KeyError:
			return self.calcSmva(time, slice_len, price_type="Close")

	
	def get_CAGR(self, start, end):
		years = (end.date()+ timedelta(days=1) - start.date()).days/365
		total_return = self.last_known_price/self.get_price(start)
		CAGR = ((total_return**(1/years))-1)*100
		return CAGR

	def update(self, time, price_type="Close"):
		pass
	
	def reset(self, strategy):
		self.curves = []
		self.time = None
		#self.plot_obj = None
		self.buy_sell_flag = None
		self.buy_sell_flag = DataFrame(columns= ["Time", "Price", "Buy", "Sell","Miss","Num", strategy.short_step_tag, strategy.long_step_tag])
