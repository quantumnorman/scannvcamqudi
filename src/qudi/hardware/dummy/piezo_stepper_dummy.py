from qudi.interface.piezo_stepper_interface import PiezoStepperInterface
from qudi.core import ConfigOption
from qudi.util.mutex import RecursiveMutex


class PiezoStepperDummy(PiezoStepperInterface):
    _coms_info = ConfigOption('inst_info', default={'name' : 'ANC300', 'address' : "COM3"})
    _default_params = ConfigOption("default_params", default = {
                    '1' : {
                        'voltage': 25, #piezo amplitude in Volts
                        'frequency' : 1000 #piezo frequency in Hz
                        },
                    '2' : {
                        'voltage' : 25,
                        'frequency' : 1000
                    },
                    '3' : {
                        'voltage' : 25,
                        'frequency' : 1000
                    }
                  })
    
    def on_activate(self):
        self.disable_axis("all")
        self.values=self._default_params
        self.setallparams(self._default_params)

        return
    
    def on_deactivate(self):
        return

    def setallparams(self, vals):
        for i in self.values:
            # self.device.set_param(vals[i], 'voltage', vals[i]['voltage'])
            # self.device.set_param(vals(i), 'frequency', vals[i]['frequency'])
            print(type(i))
            # print(vals[i], 'voltage', vals[i]['voltage'])
            # print(vals[i], 'frequency', vals[i]['frequency'])

    def set_param(self, channel, param, value):
        print("set param")

    def get_param(self, channel, param):
        print(channel, param, 'get')

    def step(self, channel, sign="+"):
        if self.is_enabled(channel)==True:
            if sign=="+":
                value = 1
            if sign == "-":
                value = -1
            # self.device.step(channel, value)
            print('step', channel, sign)
        else: print("channel grounded, cannot move")

    def jog(self, channel, direction="+"):
        if self.is_enabled(channel)==True:
            # self.device.jog(channel, direction)
            print('jog', channel, direction)
        else: print("channel disabled, cannot move")

    def stop(self, axis = "all"):
        # self.device.stop()
        print('stop')

    def disable_axis(self, axis="all"):
        # self.device.disable_axis(axis)
        print("grounded", axis)

    def enable_axis(self, axis="all"):
        # self.device.enable_channel(axis)
        print(axis, "enabled")

    def is_enabled(self, axis="all"):
        # mode = self.device.is_enabled(axis)
        print(axis, "enabled?")
        # return mode
