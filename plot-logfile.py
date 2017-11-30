import numpy as np
import matplotlib.pylab as plt
import matplotlib.dates as mdate
import datetime as dt

def laden(data):
    A=open(data,'r')
    lines=A.readlines()
    num_lines=len(lines)
    date=[]
    time=[]
    STM=[]
    ROUGH=[]
    PREP=[]
    SEN4=[]
    SEN5=[]
    SEN6=[]
    for i in range(0,num_lines):
        if i!=0 and lines[i][0]!='#':
            date.append(str(lines[i].split()[0]))
            time.append(str(lines[i].split()[1]))
            STM.append(float(lines[i].split()[2]))
            ROUGH.append(float(lines[i].split()[3]))
            PREP.append(float(lines[i].split()[4]))
            SEN4.append(float(lines[i].split()[5]))
            SEN5.append(float(lines[i].split()[6]))
            SEN6.append(float(lines[i].split()[7]))
    A.close()
    return (date,time,STM,ROUGH,PREP,SEN4,SEN5,SEN6)

d,t,stm,rough,prep,sen4,sen5,sen6=laden('pressure-log.txt')
date_fmt = '%d-%m-%Y %H:%M:%S'

times=[]
for i in zip(d,t):
    times.append(mdate.datestr2num(str(i[0]+' '+str(i[1]))))

col=['b','r','g','k','c','y']

labels=[r'STM',r'Rough',r'Prep',r'Sensor 4',r'Sensor 5',r'Sensor 6']

lines=''
mars=2

plt.figure(figsize=(10,6),dpi=100,tight_layout=True)
plt.plot(times,stm,label=labels[0],color=col[0],marker='.',ms=mars,ls=lines)
plt.plot(times,rough,label=labels[1],color=col[1],marker='.',ms=mars,ls=lines)
plt.plot(times,prep,label=labels[2],color=col[2],marker='.',ms=mars,ls=lines)
plt.plot(times,sen4,label=labels[3],color=col[3],marker='.',ms=mars,ls=lines)
plt.plot(times,sen5,label=labels[4],color=col[4],marker='.',ms=mars,ls=lines)
plt.plot(times,sen6,label=labels[5],color=col[5],marker='.',ms=mars,ls=lines)
plt.gca().xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
plt.gcf().autofmt_xdate()
plt.yscale('log')
plt.ylim(1e-12,1e2)
plt.grid()
plt.ylabel('Pressure [mbar]')
lgnd=plt.legend()
for i in range(6):
    lgnd.legendHandles[i]._legmarker.set_markersize(5)
datenow = str(dt.datetime.now().strftime(date_fmt))
plt.savefig('pressure - %s.png'%datenow.replace(':','-'))
plt.show()
