import qudi.hardware.attocube.ANC300 as ANC300
from qudi.core import LogicBase
from qudi.core import Connector, ConfigOption

from qtpy import QtCore
config = {'name' : "ANC300_attempt1",
                  'address' : 'COM3',
                    'x' : {
                        'voltage': 25, #piezo amplitude in Volts
                        'freq' : 1000 #piezo frequency in Hz
                        },
                    'y' : {
                        'voltage' : 25,
                        'freq' : 1000
                    },
                    'z' : {
                        'voltage' : 25,
                        'freq' : 1000
                    }
                  }

class PiezoControlLogic(LogicBase):

    #connectors
    _device = Connector(name='piezo', interface='piezostepper')
    #signals
    sigXAmpUpdated = QtCore.Signal()
    sigYAmpUpdated = QtCore.Signal()
    sigZAmpUpdated = QtCore.Signal()
    sigXFreqUpdated = QtCore.Signal()
    sigYFreqUpdated = QtCore.Signal()
    sigZFreqUpdated = QtCore.Signal()
    
    #config options
    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        return

    def set_param(self,inst,channel, type, val):
        if channel.lower == 'x':
            chan = 1
        if channel.lower == 'y':
            chan = 2
        if channel.lower == 'z':
            chan = 3
        inst.set_param(chan, type, val)

    def setall_volt(self, inst, vals):
        for i in range(0,3):
            inst.set_param(i, 'voltage', vals[i])

    def setall_freq(self, inst, vals):
        for i in range(0,3):
            inst.set_param(i, 'frequency', vals[i])
