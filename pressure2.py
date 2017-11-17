# -*- coding: utf-8 -*-
"""
?!!Describe what program does and what it needs?!!
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
def read_gauges():
    global ser
    ''' Reads all 6 channels and returns status and (if applicable) pressure '''
    '''  There is one list for status[CH] and one for pressure[CH] '''
    ser.flushInput()

    #send_command('ETX\r\n')
    #print(read_port())
    #send_command('\x05\r\n')
    press=[]
    stat=[]
    for j in range(6):
        send_command('PR%i\r\n'%(j+1))  #request Channel 1-6
        send_command('\x05')            #enquire data
        #what the controller returns is something like 'x,x.xxxEsx <CR><LF>'
        #first digit is the error code, seconds one is the pressure
        '''x,x.xxxEsx <CR><LF>
        x[Status],[x.xxxEsx] Measurement value (always exponential format)
        0 Measurement data okay, 1 Underrange, 2 Overrange
        3 Sensor error, 4 Sensor off, 5 No sensor, 6 Identification erro
        '''
        string=read_port().split(',') # splits read string into string[-1],string[0]
        if debug: print(string)
        string_pres=str(string[1])       #pressure value converted to string
        if debug: print('Read pressure :' + string_pres)
        string_sta=int(string[0][-1])    #status value converted to int
        if debug: print('Read status :' + str(string_stat))
        press.append(float(string_pres))    #append float of pressure to press-list
        stat.append(int(string_stat))        #append int(status) to status list
    return(stat,press)
    
def send_command(command):
    global ser 
    '''Takes ascii string 'command' and converts it to bytes and sned it over serial connection '''
    if debug2: print('########################')
    input=command.encode('utf-8')   #encode as utf-8
    if debug2: print('Command string: ' + str(input))
    convinput=to_bytes(input)       #convert to byte sequence
    if debug2: print('byte-input (as str repre): ' + str(convinput.decode('utf-8')))
    if debug2: print('CTS line: ' + str(ser.cts))
    if debug2: print('DSR line: ' + str(ser.dsr))
    ser.write(convinput)            #send to wire
    time.sleep(0.2)
    if debug2: print('########################')
    if debug2: print('Send Command: ' + str(input))
    
def read_port():
    ''' Reads serial port, gets bytes over wire, decodes them with utf-8'''
    ''' and returns string with received message'''
    if debug: print('########################')
    if debug2: print('Am I outWaiting?: ' + str(ser.out_waiting))
    if debug: print('Am I inWaiting?: ' + str(ser.in_waiting))
    if debug: print('Input buffer size: ' + str(ser.in_waiting))
    if debug: print('########################')
    if debug2: print('CTS line: ' + str(ser.cts))
    if debug2: print('DSR line: ' + str(ser.dsr))
    
    out = ''#string to hold the received message, empty one for new reading
    input_buffersize = ser.in_waiting   #input_buffersize: Numbers of bytes received
    if debug:
        if input_buffersize == 0:
            print('No data in input buffer...No data received')
    while input_buffersize > 0:
        '''  '''
        if debug: print('Input buffersize: ' + str(input_buffersize))
        if debug: print('...ser.read ...')
        input_buffersize_old = 0
        time.sleep(0.2)
        out += ser.read(64).decode('utf-8')
        if debug: print('accomplished')
        if input_buffersize == input_buffersize_old:
            break
        else:
            input_buffersize = input_buffersize_old
        
    if debug: print('Received msg: ' + str(out))
    return out

def get_info():
    global ser
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

def init_serial():
    global ser       #create global serial-connector object
    try:
        ser = serial.Serial(port='COM1',timeout=0.5,baudrate=9600,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)    
    except IndexError as err:
        print('Failed opening serial port...Try reloading the Console')
    if debug2: get_info()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

if __name__ == '__main__':
    global ser
    debug = True
    debug2 = False
    init_serial()
    
    pressures=[[],[],[],[],[],[]]
    times=[]
    col=['b','r','g','K','c','y']
    
    labels_begin=[r'STM',r'Rough',r'Prep',r'Sensor 4',r'Sensor 5',r'Sensor 6']
    
    fig=plt.figure(figsize=(10,6),dpi=100)
    ax=fig.add_subplot(111)
    plt.ion()
    plt.yscale('log')
    
    stat,stpre=read_gauges()
    
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
    date_fmt = '%d-%m-%Y %H:%M:%S'
    datenow=dt.datetime.now().strftime(date_fmt)    # get formatted datetime object
    times.append(mdate.datestr2num(datenow))        #and append it to times list
    #write header if logfile was never used ...
    header = 'Time\t\t\t\t\tSTM [mbar]\t\tRough [mbar]\tPrep [mbar]\t\tSensor 4 [mbar]\t\tSensor 5 [mbar]\t\tSensor 6 [mbar]\n'
    if os.path.isfile('pressure-log.txt'):  #... or add seperator if logfile was already used to keep old data
        header = '##########################################################################'
    with open("pressure-log.txt", "a") as logfile:
        logfile.write(header)
        log.write("%s\t\t%.2e\t\t%.2e\t\t%.2e\t\t%.2e\t\t\t%.2e\t\t\t%.2e\n"%(datenow,pressures[0][0],pressures[1][0],pressures[2][0],pressures[3][0],pressures[4][0],pressures[5][0]))
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
        status,pre=read_gauges()
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
        with open("pressure.txt", "a") as logfile:
            logfile.write("%s\t\t%.2e\t\t%.2e\t\t%.2e\t\t%.2e\t\t\t%.2e\t\t\t%.2e\n"%(datenow,pressures[0][-1],pressures[0][-1],pressures[2][-1],pressures[3][-1],pressures[4][-1],pressures[5][-1]))
        
        for j in range(6):
            sens['sen{0}'.format(j)].set_xdata(times)
            sens['sen{0}'.format(j)].set_ydata(pressures[j])
            sens['sen{0}'.format(j)].set_label(labels[j])
        ax.legend()
        ax.set_xlim(times[0]-(times[1]-times[0]),times[-1]+(times[1]-times[0]))
        plt.pause(0.05)
        ser.close()
