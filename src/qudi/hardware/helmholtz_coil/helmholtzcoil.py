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

    _address = ConfigOption("address", missing="error")
    _current_min = ConfigOption("current_min", -3)
    _current_max = ConfigOption("current_max", 3)
    _voltage_max = ConfigOption("voltage_max", 3)
    _fieldcoeffs = ConfigOption("field_coeffs")

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
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._address)
        self._write("SYST:REM")
        self._query("*IDN?")
        self._write("*RST;*CLS")
        time.sleep(1)
        
        self._write('APP:VOLT 3.000000,3.000000,3.000000')
        self._write("APP:CURR 0.000000,0.000000,0.000000")
        self._write("OUTP:STAT:ALL ON")
        self.magnet_state = MagnetState.ON
    def on_deactivate(self):
        self._write("OUTP:STAT:ALL OFF")
        if self._query("OUTP:STAT:ALL?")== '0\n':
            print("Keithley outputs disabled")
        else: print("Error, Keithley outputs may not be disabled")
        self.magnet_state = MagnetState.OFF
    

    def _write(self, command):
        self._inst.write(command)
        time.sleep(0.01)

    def _query(self, command):
        self._inst.query(command)

    def activatemagnet(self):
        self._write("OUTP:STAT:ALL ON")

    def querychannel(self, channel, type):
        self._write("INST:NSEL " + str(channel))
        dat = {}
        if type == "ALL":
            dat['channel'] = self._query("INST?")
            dat['CURR'] = self._query("MEAS:CURR?")
            dat['VOLT'] = self._query("MEAS:VOLT?")
        else: 
            dat['channel'] = self._query("INST?")
            dat[type] = self._query("MEAS:" + type + "?")
        return dat
        
    def set_magnet_state(self, state):
        self.magnet_state = state
    
    def get_magnet_state(self):
        return self.magnet_state
