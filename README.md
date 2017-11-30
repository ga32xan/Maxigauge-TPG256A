# Maxigauge-TPG256A Serial Port Reader
* Reads Pfeiffer Maxigauge TPG256A over serial connection and creates logfile
* Creates command line output for the six channels wit indicated pressure

## Changed usage:
* Start pressure recording with Pressure-reading.py
* Create a united logfile from the logfiles you want to plot
* Plot logfile with Plot-pressure.py

### Optional but not production:
* Real-time plot data in a seperate window
* Dynamically update pressure gauges for their reported status

#### Command line usage:
```
python read_pressure.py -h #plots helpline with command line options and their default value
```
