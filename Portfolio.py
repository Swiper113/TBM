from collections import defaultdict
from pandas import DataFrame, Timestamp, MultiIndex
import numpy as np

from Index import Index

class Portfolio():
    def __init__(self, clock, balance, market):
        self.clock = clock
        self.market = market

        self.starting_balance = balance
        self.balance = balance
        self.owned = defaultdict(int)
        self.history = DataFrame(columns=["Time", "Security", "Num", "Price", "Amount"])

        self.benchmark = self.market.index

        #self.performance = DataFrame(columns= ["norm_Close", "Total"])
        norm_close = self.benchmark.normalize(self.clock.start, self.starting_balance)
        print(self.benchmark)
        
        self.performance = Index(self.clock, "Portfolio", norm_close)
        self.performance.data["Close"] = np.NaN
        print(self.performance.data)
        self.performance.data["Close"].at[self.clock.time] = self.total_value
        self.performance.data["Close"] = self.performance.data.Close.astype(np.float64)

    @property
    def value(self):
        value = 0
        for security, owned in self.owned.items():
            value += security.last_known() * owned
        return value

    @property
    def total_value(self):
        total_value = self.value + self.balance
        return total_value

    @property
    def holding_performance(self):
        total = 0
        #for security in self.market.securitys:
        traided =  self.history["Security"].unique()
        #print(securitys)
        for security in traided:
            filt = self.history["Security"] == security
            transactions = self.history.loc[filt]
            
            #print(transactions.Num , self.num_owned(security), " : ",  transactions.Num.sum())

            ret = security.last_known()*self.num_owned(security) + transactions.Amount.sum()
            total += ret
            print(f"{security}, {ret:,.2f}")
        print(f"Total return: {total:,.2f}")

    
    def num_owned(self, security):
        if security in self.owned:
            return self.owned.get(security)
        else:
            return 0

    def print_portfolio(self):
        for security, owned in self.owned.items():
            value = security.last_known_price * owned
            print(f"{security}: {owned} at a value of: {value:,.2f}")

    def evaluate(self):
        start = self.clock.start
        time = self.clock.time
        print(self.benchmark.data)
        print(self.performance.data)

        index_CAGR = self.benchmark.CAGR(self.clock.start, time)
        print(f'''Balance:{self.balance:,.2f} Holding Value:{self.value:,.2f}
              Total:{self.total_value:,.2f} 
              \nwith a yearly return of {self.performance.CAGR(start, time):,.2f}% 
              and market return of:{index_CAGR:,.2f}%''')
        print(f'''Alpha of:{self.performance.alpha(self.benchmark):.2f}%
              and Beta of:{self.performance.beta(self.benchmark):.2f}''')
        #self.holding_performance

    def update(self):
        self.performance.data.Close.at[self.clock.time] = self.total_value

class PortfolioManager():
    def __init__(self, clock, portfolio, max_buy = 0.1):
        self.clock = clock
        self.portfolio = portfolio
        self.max_buy = max_buy

    def buy(self, security, price, num):
        self.portfolio.balance -= float(price * num)
        self.portfolio.owned[security] += num

    def sell(self, security, price, num):
        self.portfolio.balance += float(price * num)
        self.portfolio.owned[security] -= num
        del self.portfolio.owned[security]

    def order(self, security, price, flag):
        try:
            balance = self.portfolio.balance
            portion_size = int(balance * self.max_buy)
            num = int(portion_size//price)
            buy_cond = num > 0 and price < balance
            sell_cond = security in self.portfolio.owned.keys()

            if flag == "Sell" and sell_cond:
                num = self.portfolio.owned[security]
                self.sell(security, price, num)

                self.portfolio.history = self.portfolio.history.append(
                    {"Time":self.clock.time, 
                    "Security":security, 
                    "Num":-num, 
                    "Price":price,
                    "Amount": num*price
                    }, ignore_index=True)
                print(f"  {flag}:{num} {security} at:{price:,.2f} Balance:{self.portfolio.balance:,.2f}")
            elif flag == "Buy" and buy_cond:
                self.buy(security, price, num)

                self.portfolio.history = self.portfolio.history.append(
                    {"Time":self.clock.time, 
                    "Security":security, 
                    "Num":num, 
                    "Price":price,
                    "Amount": num*-price
                    }, ignore_index=True)
                print(f"  {flag}:{num} {security} at:{price:,.2f} Balance:{self.portfolio.balance:,.2f}")
            elif flag == "Buy":
                flag = "Miss"

                self.portfolio.history = self.portfolio.history.append(
                    {"Time":self.clock.time, 
                    "Security":security, 
                    "Num":0, 
                    "Price":price,
                    "Amount": 0
                    }, ignore_index=True)
                print(f"  {flag}:{num} {security} at:{price:,.2f} Balance:{self.portfolio.balance:,.2f}")

        except ValueError:
            print(f"price is:{price}")