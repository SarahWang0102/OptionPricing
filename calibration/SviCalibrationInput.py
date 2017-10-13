

class SviInputSet:


    def __init__(self,evalDate,spot):
        self.evalDate = evalDate
        self.spot = spot
        self.dataSet = {}

    def update_data(self,mdate,strike,moneyness,volatility,ttm,totalvariance,close,open,amount=0.0):
        if mdate not in self.dataSet.keys():
            data_mdate = SviInputOneMaturity(mdate)
            data_mdate.add_data(strike,moneyness,volatility,totalvariance,close,open,amount)
            data_mdate.ttm = ttm
            self.dataSet.update({mdate:data_mdate})
        else:
            self.dataSet.get(mdate).add_data(strike,moneyness,volatility,totalvariance,close,open,amount)


class SviInputOneMaturity:


    def __init__(self , mdate):
        self.mdate=mdate
        self.ttm = ''
        self.strike = []
        self.moneyness = []
        self.volatility = []
        self.totalvariance = []
        self.close = []
        self.open = []
        self.volums = []

    def add_data(self,strike,moneyness,volatility,totalvariance,close,open,amount=0.0):
        self.strike.append(strike)
        self.moneyness.append(moneyness)
        self.volatility.append(volatility)
        self.close.append(close)
        self.open.append(open)
        self.totalvariance.append(totalvariance)
        self.volums.append(amount)

