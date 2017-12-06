import matplotlib.pyplot as plt


c1 = "#CC0000"
c2 = "#8C8C8C"
c3 = "#FF6464"
c4 = "#1E1E1E"
c5 = "#FFC8C8"
c6 = "#5A5A5A"
c7 = "#FF9664"
c8 = "#B4B4B4"
c9 = "#FFD27D"
c10 = "#918CD7"

dash = [7,2,3,2]

l1 = "-"
l2 = "-"
l3 = "--"
l4 = "--"
l5 = "-."
l6 = l3
l7 = l1
l8 = l3
l9 = l1
l10 = l2

def set_frame(axarrs):
    for axarr in axarrs:
        axarr.spines['right'].set_visible(False)
        axarr.spines['top'].set_visible(False)
        axarr.yaxis.set_ticks_position('left')
        axarr.xaxis.set_ticks_position('bottom')

def get_figure(x,Y,legends,x_label='',y_label=''):
    plt.rcParams['font.sans-serif'] = ['STKaiti']
    plt.rcParams.update({'font.size': 13})
    f, ax = plt.subplots()
    for idx,y in enumerate(Y):
        lgd = legends[idx]
        print('c'+str(idx+1),'l'+str(idx+1))
        print(x)
        print(y)
        # 'l'+str(idx+1)
        ax.plot(x, y, color='c'+str(idx+1), line=l1, linewith=2, label=lgd)
    ax.legend()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    set_frame([ax])
    return f