import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pylab as plt
import matplotlib.dates as mdate
import datetime as dt
from matplotlib.widgets import RadioButtons, Cursor
import re
import sys
import tkinter as tk
from tkinter import filedialog
import os as os
import time as ti
import scipy.spatial as spatial

def fmt(x, y, label):
    x=mdate.num2date(x)
    return 't: {x}\n{label}: {y:0.2e}'.format(x=dt.datetime.strftime(x, '%d-%m-%Y %H:%M:%S'), label=label, y=y)

class FollowDotCursor(object):
    """Display the x,y location of the nearest data point.
    https://stackoverflow.com/a/4674445/190597 (Joe Kington)
    https://stackoverflow.com/a/20637433/190597 (unutbu)
    """
    def __init__(self, ax, x_orig, y, label, formatter=fmt, offsets=(-20, 20)):
        try:
            x = np.asarray(x_orig, dtype='float')
        except (TypeError, ValueError):
            x = np.asarray(mdate.datestr2num(x_orig), dtype='float')
        y = np.asarray(y, dtype='float')
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        self.label=label
        self._points = np.column_stack((x, y))
        self.offsets = offsets
        y = y[np.abs(y - y.mean()) <= 3 * y.std()]
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('top')
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=130, color='#A4A4A4', alpha=0.7)
        self.annotation = self.setup_annotation()
        plt.connect('motion_notify_event', self)

    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax
        # event.inaxes is always the current axis. If you use twinx, ax could be
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x, y = self.snap(x, y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(x, y, self.label))
        self.dot.set_offsets((x, y))
        event.canvas.draw()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='yellow', alpha=0.75),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]

def laden(data):
    A = open(data,'r')
    lines = A.readlines()
    num_lines = len(lines)
    date = []
    time = []
    pressures=[[],[],[],[],[],[]]
    eventdate = []
    eventtime = []
    for i in range(0,num_lines):
        if i == 0:
            labels = parse_labels(lines[i])  #passes first line for label parsing, return list of labels
            #print('Parsed labels: ' + str(labels))
        if i!=0 and lines[i][0]!='#':
            date_roh=lines[i].split()[0].split('-')
            date.append(str(date_roh[1]+'-'+date_roh[0]+'-'+date_roh[2]))
            time.append(str(lines[i].split()[1]))
            for k in range(6):
                pressures[k].append(float(lines[i].split()[k+2]))
        ''' Program crashes when controller ressets names! '''
    A.close()
    return (date,time,pressures,labels)

def strip_tabs(string):
    ''' Replace mulpiple occurences of tabs to whitespace '''
    stripped = re.sub('\t', ' ',string)
    return stripped
    
def parse_labels(line):
    ''' Parse labels from input '''
    labels = [] #list to hold names of channels
    for i in line.split('\t'):
        if i!='' and i[-1]==']':
            labels.append(i.replace('[mbar]',''))
        elif i!='' and i[-1]=='\n':
            labels.append(i.replace('[mbar]\n',''))
        elif i!='':
            labels.append(i)
    return labels
 
#load_data=sys.argv[1]
root = tk.Tk()
root.withdraw()
load_data=filedialog.askopenfilename(filetypes=[('Pressure log file','*.log')])
root.destroy()

date,time,pressures,labels=laden(load_data)

times=[]    #should be list NOT list of lists
times_str=[]
max_times=0
max_times_str=''
for i,j in zip(date,time):
    times_str.append(str(i)+' '+str(j))
    times.append(mdate.datestr2num(str(i)+' '+str(j),)) #looks like [date time
    if times[-1]>max_times:
        max_times=times[-1]
        max_times_str=i.split('-')[1]+'-'+i.split('-')[0]+'-'+i.split('-')[2]+' '+j

