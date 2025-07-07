# import serial
import time
import sys
import math as np
# import pyvisa as visa
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.core.connector import Connector
from qudi.interface.helmholtz_coil_relay_interface import HelmholtzCoilRelayInterface
# rm = visa.ResourceManager()

class HelmholtzCoilRelay(HelmholtzCoilRelayInterface):
    _relayaddress = ConfigOption("relay_address", missing="error")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self):
        # self.relay = serial.Serial(port=self._relayaddress, baudrate=9600, timeout=3) 
        self._flush()
        print("relay activated")    

    def on_deactivate(self):
        return

    def _readline(self):
        print("readline")
        return "101"

    def _write(self, command):
        print("write")
        return
    
    def _flush(self):
        print("flush")
        return
    
    def _sendBreak(self):
        print("break")
        return
    

    def setbfieldrelaypol(self, pols): ####neg = 1, pos = 0
        print(pols)
        print("Writes the polarity to the Arduino relay. Must be a 3-bit string made of 0s and 1s")
        settings = "set " + pols + '\n'
        self._write(settings)
        print("relay settings", settings)
        time.sleep(.1)
        d = self._readline()
        self._flush()
        self._sendBreak()
        self._flush()
        print(d)
        return d
    
    def getbfieldrelaypol(self):
        "Reads the field polarities from the Arduino relay"
        settings = 'get \n'
        self._write(settings)
        time.sleep(.1)
        output = {}
        d1 = self._readline()
        self._flush()
        self._sendBreak()
        self._flush()
        print(d1)
        return d1