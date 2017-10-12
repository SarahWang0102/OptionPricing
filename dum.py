class dum:

    def __init__(self,date='nan',x=[0,0,0]):
        self.a = x[0]
        self.b = x[1]
        self.c = x[2]
        self.date = date
    def __str__(self):
        return 'a'+str(self.a)+'\tb'+str(self.b) + '\tc'+str(self.c)

ret = {}
ret.update({'Jan 1st':dum([1,1,1])})
ret['Jan 2nd'] = dum([2,2,2])
print(ret)
ret['Jan 2nd'].c = 33333
print(ret)