fig,ax=plt.subplots(figsize=(10,6),dpi=100)
plt.xticks(rotation=45)
plt.subplots_adjust(left=0.2,bottom=0.25)
axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.05, 0.7, 0.10, 0.2], facecolor=axcolor)
radio = RadioButtons(rax, ('all', '12h', '3h', '1h','30min'))

col=['b','r','g','k','c','y']

lines=''
mars=2

def hzfunc(label):
    t0=0
    t1=30
    t2=1
    t3=3
    t4=12
    hzdict = {'all': t0, '30min': t1, '1h': t2, '3h': t3, '12h': t4}
    if hzdict[label]==t0:
        ax.set_xlim(min(times)-(max(times)-min(times))*0.05,max(times)+(max(times)-min(times))*0.05)
    elif hzdict[label]==t1:
        ax.set_xlim(dt.datetime.strptime(max_times_str,date_fmt)-dt.timedelta(minutes=hzdict[label])-dt.timedelta(minutes=hzdict[label])*0.05,dt.datetime.strptime(max_times_str,date_fmt)+dt.timedelta(minutes=hzdict[label]*0.05))
    else:
        ax.set_xlim(dt.datetime.strptime(max_times_str,date_fmt)-dt.timedelta(hours=hzdict[label])-dt.timedelta(hours=hzdict[label])*0.05,dt.datetime.strptime(max_times_str,date_fmt)+dt.timedelta(hours=hzdict[label]*0.05))
    plt.draw()
radio.on_clicked(hzfunc)

if pressures[0][-1]==1e11:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Underranged',color=col[0],marker='.',ms=mars,ls=lines)
elif pressures[0][-1]==1e12:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Overranged',color=col[0],marker='.',ms=mars,ls=lines)
elif pressures[0][-1]==1e13:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Error',color=col[0],marker='.',ms=mars,ls=lines)
elif pressures[0][-1]==1e14:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Off',color=col[0],marker='.',ms=mars,ls=lines)
elif pressures[0][-1]==1e15:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Not found',color=col[0],marker='.',ms=mars,ls=lines)
elif pressures[0][-1]==1e16:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' - Identification error',color=col[0],marker='.',ms=mars,ls=lines)
else:
    plot0,=ax.plot_date(times,pressures[0],label=labels[1]+' %.2e mbar'%pressures[0][-1],color=col[0],marker='.',ms=mars,ls=lines)
    
if pressures[1][-1]==1e11:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Underranged',color=col[1],marker='.',ms=mars,ls=lines)
elif pressures[1][-1]==1e12:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Overranged',color=col[1],marker='.',ms=mars,ls=lines)
elif pressures[1][-1]==1e13:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Error',color=col[1],marker='.',ms=mars,ls=lines)
elif pressures[1][-1]==1e14:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Off',color=col[1],marker='.',ms=mars,ls=lines)
elif pressures[1][-1]==1e15:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Not found',color=col[1],marker='.',ms=mars,ls=lines)
elif pressures[1][-1]==1e16:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' - Identification error',color=col[1],marker='.',ms=mars,ls=lines)
else:
    plot1,=ax.plot_date(times,pressures[1],label=labels[2]+' %.2e mbar'%pressures[1][-1],color=col[1],marker='.',ms=mars,ls=lines)

if pressures[2][-1]==1e11:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Underranged',color=col[2],marker='.',ms=mars,ls=lines)
elif pressures[2][-1]==1e12:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Overranged',color=col[2],marker='.',ms=mars,ls=lines)
elif pressures[2][-1]==1e13:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Error',color=col[2],marker='.',ms=mars,ls=lines)
elif pressures[2][-1]==1e14:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Off',color=col[2],marker='.',ms=mars,ls=lines)
elif pressures[2][-1]==1e15:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Not found',color=col[2],marker='.',ms=mars,ls=lines)
elif pressures[2][-1]==1e16:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' - Identification error',color=col[2],marker='.',ms=mars,ls=lines)
else:
    plot2,=ax.plot_date(times,pressures[2],label=labels[3]+' %.2e mbar'%pressures[2][-1],color=col[2],marker='.',ms=mars,ls=lines)

