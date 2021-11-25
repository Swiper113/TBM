from datetime import date, datetime, timedelta

class SystemClock():
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.time = start

    def yearsFromStart(self):
        return (self.time.date()+timedelta(days=1) - self.start.date()).days/365

    def setClock(self, start, end):
        self.start = start
        self.end = end
    
    def update(self, time):
        self.time = time
    
    