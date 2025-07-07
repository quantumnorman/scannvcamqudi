# import serial
import time
import sys
import math as np
# import pyvisa as visa
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.core.connector import Connector
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState
# rm = visa.ResourceManager()

class HelmholtzCoil(HelmholtzCoilInterface):
# 
    # _address = ConfigOption("address", missing="error")
    _address = ''

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
        # self.magnet_state = None
        


    def on_activate(self):
        # rm = visa.ResourceManager()
        # self._inst = rm.open_resource(self._address)
        # self._write("SYST:REM")
        # self._query("*IDN?")
        # self._write("*RST;*CLS")
        # time.sleep(1)
        
        # self._write('APP:VOLT 3.000000,3.000000,3.000000')
        # self._write("APP:CURR 0.000000,0.000000,0.000000")
        # self._write("OUTP:STAT:ALL ON")
        self.set_magnet_state(MagnetState.ON)
        # print("coil activated")

        return

    def on_deactivate(self):
        self._write("OUTP:STAT:ALL OFF")
        if self._query("OUTP:STAT:ALL?")== '0\n':
            print("Keithley outputs disabled")
        else: print("Error, Keithley outputs may not be disabled")
        self.set_magnet_state(MagnetState.OFF)
    

    def _write(self, command):
        print("write: ", command)
        time.sleep(0.01)

    def _query(self, command):
        print("query: ", command)
        return 1.51

    def activatemagnet(self):
        self._write("OUTP:STAT:ALL ON")


    def write3channels(self, TYPE, x, y, z):
        "Writes the TYPE (CURR or VOLT) to all three channels x, y, z on the current source"
        s = "APP:" + TYPE + " " + str(abs(x)) + ","+str(abs(y))+"," + str(abs(z))
        self._write(s)
        return s

    def querychannel(self, channel, type):
        self._write("INST:NSEL " + str(channel))
        dat = {}
        print('fake data channel')
        if type == "ALL":
            dat['channel'] = self._query("INST?")
            dat['CURR'] = self._query("MEAS:CURR?")
            dat['VOLT'] = self._query("MEAS:VOLT?")
        
        else: 
            dat['channel'] = self._query("INST?")
            # dat[type] = self._query("MEAS:" + type + "?")
            dat[type] = 1.34
        return dat
    
    def query3channels(self, type):
        dat = {}
        print("making up fake data")
        dat["X"] = self.querychannel(1, type)
        dat["Y"] = self.querychannel(2, type)
        dat["Z"] = self.querychannel(3, type)
        return dat



    def set_magnet_state(self, state):
        self.magnet_state = state
        print("magnet state set to: ", state)
    

    def get_magnet_state(self):
        # print("magnet state got: ", self.magnet_state)
        return self.magnet_state