if pressures[3][-1]==1e11:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Underranged',color=col[3],marker='.',ms=mars,ls=lines)
elif pressures[3][-1]==1e12:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Overranged',color=col[3],marker='.',ms=mars,ls=lines)
elif pressures[3][-1]==1e13:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Error',color=col[3],marker='.',ms=mars,ls=lines)
elif pressures[3][-1]==1e14:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Off',color=col[3],marker='.',ms=mars,ls=lines)
elif pressures[3][-1]==1e15:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Not found',color=col[3],marker='.',ms=mars,ls=lines)
elif pressures[3][-1]==1e16:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' - Identification error',color=col[3],marker='.',ms=mars,ls=lines)
else:
    plot3,=ax.plot_date(times,pressures[3],label=labels[4]+' %.2e mbar'%pressures[3][-1],color=col[3],marker='.',ms=mars,ls=lines)

if pressures[4][-1]==1e11:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Underranged',color=col[4],marker='.',ms=mars,ls=lines)
elif pressures[4][-1]==1e12:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Overranged',color=col[4],marker='.',ms=mars,ls=lines)
elif pressures[4][-1]==1e13:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Error',color=col[4],marker='.',ms=mars,ls=lines)
elif pressures[4][-1]==1e14:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Off',color=col[4],marker='.',ms=mars,ls=lines)
elif pressures[4][-1]==1e15:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Not found',color=col[4],marker='.',ms=mars,ls=lines)
elif pressures[4][-1]==1e16:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' - Identification error',color=col[4],marker='.',ms=mars,ls=lines)
else:
    plot4,=ax.plot_date(times,pressures[4],label=labels[5]+' %.2e mbar'%pressures[4][-1],color=col[4],marker='.',ms=mars,ls=lines)

if pressures[5][-1]==1e11:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Underranged',color=col[5],marker='.',ms=mars,ls=lines)
elif pressures[5][-1]==1e12:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Overranged',color=col[5],marker='.',ms=mars,ls=lines)
elif pressures[5][-1]==1e13:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Error',color=col[5],marker='.',ms=mars,ls=lines)
elif pressures[5][-1]==1e14:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Off',color=col[5],marker='.',ms=mars,ls=lines)
elif pressures[5][-1]==1e15:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Not found',color=col[5],marker='.',ms=mars,ls=lines)
elif pressures[5][-1]==1e16:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' - Identification error',color=col[5],marker='.',ms=mars,ls=lines)
else:
    plot5,=ax.plot_date(times,pressures[5],label=labels[6]+' %.2e mbar'%pressures[5][-1],color=col[5],marker='.',ms=mars,ls=lines)

lgnd=ax.legend(loc=2)
for i in range(6):
    lgnd.legendHandles[i]._legmarker.set_markersize(5)
    
date_fmt = '%d-%m-%Y\n%H:%M:%S'

ax.set_yscale('log')
ax.set_ylim(1e-12,1e4)
ax.grid(True,which='both',ls='-',color='0.45')
ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
ax.format_xdata = mdate.DateFormatter(date_fmt)
ax.set_ylabel('Pressure [mbar]')
cursor1 = FollowDotCursor(ax, times_str, pressures[0],label='prep',offsets=(-20, 20))
cursor2 = FollowDotCursor(ax, times_str, pressures[1],label='rough',offsets=(-20, -40))
cursor3 = FollowDotCursor(ax, times_str, pressures[2],label='STM',offsets=(-20, -40))
cursor = Cursor(ax, useblit=True, color='#A4A4A4', linewidth=2, horizOn=False)
    
datenow = str(dt.datetime.now().strftime(date_fmt))
plt.savefig('%s.png'%load_data.split('/')[-1],dpi=300)
plt.show()
