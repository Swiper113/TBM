from Security import Security

class Index(Security):
	preferred_val = "norm"
	def __init__(self, clock, ticker, data):
		super().__init__(clock, ticker, data)
		self.type = "index"
		self.preferred_val = "norm"

	def normalize(self, time, normalize = 1, price_type = "Close"):
		index_slice = self.data.loc[time:].copy()
		base_value = index_slice[price_type].iat[0]
		norm_mod = normalize/base_value
		index_slice["norm"] = index_slice[price_type] * norm_mod
		self.data["norm"] = self.data[price_type] * norm_mod
		return index_slice