import serial
import time
import sys
import math as np
import pyvisa as visa
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState, HelmholtzCoilRelayInterface

rm = visa.ResourceManager()

class HelmholtzCoil(HelmholtzCoilInterface):
# 
    # _address = ConfigOption("address", missing="error")
    _address = ''
    _current_min = ConfigOption("current_min", -3)
    _current_max = ConfigOption("current_max", 3)
    _voltage_max = ConfigOption("voltage_max", 3)
    # _fieldcoeffs = ConfigOption("field_coeffs")
    _fieldcoeffs = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bnorm_setpoint = 0
        self.theta_setpoint = 0
        self.phi_setpoint = 0
        self.bnorm_read = 0
        self.theta_read = 0
        self.phi_read = 0
        self.xcurrent_read = 0
        self.ycurrent_read = 0
        self.zcurrent_read = 0


    def on_activate(self):
        # rm = visa.ResourceManager()
        # self._inst = rm.open_resource(self._address)
        self._write("SYST:REM")
        self._query("*IDN?")
        self._write("*RST;*CLS")
        time.sleep(1)
        
        self._write('APP:VOLT 3.000000,3.000000,3.000000')
        self._write("APP:CURR 0.000000,0.000000,0.000000")
        self._write("OUTP:STAT:ALL ON")
        self.magnet_state = MagnetState.ON
        MagnetState(1)
    def on_deactivate(self):
        self._write("OUTP:STAT:ALL OFF")
        if self._query("OUTP:STAT:ALL?")== '0\n':
            print("Keithley outputs disabled")
        else: print("Error, Keithley outputs may not be disabled")
        self.magnet_state = MagnetState.OFF
        MagnetState(0)
    

    def _write(self, command):
        print("write: ", command)
        time.sleep(0.01)

    def _query(self, command):
        print("query: ", command)

    def querychannel(self, channel):
        "Returns a dictionary, dat, with the channel number, current set, and voltage set off the current source"
        self._write("INST:NSEL " + str(channel))
        dat = {}
        dat['channel'] = self._query("INST?")
        dat['current'] = self._query("MEAS:CURR?")
        dat['voltage'] = self._query("MEAS:VOLT?")
        return dat

    def query3channels(self):
        "Returns a dictionary of the current and voltage set on all three x,y,z channels off the current source"
        dat = {}
        dat["X"] = self.querychannel(1)
        dat["Y"] = self.querychannel(2)
        dat["Z"] = self.querychannel(3)
        return dat

    def write3channels(self, TYPE, x, y, z):
        "Writes the TYPE (CURR or VOLT) to all three channels x, y, z on the current source"
        s = "APP:" + TYPE + " " + str(abs(x)) + ","+str(abs(y))+"," + str(abs(z))
        self._write(s)
        return s

    def fieldtocurrent(self, B, phi, theta):
        "Converts the Bnorm, phi, and theta input values into x, y, z, current values using calibration parameters in fieldcoeffs"
        x, errx = self.calibbfieldtocurr(self._fieldcoeffs['X'], B * np.sin(theta)* np.cos(phi))
        y, erry = self.calibbfieldtocurr(self._fieldcoeffs['Y'], B * np.sin(theta) * np.sin(phi))
        z, errz = self.calibbfieldtocurr(self._fieldcoeffs['Z'], B * np.cos(theta))
        if errx==erry==errz==None: return x,y,z, None
        else: return x,y,z, [errx, erry, errz]

    def calibbfieldtocurr(self, fieldcoeffs, x):
        "Calibrates the field to current conversion using parameters in fieldcoeffs"
        y = (x - fieldcoeffs[1])/fieldcoeffs[0]
        if self._current_min<=y<=self._current_max:
            return y, None
        elif y>self._current_max: return self._current_max, "Current clipped to " + str(self._current_max) + "A"
        elif y<self._current_min: return self._current_min, "Current clipped to " + str(self._current_min) + "A"

    def setpolarity(self, x,y,z):
        "Determines the 3-bit polarity string to send to the Arduino Relay. 0 for positive polarity, 1 for negative polarity"
        pols = []
        if abs(x) == x: pols.append(0)
        else: pols.append(1)

        if abs(y) == y: pols.append(0)
        else: pols.append(1)

        if abs(z) == z: pols.append(0)
        else: pols.append(1)
        pols = "".join(str(pol) for pol in pols)
        HelmholtzCoilRelay.setbfieldpol(pols)
        output, d = HelmholtzCoilRelay.getbfieldpol()

        return d, pols


    def currenttofield(self, x1, y1, z1):
        "Converts the x,y,z current input values into bnorm, phi, and theta values using calibration parameters in fieldcoeffs"

        x = self.calibcurrtobfield(self._fieldcoeffs["X"], x1)
        y = self.calibcurrtobfield(self._fieldcoeffs["Y"], y1)
        z = self.calibcurrtobfield(self._fieldcoeffs["Z"], z1)

        bnorm = np.sqrt(x**2 + y**2 + z**2)
        phi = np.atan(y/x)
        theta = np.acos(z/bnorm)
        return bnorm, phi, theta

    def calibcurrtobfield(fieldcoeffs, x):
        "Calibrates the current to field conversion using parameters in fieldcoeffs"
        return (x * fieldcoeffs[0]) + fieldcoeffs[1]


    def setfield(self, bnorm, phi, theta):
        if self.magnet_state != MagnetState.ON:
            self._write("OUTP:STAT:ALL ON")
        if MagnetState == 3:
            print("Error with magnet state!")

        x,y,z, errs = self.fieldtocurrent(bnorm, phi, theta) ## Step 1 Convert input B field values to current values
        print("Any clipped currents? ", errs)

        d,pols = self.setpolarity(x,y,z) ##Step 2 set the Arduino relay polarities
        print("String sent to Arduino relay and string read from Arduino: ", d, pols) ###d and pols should be the same (pols is what you're trying to set, d is what is read out)


        s = self.write3channels("CURR", x,y,z) ##Step 3 sets the current (using absolute values since this is setting to the Keithley and the Arduino will deal with the polarities)
        print("String sent to kethiley: ", s)
        dat = self.query3channels()
        print("Final readings from Keithley: ", dat)

        currents, field = self.getfield()
        return currents, field

    def getfield(self):
        dat = self.query3channels()
        self.xcurrent_read = float(dat["X"]["current"])
        self.ycurrent_read = float(dat["Y"]["current"])
        self.zcurrent_read = float(dat["Z"]["current"])
        self.bnorm_read, self.phi_read, self.theta_read = self.currenttofield(self.xcurrent_read, self.ycurrent_read, self.zcurrent_read) ##Convert read values to field values

        return [self.xcurrent_read, self.ycurrent_read, self.zcurrent_read],  [self.bnorm_read, self.phi_read, self.theta_read]

    def set_magnet_state(self, state):
        self.magnet_state = state
        print(state)
    
    def get_magnet_state(self):
        print(self.magnet_state)
        return self.magnet_state

