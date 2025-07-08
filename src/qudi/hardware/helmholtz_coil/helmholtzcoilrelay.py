import serial
import time
import sys
import math as np
import pyvisa as visa
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState
from qudi.interface.helmholtz_coil_relay_interface import HelmholtzCoilRelayInterface
import pyfirmata

class HelmholtzCoilRelay(HelmholtzCoilRelayInterface):
    _relayaddress = ConfigOption("relay_address", missing="error")
    _pins = ConfigOption("relay_pinouts", missing = "error")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self):
        self.relay = pyfirmata.Arduino(self._relayaddress)
        it = pyfirmata.util.Iterator(self.relay)
        it.start()
        return

    def on_deactivate(self):
        self.relay.exit()
        self.relay.exit()


    def polarizationflip(self, pol, channel1, channel2):
        if pol=="1":
            self.relay.digital[channel1].write(1)
            self.relay.digital[channel2].write(1)
        else: 
            self.relay.digital[channel1].write(0)
            self.relay.digital[channel2].write(0)

    def setbfieldrelaypol(self,pols):
        self.polarizationflip(pols[0], self._pins[0], self._pins[1]) 
        self.polarizationflip(pols[1], self._pins[2], self._pins[3])

        self.polarizationflip(pols[2], self._pins[4], self._pins[5])

        read = self.getbfieldrelaypol()
        return read

    def getbfieldrelaypol(self):
        read = []
        for i in self._pins:
            read.append(self.relay.digital[i].read())
        print(read)
        return read