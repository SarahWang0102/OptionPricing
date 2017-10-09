

class SviInputSet:


    def __init__(self,evalDate):
        self.evalDate = evalDate
        self.dataSet = {}

    def update_data(self,mdate,strike,moneyness,volatility,ttm,totalvariance,close,open):
        if mdate not in self.dataSet.keys():
            data_mdate = SviInputOneMaturity(mdate)
            data_mdate.add_data(strike,moneyness,volatility,totalvariance,close,open)
            data_mdate.ttm = ttm
            self.dataSet.update({mdate:data_mdate})
        else:
            self.dataSet.get(mdate).add_data(strike,moneyness,volatility,totalvariance,close,open)


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

    def add_data(self,strike,moneyness,volatility,totalvariance,close,open):
        self.strike.append(strike)
        self.moneyness.append(moneyness)
        self.volatility.append(volatility)
        self.close.append(close)
        self.open.append(open)
        self.totalvariance.append(totalvariance)

