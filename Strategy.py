# Standard librarys
from datetime import date, datetime, timedelta
from os import listdir, mkdir, path
from time import time as timer
from collections import defaultdict
#from statistics import mean
import sys

# Third party librarys
from numpy import nanmean, mean, float64, isnan, array, int64, empty

from pandas import DataFrame, read_csv, to_datetime, bdate_range
from pandas.tseries.offsets import BDay, CustomBusinessDay
from pandas.tseries.holiday import Easter
from pandas_datareader import DataReader 

class Golden_Cross():
    def __init__(self, short_step, long_step):
        self.short_step = short_step
        self.long_step = long_step
        self.name = "Golden Cross"
        self.abbreviation = "GC"
        self.short_step_tag = f"AVL:{self.short_step}"
        self.long_step_tag = f"AVL:{self.long_step}"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def logic(self, stock, current_price):
        flag = None
        #last_short = stock.buy_sell_flag[self.short_step_tag].iat[-1]
        #last_long = stock.buy_sell_flag[self.long_step_tag].iat[-1]
        mva_s = stock.smva(stock.clock.time, self.short_step)
        mva_l = stock.smva(stock.clock.time, self.long_step)
        last_short = stock.smva(stock.clock.time - BDay(1), self.short_step)
        last_long = stock.smva(stock.clock.time - BDay(1), self.long_step)
        #print("L/S ",last_long, last_short)
        #print(stock.clock.time-BDay(1), " ", stock.clock.time)

        if mva_s <= mva_l and last_short > last_long:
            flag = "Sell"
        elif mva_s >= mva_l and last_short < last_long:
            flag = "Buy"
        return flag

    def main(self, stock, price):
        #price = stock.price
        #mva_s = stock.smva(self.short_step)
        #mva_l = stock.smva(self.long_step)
        flag = None
        try:


            flag = self.logic(stock, price)
            #print("Flag ", flag)
            #stock.buy_sell_flag.at[stock.clock.time, self.short_step_tag] = mva_s
            #stock.buy_sell_flag.at[stock.clock.time, self.long_step_tag] = mva_l
        except IndexError:
            print("Cant compute MA")
            #stock.buy_sell_flag.at[stock.clock.time, self.short_step_tag] = price 
            #stock.buy_sell_flag.at[stock.clock.time, self.long_step_tag] = price
        #stock.buy_sell_flag.at[stock.clock.time, "Price"] = price
        #print(stock.buy_sell_flag)
        return flag

class Golden_Vertex(Golden_Cross):
    def __init__(self, short_step, long_step):
        super().__init__(short_step, long_step)
        self.name = "Golden Vertex"
        self.abbreviation = "GV"

    def logic(self, stock, current_price):
        flag = None
        mva_s = stock.smva(stock.clock.time, self.short_step)
        mva_l = stock.smva(stock.clock.time, self.long_step)
        last_short = stock.smva(stock.clock.time - BDay(1), self.short_step)
        last_long = stock.smva(stock.clock.time - BDay(1), self.long_step)
        last_drv_s = last_short - stock.smva(stock.clock.time - BDay(2), self.short_step)
        drv_s = mva_s - last_short
        if (drv_s + last_drv_s) < 0:
            flag = "Sell"
        elif ((drv_s + last_drv_s) > 0) and (last_short < last_long) and (current_price < mva_l):
            flag = "Buy"
        return flag 


class Golden_Vertex_Greedy(Golden_Cross):
    def __init__(self, short_step, long_step):
        super().__init__(short_step, long_step)
        self.name = "Golden Vertex (Greedy)"
        self.abbreviation = "GV(G)"

    def logic(self, stock, current_price):
        flag = None
        mva_s = stock.smva(stock.clock.time, self.short_step)
        mva_l = stock.smva(stock.clock.time, self.long_step)
        last_short = stock.smva(stock.clock.time - BDay(1), self.short_step)
        last_long = stock.smva(stock.clock.time - BDay(1), self.long_step)
        last_drv_s = last_short - stock.smva(stock.clock.time - BDay(2), self.short_step)
        drv_s = mva_s - last_short
        if (drv_s + last_drv_s) < 0 and (current_price > mva_l):
            flag = "Sell"
        elif ((drv_s + last_drv_s) > 0) and (last_short < last_long) and (current_price < mva_l):
            flag = "Buy"
        return flag 
