# Maxigauge-TPG256A Serial Port Reader
* Reads Pfeiffer Maxigauge TPG256A over serial connection and creates logfile
* Creates command line output for the six channels wit indicated pressure

## Changed usage:
* Start pressure recording with maxigauge-TPG256A.py 
* Create a united logfile from the logfiles you want to plot with merge-logfiles.py
* Plot logfile with plot-logfiles.py

### Optional but not production:
* Real-time plot data in a seperate window with calling maxigauge-TPG256A.py with the -p flag
* Dynamically update pressure gauges for their reported status on the command line

#### (record/display):
* prints helpline with command line options and their default values
``` 
python read_pressure.py -h 
```
* starts program with default parameters (COMport = 8, no plotting) - writes logfile to %(date) - pressure.log
``` 
python Maxigauge-TDG256A.py 
```
* starts logfile-writing on COM port 5 and enables real-time plotting 
``` 
python Maxigauge-TDG256A.py -c 5 [-p] 
```
* plots single logfile given as command line argument LOGFILE
``` 
python plot-logfile.py LOGFILE 
```

#### (merge/plot logfiles)
* merge multiplot logfiles into one big file - by default it grabs all files in the current folder ending with *pressure.log into OUTPUT
``` 
python merge-logfiles.py s OUTPUT 
```
* merge given logfiles into OUTPUT
```
python merge-logfiles.py [LOGFILE LOGFILE ... ] s OUTPUT 
```
