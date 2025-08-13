import sys
sys.path.append(r"C:\Users\QOMS-User\Code")

from pylablib.devices import Attocube
import time
from qudi.interface.piezo_stepper_interface import PiezoStepperInterface
from qudi.core import ConfigOption
from qudi.util.mutex import RecursiveMutex
##TODO: pull constraints from config instead of hardcode 0-80 volts and 0-100Hz


class ANC300(PiezoStepperInterface):
    ''' Class for ANC300 Piezo Controller to talk to device over rypc server. 
        Possible to add functionality from available functions at: 
        https://pylablib.readthedocs.io/en/latest/.apidoc/pylablib.devices.Attocube.html#pylablib.devices.Attocube.anc300.ANC300.get_axis_serial
        if functisons are added to this class.
    '''

    _config_info = ConfigOption('inst_info', default={'name' : 'ANC300', 'address' : "COM3"})
    _default_params = ConfigOption("default_params", default = {
                    '1' : {
                        'voltage': 25, #piezo amplitude in Volts
                        'frequency' : 100 #piezo frequency in Hz
                        },
                    '2' : {
                        'voltage' : 25,
                        'frequency' : 100
                    },
                    '3' : {
                        'voltage' : 25,
                        'frequency' : 100
                    }
                  })
    def on_activate(self):
        self.name = self._config_info['name']
        self.address = self._config_info['address']
        try:
            self.device = Attocube.ANC300(self.address)  # USB or RS232 connection
            print('Successfully connected to the ANC300 on address {}'.format(self.address))
        except Exception as e:
            print('Failed to connect to the ANC300 on address {} because:\n'.format(self.address))
            print(e)
        self.disable_axis("all")
        self.values=self._default_params
        self.setallparams(self.values)

    def on_deactivate(self):
        self.close()
        return
    # Getters and setters
  
    def get_param(self, channel, param):
        
        if param == 'capacitance':
            cap = self.device.get_capacitance(channel, measure=True)
            return float(cap)
        elif param == 'voltage':
            vol = self.device.get_voltage(channel)
            return float(vol)
        elif param == 'frequency':
            freq = self.device.get_frequency(channel)
            return freq
        
    def setallparams(self, vals):
        for i in self.values:
            self.set_param(int(i), 'voltage', vals[i]['voltage'])
            self.set_param(int(i), 'frequency', vals[i]['frequency'])

    def set_param(self, channel, param, value):
        if param == 'voltage':
            if 0<=value<=80:
                self.device.set_voltage(channel, value)
                return
            else:
                print('Voltage  outside of limits', value)
                return
        if param == 'frequency':
            if 0<=value<=150:
                self.device.set_frequency(channel, value)
                return
            else:
                print('Frequency outside of limits', value)
                return

    def step(self, channel, value=1, sign="+"):
        if self.is_enabled(channel)==True:
            if sign=="+":
                value = value
            if sign == "-":
                value = -1*value
            self.device.move_by(channel, value)
            print('step', channel, sign)
        else: print("channel grounded, cannot move")

    def jog(self, channel, direction="+"):
        if self.is_enabled(channel)==True:
            self.device.jog(channel, direction)
        else: print("channel grounded, cannot move")

    def stop(self, axis = "all"):
        self.device.stop()

    def enable_axis(self, channel): 
        self.device.enable_axis(channel)
        return
    
    def disable_axis(self, channel):
        self.device.disable_axis(channel)
        return
    
    def is_enabled(self, axis):
        return self.device.is_enabled(axis)

    def close(self):
        self.stop()
        self.disable_axis("all")
        self.device.close()