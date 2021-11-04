from math import sqrt, exp

class RealOption():
	def __init__(self, portfolio, dif):
		self.portfolio = portfolio
		self.dif = dif
		self.exp = 1
		self.con = 0.5
		self.steps = 3

	def main(self, stock, price):
		#owned = self.portfolio.owned(stock)
		owned = 0
		buy = 1
		#price = stock.close
		#price = 100
		value = price * (owned if owned !=0 else buy)
		self.rf = 0.10
		#self.rf = self.portfolio.CAGR
		#std = stock.std
		std = 0.15

		t = 1
		n = 1

		self.up = exp(std*sqrt(t/n))
		self.down = 1/self.up
		print(f"up:{self.up}, down:{self.down}")

		self.prob_up = (exp(self.rf*sqrt(t/n))-self.down) / (self.up - self.down)
		self.prob_down = 1 - self.prob_up
		print(f"prob up:{self.prob_up}")
		
		print(self.eNPV(value, 0))

	def eNPV(self, value, steps):
		value_up = value*self.up
		value_down = value*self.down
		if steps <= self.steps:
			step = steps + 1
			normal = (self.prob_up*self.eNPV(value_up, step) + self.prob_down*self.eNPV(value_down, step)) / (1+self.rf)
			exp = (normal * (1 + self.exp)) - value*self.exp
			con = (normal * self.con) + value*(1-self.con)
			abb = value
			#abb = 100* 1.1**steps
			#enpv = max(value, normal, exp - value*self.exp, con + value*(1-self.con), abb)
			enpv = max(normal, exp, con, abb)
			#print(f"step:{steps}, value:{value:,.2f} normal:{normal:,.2f}, exp:{exp - value*self.dif:,.2f}, con:{con + value*self.dif:,.2f}, abb:		{abb:,.2f}")
			print(f"step:{steps}, normal:{normal:,.2f}, exp:{exp:,.2f}, con:{con:,.2f}, abb:{abb:,.2f}")
			return enpv
		else:
			return value




ro = RealOption(2, 0.5)
ro.main(1)