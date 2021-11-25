# Standard librarys
from os import listdir, mkdir, path
import concurrent.futures
import itertools


from Security import Security
from Index import Index 


# Class handles securitys and indexes in a given market
class Market():							
    def __init__(self, clock, market, currency, securitys):
        self.clock = clock
        self.market = market
        self.currency = currency
        self.securitys = securitys

        self.data_start, self.data_end = self.data_range()
        self.index = Index.from_source(self.clock, self.market, "yahoo")

    def __repr__(self):
        return "{} {} {} {}".format(self.market, self.currency, self.data_start, self.data_end)

    def __str__(self):
        return self.market

    def __iter__(self):
        for security in self.securitys:
            yield security
    
    def __len__(self):
        return len(self.securitys)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.securitys[key]

        elif isinstance(key, str):
            for security in self.securitys:
                if str(security) == key:
                    return security

        print(key, "not in market")
        return None

    def __contains__(self, security):
        if isinstance(security, Security):
            return security in self.securitys
        elif isinstance(security, str):
            for security in self.securitys:
                if str(security) == security:
                    return True
        else:
            return False
    
    def data_range(self):
        data_start = None
        data_end = None
        for security in self.securitys:
            data_start = security.data_start if data_start == None or security.data_start < data_start else data_start
            data_end = security.data_end if data_end == None or security.data_end > data_end else data_end
        return (data_start, data_end)

    @classmethod
    def from_dir(cls, clock, market, currency):
        print("Getting data from dir")
        path_list = [f"{market}/{filename}" for filename in listdir(market)]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            securitys = list(executor.map(Security.from_dir, itertools.repeat(clock), path_list))
        return cls(clock, market, currency, securitys)

    @classmethod
    def from_source(cls, clock, market, currency):
        securitys = []
        market_list = []
        with open(f"ticker_list/{market}.txt") as fin:
            for ticker in fin.read().split(","):
                market_list += [ticker.strip(" ")]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            securitys = list(executor.map(Security.from_source, itertools.repeat(clock), market_list))
        return cls(clock, market, currency, securitys)

    def save_to_dir(self):
        print("Saving to dir")
        new_dir = str(self.market)
        if not path.exists(new_dir):
            mkdir(new_dir)
        for security in self.securitys:
            security.data.to_csv(f"{new_dir}/{security.ticker}.csv", index="Date")


