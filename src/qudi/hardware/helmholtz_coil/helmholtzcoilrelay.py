import serial
import time
import sys
import math as np
import pyvisa as visa
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState
from qudi.interface.helmholtz_coil_relay_interface import HelmholtzCoilRelayInterface

class HelmholtzCoilRelay(HelmholtzCoilRelayInterface):
    _relayaddress = ConfigOption("relay_address", missing="error")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self):
        self.relay = serial.Serial(port=self._relayaddress, baudrate=9600, timeout=3) 
        self.relay.flush()

    def on_deactivate(self):
        self.relay.close()

    def _readline(self):
        self.relay.readline()

    def _write(self, command):
        self.relay.read(bytes(command, 'utf-8'))
    
    def _flush(self):
        self.relay.flush()
    
    def _sendBreak(self):
        self.relay.sendBreak()

    def setbfieldrelaypol(self, pols): ####neg = 1, pos = 0
        "Writes the polarity to the Arduino relay. Must be a 3-bit string made of 0s and 1s"
        settings = "set " + pols + '\n'
        self._write(settings)
        time.sleep(.1)
        d = self._readline()
        self._flush()
        self._sendBreak()
        self._flush()
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
        return d1