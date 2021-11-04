from pprint import pprint
import numpy as np
#from numpy import nanmean, float64, isnan, array, int32, int64, empty, nan
from datetime import datetime, timedelta

from pandas import DataFrame, read_csv, to_datetime, bdate_range, Timestamp
from pandas.tseries.offsets import BDay, CustomBusinessDay
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

		self.preferred_val = "Close"

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

	
	def last_known(self, time = 0):
		if time == 0:
			time = self.clock.time
		try:
			return self.data[time]
		except KeyError:
			return self.data[self.preferred_val].loc[:time].iloc[-1]

	
	# def normalize(self, time, normalize = 1, price_type="Close"):
	# 	index_slice = self.data.loc[time:].copy()
	# 	base_value = index_slice[price_type].iat[0]
	# 	norm_mod = normalize/base_value
	# 	index_slice["norm"] = index_slice[price_type] * norm_mod
	# 	return index_slice

	def var(self):
		return self.data["Close"].loc[self.clock.time - timedelta(days=365):self.clock.time].var()

	def std(self):
		return self.data["Close"].loc[self.clock.time - timedelta(days=365):self.clock.time].std()

	def cov(self, bench_mark):
		return self.data["Close"].cov(bench_mark.data["norm"])

	def CAGR(self, start, end):
		years = self.clock.yearsFromStart()
		total_return = self.last_known(end)/self.last_known(start)
		CAGR = ((total_return**(1/years))-1)*100
		return CAGR

	def expected_return(self, bench_mark, risk_free_return = 0):
		return risk_free_return + self.beta(bench_mark)*(bench_mark.CAGR(self.clock.start, self.clock.time) - risk_free_return)

	def alpha(self, bench_mark):
		return self.CAGR(self.clock.start, self.clock.end) - self.expected_return(bench_mark)
	
	def beta(self, bench_mark):
		return self.cov(bench_mark)/bench_mark.var()

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


