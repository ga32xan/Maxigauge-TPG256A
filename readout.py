# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 15:08:19 2017

@author: ltstm
"""
import serial
import matplotlib.pylab as plt
import numpy as np
import datetime as dt
import matplotlib.dates as md
import time

class color:
    HEADER 		= '\033[95m'
    OKBLUE 		= '\033[94m'
    WARNING 		= '\033[93m'
    OKGREEN 		= '\033[92m'
    FAIL 		= '\033[91m'
    ENDC 		= '\033[0m'
    BOLD 		= '\033[1m'
    UNDERLINE 		= '\033[4m'

class pressure_gauge():
    '''defines a class pressure gauges that take a name, channel and pressure value-array'''
    def __init__(self,name='not-set',channel=-1):
        '''self-initialization, nonsense voalues of not initialized properly'''
        self.__name=name
        self.__channel=channel
        self.__pressure=[[]]
    
    def set_name(self,name):
        self.__name=name
    def get_name(self):
        return self.__name
    
    def set_channel(self,channel):
        self.__channel=channel
    def get_channel(self):
        return self.__channel
    
    def append_pressure(self,pressure):
        '''appends [timestamp,pressure] tuple if called with self.pressure=float'''
        now = time.mktime(time.localtime())
        self.__pressure += [now,pressure]
    def get_pressure(self):
        '''returns full array of [time,pressure] values'''
        return self.__pressure
    
    name = property(get_name,set_name)
    channel = property(get_channel,set_channel)
    pressure = property(get_pressure,append_pressure)
    
def to_bytes(seq):
    '''convert a sequence to a bytes type'''
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

# configure the serial connections (the parameters differs on the device you are connecting to)
def get_pressures():
    #create pressure gauge objects
    global STM, ROUGH, PREP
    STM = pressure_gauge('STM',1)
    ROUGH = pressure_gauge('ROUGH',2)
    PREP = pressure_gauge('PREP',2)
    
    send_command('PR1\r\n') # Trigger readeout of CH1
    send_command('\x05')    # Enquery data
    STM.pressure=float(str(read_port().split(',')[1]))#Strip unwanted parts
    ''' Need ERROR handling! '''
    send_command('PR2\r\n')
    send_command('\x05\r\n')
    ROUGH.pressure=float(str(read_port().split(',')[1]))
    send_command('PR3\r\n')
    send_command('\x05\r\n')
    PREP.pressure=float(str(read_port().split(',')[1]))
    #ts = ti.time()
    #tida = dt.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    if debug: print('Pressures are - ' + 'Prep: ' + str(Prep.pressure) + 'STM: ' + str(STM.pressure) + 'ROUGH: ' + str(ROUGH.pressure))
    if debug2: print('Types of returned pressures: ' + str(type(Prep.pressure)))
    return([PREP.pressure,STM.pressure,ROUGH.pressure])
    
    
def send_command(command):
    global ser
    if debug2: print('########################')
    input=command.encode('utf-8')
    if debug2: print('Command string: ' + str(input))
    convinput=to_bytes(input)
    if debug2: print('byte-input (as str repre): ' + str(convinput.decode('utf-8')))
    #if debug2: print('CTS line: ' + str(ser.cts))
    #if debug2: print('DSR line: ' + str(ser.dsr))
    ser.write(convinput)
    time.sleep(0.2)
    if debug:print('########################')
    if debug:print('Send Command: ' + str(input))
    
def read_port(retry=3,retry_delay=0.5,wait=0.1):
    global ser
    if debug2: print('########################')
    if debug2: print('Am I outWaiting?: ' + str(ser.out_waiting))
    if debug2: print('Am I inWaiting?: ' + str(ser.in_waiting))
    if debug2: print('########################')
    if debug2: print('...ser.read ...')
    #if debug2: print('CTS line: ' + str(ser.cts))
    #if debug2: print('DSR line: ' + str(ser.dsr))
    
    out = ''
    input_buffersize = ser.in_waiting
    while input_buffersize > 0:
        input_buffersize_old = 0
        time.sleep(wait)
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

def initialize():
    global ser
    try:
        ser = serial.Serial(port='COM6',timeout=1,baudrate=9600,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)    
    #clear all old buffer in case come trash is in them
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.flushInput()
        if debug: print('...Initialized...')
    except:
        print('Initialization failed')
        
    #print full configuration of comport into console
    show_info=input("Show configuration? If so type y or Y")
    if show_info == 'y':
        get_info()
    if show_info == 'Y':
        get_info()

if __name__ == '__main__':
    '''not executed when this files is imported from another python file!! '''
    global ser
    debug = True
    debug2 = True
    try:
        initialize()
    except:
        print('COM connection NOT opened')
    
    try:    
        if debug2: print(color.HEADER + '...Updating pressures...' + color.ENDC)
        get_pressures() # update values of pressure gauges
        if debug2: print('...Plotting...')
        plt.ion()
        fig,ax=plt.subplots()
        labels=[Prep.name,STM.name,ROUGH.name]
        col=['g','b','r']
        prep=ax.plot(times, pressures[0] ,label=labels[0],color=col[0])
        ax.set_yscale('log')
        ax.set_xlim(min(times))
        plt.legend()
        fig.canvas.draw()
    except:    
        print('Could not draw all the stuff')
        ser.close()
