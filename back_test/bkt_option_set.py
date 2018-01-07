import datetime
class OptionSet(object):

    def __init__(self,option_dic):
        self.option_set = option_dic

    def set_mdt1(self):
        mdt = datetime.date(2017,1,1) # maturity 1
        # TODO get all options with maturity == maturity 1
        optiondic_mdt1 = self.option_set
        self.set_mdt1 = optiondic_mdt1

    # TODO : maturity 2-4 are the same as mdt1
    def set_mdt2(self):
        mdt = datetime.date(2017,2,1) # maturity 2

    