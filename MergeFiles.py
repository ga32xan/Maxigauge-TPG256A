import numpy as np
import matplotlib.pylab as plt
import sys
import matplotlib.dates as mdate
import datetime as dt
import glob

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
        if i==0:
            labels=parse_labels(lines[i])
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
    return (date,time,[STM,ROUGH,PREP,SEN4,SEN5,SEN6],labels)

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

if len(sys.argv)==1:
    print('\nThis program can merge pressure log files.\nFor merging and saving multiple pressure log-files:\n  MergeFiles.py "filename1" "filename2" .. "filenameN" s "savetitle.log"\n')
elif sys.argv[-2]=='s':
    if len(sys.argv)==3:
        files=glob.glob('*pressure.log')
    else:
        files=sys.argv[1:-2]
    files.sort()
    save=sys.argv[-1]
    for o,k in enumerate(files):
        d,t,p,labels=laden(k)
        if o==0:
            with open(save,'a') as logfile:
                logfile.write('%s\t\t\t\t%s [mbar]\t\t%s [mbar]\t\t%s [mbar]\t\t%s [mbar]\t\t\t%s [mbar]\t\t\t%s [mbar]\n'%(labels[0],labels[1],labels[2],labels[3],labels[4],labels[5],labels[6]))
        for f in range(len(d)):
            with open(save,'a') as logfile:
                logfile.write("%s %s\t\t%.2e\t\t%.2e\t\t%.2e\t\t%.2e\t\t\t%.2e\t\t\t%.2e\n"%(d[f],t[f],p[0][f],p[1][f],p[2][f],p[3][f],p[4][f],p[5][f]))
	