class HelmholtzCoilRelay(HelmholtzCoilRelayInterface):
    _relayaddress = ConfigOption("relay_address", missing="error")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self):
        # self.relay = serial.Serial(port=self._relayaddress, baudrate=9600, timeout=3) 
        self._flush()

    def on_deactivate(self):
        print("relay close")

    def _readline(self):
        print("relay readline")

    def _write(self, command):
        print("relay write: ", command)
    
    def _flush(self):
        print("relay flush")
    
    def _sendBreak(self):
        print("relay break")

    def setbfieldpol(self, pols): ####neg = 1, pos = 0
        "Writes the polarity to the Arduino relay. Must be a 3-bit string made of 0s and 1s"
        settings = "set " + pols + '\n'
        self._write(settings)
        time.sleep(.1)
        d = self._readline()
        self._flush()
        self._sendBreak()
        self._flush()
        return d

    def getbfieldpol(self):
        "Reads the field polarities from the Arduino relay"
        settings = 'get \n'
        self._write(settings)
        time.sleep(.1)
        output = {}
        d1 = self._readline()
        d = int(d1)
        op1 = np.floor(d/100)
        if op1 == 0: output['op1'] = 'out'
        else: output['op1'] = 'in'
        op2 = np.remainder(d, 100)
        if np.floor(op2) == 0: output['op2'] = 'out'
        else: output['op2'] = 'in'
        op3 = np.remainder(d,10)
        if np.floor(op3) == 0: output['op3'] = 'out'
        else: output['op3'] = 'in'
        self._flush()
        self._sendBreak()
        self._flush()    