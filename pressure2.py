# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 12:59:26 2017

@author: The greatest hexxor tha world!
"""
import time
import serial
import matplotlib.pylab as plt
import datetime as dt
import matplotlib.dates as mdate
import numpy as np

def to_bytes(seq):
    """convert a sequence to a bytes type"""
    if isinstance(seq, bytes):
        return seq
    elif isinstance(seq, bytearray):
        return bytes(seq)
    elif isinstance(seq, memoryview):
        return seq.tobytes()
    else:
        b = bytearray()
        for item in seq:
            b.append(item)  # this one handles int and str for our emulation and ints for Python 3.x
        return bytes(b)
'''
def bytetoarray(byte):
    array = []
    for i in range(len(byte)):
        array+=byte[i]
    return array
'''

# configure the serial connections (the parameters differs on the device you are connecting to)
def main():
    #ser.read()
    #pressure=[]
    ser.flushInput()
    
    #send_command('ETX\r\n')
    #print(read_port())
    #send_command('\x05\r\n')
    press=[]
    stat=[]
    for j in range(6):
        send_command('PR%i\r\n'%(j+1))
        send_command('\x05')
        string=read_port().split(',')
        string_pres=str(string[1])
        string_sta=int(string[0][-1])
        press.append(float(string_pres))
        stat.append(int(string_sta))
    return(stat,press)
    
def send_command(command):
    if debug: print('########################')
    input=command.encode('utf-8')
    if debug: print('Command string: ' + str(input))
    convinput=to_bytes(input)
    if debug: print('byte-input (as str repre): ' + str(convinput.decode('utf-8')))
    if debug: print('CTS line: ' + str(ser.cts))
    if debug: print('DSR line: ' + str(ser.dsr))
    ser.write(convinput)
    time.sleep(0.2)
    if debug: print('########################')
    if debug: print('Send Command: ' + str(input))
    
def read_port():
    
    if debug: print('########################')
    if debug: print('Am I outWaiting?: ' + str(ser.out_waiting))
    if debug: print('Am I inWaiting?: ' + str(ser.in_waiting))
    if debug: print('########################')
    if debug: print('...ser.read ...')
    if debug: print('CTS line: ' + str(ser.cts))
    if debug: print('DSR line: ' + str(ser.dsr))
    
    out = ''
    input_buffersize = ser.in_waiting
    while input_buffersize > 0:
        input_buffersize_old = 0
        time.sleep(0.2)
        if debug: print('Input buffersize: ' + str(input_buffersize))
        out += ser.read(64).decode('utf-8')
        if debug: print('accomplished')
        if input_buffersize == input_buffersize_old:
            break
        else:
            input_buffersize = input_buffersize_old
        
    if debug: print('Received msg: ' + str(out))
    return out

def get_info():
    print('############ Information about connection: ############')
    print('Name of device: ' + ser.name)
    print('@ port : ' + ser.port)
    print('Port is open?: ' + str(ser.is_open))
    print('state of ...')
    print('   ... CTS line: ' + str(ser.cts))
    print('   ... DSR line: ' + str(ser.dsr))
    print('   ...  RI line: ' + str(ser.ri))
    print('   ...  CD line: ' + str(ser.cd))

    print('############ Can set values to: ######################')
    print('port: ' + ser.port)
    print('baudrate: ' + str(ser.baudrate))
    print('bitesyze: ' + str(ser.bytesize))
    print('parity: ' + str(ser.parity))
    print('stopbits: ' + str(ser.stopbits))
    print('read_timeout: ' + str(ser.timeout))
    print('write_timeout: ' + str(ser.write_timeout))
    print('inter byte timeout: ' + str(ser.inter_byte_timeout))
    print('software flow control setting: ' + str(ser.xonxoff))
    print('hardware flow control setting of ... ')
    print('\t \t \t \t... CTS line: ' + str(ser.rtscts))
    print('\t \t \t \t... DSR line: ' + str(ser.dsrdtr))
    print('RS485 settings: ' +  str(ser.rs485_mode))

if __name__ == '__main__':
	ser = serial.Serial(port='/dev/ttyUSB0',timeout=0.5,baudrate=9600,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)    
	debug = 0
	ser.reset_input_buffer()
	ser.reset_output_buffer()
	pressures=[[],[],[],[],[],[]]
	times=[]
	col=['b','r','g','K','c','y']
	
	labels_begin=[r'STM',r'Rough',r'Prep',r'Sensor 4',r'Sensor 5',r'Sensor 6']
	
	fig=plt.figure(figsize=(10,6),dpi=100)
	ax=fig.add_subplot(111)
	date_fmt = '%d-%m-%Y %H:%M:%S'
	plt.ion()
	plt.yscale('log')
	
	stat,stpre=main()
	
	labels=['','','','','','']
	
	for num,sensor in enumerate(stat):
		if sensor==0:
			pressures[num].append(stpre[num])
			if pressures[num][-1]>1e-1:
				labels[num]=labels_begin[num]+r' $\rightarrow$'
			elif pressures[num][-1]<1e-1:
				labels[num]=labels_begin[num]+r' $\leftarrow$'
		elif sensor==1:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Underrange'
		elif sensor==2:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Overrange'
		elif sensor==3:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Error'
		elif sensor==4:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Off'
		elif sensor==5:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Not found'
		elif sensor==6:
			pressures[num].append(0)
			labels[num]=labels_begin[num]+' - Identification error'
	datenow=dt.datetime.now().strftime(date_fmt)
	times.append(mdate.datestr2num(datenow))
	header = 'Time\t\t\t\t\tSTM [mbar]\t\tRough [mbar]\tPrep [mbar]\t\tSensor 4 [mbar]\t\tSensor 5 [mbar]\t\tSensor 6 [mbar]\n'
	if os.path.isfile('pressure-log.txt'):
		header = '##########################################################################'
	with open("pressure-log.txt", "a") as myfile:
		myfile.write(header)
		myfile.write("%s\t\t%.2e\t\t%.2e\t\t%.2e\t\t%.2e\t\t\t%.2e\t\t\t%.2e\n"%(datenow,pressures[0][0],pressures[1][0],pressures[2][0],pressures[3][0],pressures[4][0],pressures[5][0]))
	sens={}
	for j in range(6):
		sens['sen{0}'.format(j)],=ax.plot(times,pressures[j],'o',ls='-',color=col[j],label=labels[j])
	ax.set_ylim(1e-12,1e-4)
	ax.set_xlabel('Time')
	ax.set_ylabel('Pressure [mbar]')
	
	ax.legend()
	plt.gca().xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
	plt.gcf().autofmt_xdate()
	
	ax2 = ax.twinx()
	for j in range(6):
		if pressures[j][-1]>1e-1:
			sens['sen{0}'.format(j)],=ax2.plot(times,pressures[j],'o',ls='-',color=col[j],label=labels[j])
	ax2.set_ylim(1e-1,1e3)
	ax2.set_yscale('log')
	ax2.set_ylabel('Pressure [mbar]')
	
	while True:
		ser.open()
		status,pre=main()
		datenow=dt.datetime.now().strftime(date_fmt)
		times.append(mdate.datestr2num(datenow))
		ax.legend_.remove()
		for num,sensor in enumerate(status):
			if sensor==0:
				pressures[num].append(pre[num])
				if pressures[num][-1]>1e-1:
					labels[num]=labels_begin[num]+r' $\rightarrow$'
				elif pressures[num][-1]<1e-1:
					labels[num]=labels_begin[num]+r' $\leftarrow$'
			elif sensor==1:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Underrange'
			elif sensor==2:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Overrange'
			elif sensor==3:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Error'
			elif sensor==4:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Off'
			elif sensor==5:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Not found'
			elif sensor==6:
				pressures[num].append(0)
				labels[num]=labels_begin[num]+' - Identification error'
		with open("pressure.txt", "a") as myfile:
			myfile.write("%s\t\t%.2e\t\t%.2e\t\t%.2e\t\t%.2e\t\t\t%.2e\t\t\t%.2e\n"%(datenow,pressures[0][-1],pressures[0][-1],pressures[2][-1],pressures[3][-1],pressures[4][-1],pressures[5][-1]))
		
		for j in range(6):
			sens['sen{0}'.format(j)].set_xdata(times)
			sens['sen{0}'.format(j)].set_ydata(pressures[j])
			sens['sen{0}'.format(j)].set_label(labels[j])
		ax.legend()
		ax.set_xlim(times[0]-(times[1]-times[0]),times[-1]+(times[1]-times[0]))
		plt.pause(0.05)
		ser.close()