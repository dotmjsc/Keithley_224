# Python drivers for the Keithley 224 current source
You will need these additional packages:
* pyvisa
* enum

Usage example:
```python
import numpy
import time

instrument = KEITHLEY_224("GPIB0::0::INSTR")

meas = instrument.get_measurement()
print('Raw data: ' + str(meas.raw))
print('Current: ' + str(meas.current))
print('Overcompliance: ' + str(meas.overcompliance))
print('Voltage: ' + str(meas.voltage))
print('Time: ' + str(meas.time))

instrument.operate = True
instrument.voltage = 15
instrument.time = 0.1

for i in numpy.arange(0.001,0.015,0.001):
    instrument.current = i
    time.sleep(0.1)

del instrument
