# Maxigauge-TPG256A Serial Port Reader
* Reads Pfeiffer Maxigauge TPG256A over serial connection and creates logfile.
* Creates command line output for the six channels with indicated pressures & stati.

## Usage:
* Start pressure recording with python Maxigauge-TPG256A.py 
* Plot logfile with plot-logfiles.py
* Create a united logfile from the logfiles you want to plot with merge-logfiles.py

### Optional but not production yet:
* Real-time plot data in a seperate window with calling maxigauge-TPG256A.py with the -p flag

### record/display:
* prints helpline with command line options and their default values
``` 
python Maxigauge-TDG256A.py -h 
```
* starts program with default parameters (COMport = 8, no plotting) - writes logfile to "%(date) - pressure.log"
``` 
python Maxigauge-TDG256A.py 
```
* starts on COM port 5 [and enables real-time plotting]
``` 
python Maxigauge-TDG256A.py -c 5 [-p] 
```
* starts with loglevel info
``` 
python Maxigauge-TDG256A.py -v info
```

### merge/plot logfiles:
* merge multiplot logfiles into one big file - by default it grabs all files in the current folder ending with *pressure.log into OUTPUT
``` 
python merge-logfiles.py s SINGLELOGFILE 
```
* merge given logfiles into OUTPUT
```
python merge-logfiles.py [LOGFILE LOGFILE ... ] s SINGLELOGFILE 
```
* plots single logfile given as command line argument SINGLELOGFILE
``` 
python plot-logfile.py SINGLELOGFILE 
```

#### tested module versions:
```
serial:   3.2.1
pylab:    1.12.1
numpy:    1.12.1
argparse: 1.1
logging:  0.5.1.2
re:       2.2.1
```
