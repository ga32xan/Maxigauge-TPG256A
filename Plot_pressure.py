import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pylab as plt
import matplotlib.dates as mdate
import datetime as dt
from matplotlib.widgets import RadioButtons
import re
import sys

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
            date.append(str(lines[i].split()[0]))
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
 
load_data=sys.argv[1]
date,time,pressures,labels=laden(load_data)
date_fmt = '%d-%m-%Y %H:%M:%S'

times=[]    #should be list NOT list of lists
max_times=0
max_times_str=''
for i,j in zip(date,time):
    times.append(mdate.datestr2num(str(i)+' '+str(j))) #looks like [date time
    if times[-1]>max_times:
        max_times=times[-1]
        max_times_str=i+' '+j

col=['b','r','g','k','c','y']

''' Parse labels from file !!! '''
lines=''
mars=2

fig,ax=plt.subplots(figsize=(10,6),dpi=100)
plt.xticks(rotation=45)
plt.subplots_adjust(left=0.2,bottom=0.25)
axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.05, 0.7, 0.10, 0.2], facecolor=axcolor)
radio = RadioButtons(rax, ('all', '12h', '3h', '1h','30min'))

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
for k in range(6):
    ax.plot(times,pressures[k],label=labels[k+1]+' %.2e mbar'%pressures[k][-1],color=col[k],marker='.',ms=mars,ls=lines)
''' plots vertical lines when label is changed '''
"""for i in range(len(events)):
    ax.plot([events[i],events[i]], [1e-12,1e2], 'k', lw = 1)
    ax.text(events[i],1e1,'Label changed')""" 

ax.set_yscale('log')
ax.set_ylim(1e-12,1e2)
ax.grid(True,which='both',ls='-',color='0.45')
ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
ax.format_xdata = mdate.DateFormatter(date_fmt)
fig.autofmt_xdate()

ax.set_ylabel('Pressure [mbar]')
lgnd=ax.legend(loc=3)
for i in range(6):
    lgnd.legendHandles[i]._legmarker.set_markersize(5)
datenow = str(dt.datetime.now().strftime(date_fmt))
plt.savefig('pressure - %s.png'%datenow.replace(':','-'))
plt.show()
