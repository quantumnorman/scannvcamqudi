from pylablib.devices import Attocube
import time


class ANC300():
    ''' Class for ANC300 Piezo Controller to talk to device over rypc server. 
        Possible to add functionality from available functions at: 
        https://pylablib.readthedocs.io/en/latest/.apidoc/pylablib.devices.Attocube.html#pylablib.devices.Attocube.anc300.ANC300.get_axis_serial
        if functions are added to this class.
    '''
    def __init__(self, config):
        self.name = config['name']
        self.address = config['address']
        # Connect
        try:
            self.device = Attocube.ANC300(self.address)  # USB or RS232 connection
            print('Successfully connected to the ANC300 on address {}'.format(self.address))
        except Exception as e:
            print('Failed to connect to the ANC300 on address {} because:\n'.format(self.address))
            print(e)

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



    def enable_axis(self, channel): 
        self.device.enable_axis(channel)
        return
    
    def disable_axis(self, channel):
        self.device.disable_axis(channel)
        return

    def axis_status(self, channel):
        return self.device.is_enabled(channel)
    
    def step(self, channel, value):
        self.device.move_by(channel, steps= value)
        return

    def jog(self, channel, direction):
        self.device.jog(channel, direction)
        return
    
    def stop(self,axis="all"):
        self.device.stop()
        return
    
    def is_enabled(self, axis):
        self.device.is_enabled(axis)
