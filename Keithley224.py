'''
KEITHLEY 224 instrument driver
TODO: SRQ decoding
'''
import pyvisa
import enum

class Readout_Values:
    def __init__(self):
        self.raw = ""
        self.current = 0.0
        self.overcompliance = False
        self.voltage = 0.0
        self.time = 0.0

# Range Commands
RANGE_LIST = (
    'R0',
    'R5',
    'R6',
    'R7',
    'R8',
    'R9',
    )

def get_available_devices():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()
    rm.close()
    return devices

def _decode_values(rawdata):
    splitted = rawdata.split(',')
    readout = Readout_Values()
    readout.raw = rawdata
    for element in splitted:
        if 'DCI' in element:
            if element[0] is 'O':
                readout.overcompliance = True
            readout.current = float(element[4:])
        if 'V' in element:
            readout.voltage = float(element[1:])
        if 'W' in element:
            readout.time = float(element[1:])
    return readout

def _format_e(n):
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

class KEITHLEY_224(object):

    class Ranges(enum.Enum):
        AUTO = 0
        MAN_20uA = 1
        MAN_200uA = 2
        MAN_2mA = 3
        MAN_20mA = 4
        MAN_1m01A = 5

    def __init__(self, address):
        self._address = address
        self._rm = pyvisa.ResourceManager()
        self._inst = self._rm.open_resource(address)
        self._range = self.Ranges.AUTO
        self.voltage = 3.0
        self.current = float(1e-06)
        self.time = 0.05
        self.operate = False

    def __del__(self):
        self.operate = False
        self._rm.close()

    def get_measurement(self):
        self._inst.timeout = 1000
        result = _decode_values(self._inst.read())
        return result

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, range):
        if not isinstance(range, self.Ranges):
            raise TypeError('mode must be an instance of Ranges Enum')
        self._range = range
        self._inst.write(RANGE_LIST[self._range.value]+'X')

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        if (voltage < 1) or (voltage > 105):
            raise ValueError('voltage limits: 1 to 105')
        self._voltage = voltage
        self._inst.write('V'+ _format_e(voltage)+'X')

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, current):
        if (current < -0.101) or (current > 0.101):
            raise ValueError('current limits: +/- 0.101')
        self._current = current
        self._inst.write('I' + _format_e(current) + 'X')

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        if (time < 0.05) or (time > 0.9999):
            raise ValueError('time limits: 0.05 to 0.9999 sec')
        self._time = time
        self._inst.write('W' + _format_e(time) + 'X')

    @property
    def operate(self):
        return self._operate

    @operate.setter
    def operate(self, operate):
        if type(operate) is not type(True):
            raise ValueError('operate takes a bool value')
        self._operate = operate
        if operate is True:
            self._inst.write('F1X')
        else:
            self._inst.write('F0X')


# testing the code
if __name__ == '__main__':
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
