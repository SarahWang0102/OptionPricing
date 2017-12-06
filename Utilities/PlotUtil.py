import matplotlib.pyplot as plt

class PlotUtil:

    def __init__(self):

        plt.rcParams['font.sans-serif'] = ['STKaiti']
        plt.rcParams.update({'font.size': 15})
        self.c1 = "#CC0000"
        self.c2 = "#8C8C8C"
        self.c3 = "#FF6464"
        self.c4 = "#1E1E1E"
        self.c5 = "#FFC8C8"
        self.c6 = "#5A5A5A"
        self.c7 = "#FF9664"
        self.c8 = "#B4B4B4"
        self.c9 = "#FFD27D"
        self.c10 = "#918CD7"

        self.dash = [7,2,3,2]

        self.l1 = "-"
        self.l2 = "-"
        self.l3 = "--"
        self.l4 = "--"
        self.l5 = "-."
        self.l6 = self.l3
        self.l7 = self.l1
        self.l8 = self.l3
        self.l9 = self.l1
        self.l10 = self.l2

        self.date_fmt = "%m/%y"

        self.colors = [self.c1,self.c2,self.c3,self.c4,self.c5,self.c6,self.c7,self.c8,self.c9,self.c10]
        self.lines = [self.l1, self.l2, self.l3, self.l4, self.l5, self.l6, self.l7, self.l8, self.l9, self.l10]


    def set_frame(self,axarrs):
        for axarr in axarrs:
            axarr.spines['right'].set_visible(False)
            axarr.spines['top'].set_visible(False)
            axarr.yaxis.set_ticks_position('left')
            axarr.xaxis.set_ticks_position('bottom')
        return axarrs

    def plot_line(self,ax,count,x,y,lgd='' ,x_label='', y_label=''):
        c = self.colors[count]
        l = self.lines[count]
        if lgd == '':
            if count == 3:
                tmp, = ax.plot(x, y, color=c, linestyle=l, linewidth=2)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2.3)
            else:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2)
        else:
            if count == 3:
                tmp, = ax.plot(x, y, color=c, linestyle=l, linewidth=2, label=lgd)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2.3, label=lgd)
            else:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2, label=lgd)
        ax.legend()
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])

    def get_figure(self,x,Y,legends,x_label='',y_label=''):
        f, ax = plt.subplots()
        for idx,y in enumerate(Y):
            lgd = legends[idx]
            self.plot_line(ax,idx,x,y,lgd)
        ax.legend()
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])
        return f