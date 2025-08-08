
import numpy as np
from datetime import datetime

from qudi.core.connector import Connector
from qudi.core.statusvariable import StatusVar
from qudi.util.mutex import Mutex
from qudi.core.module import LogicBase
from qtpy import QtCore
from qudi.util.network import netobtain

from qudi.interface.finite_sampling_input_interface import FiniteSamplingInputConstraints
from qudi.core.configoption import ConfigOption

from nidaqmx.errors import DaqError
import matplotlib.pyplot as plt
import time
class PiezoStepperLogic(LogicBase):
    sigParamsUpdated = QtCore.Signal()
    sigAxisModeUpdated = QtCore.Signal()

    _device_ = Connector(name = "piezo_stepper", interface="PiezoStepperInterface")


    def on_activate(self):
        self.device = self._device_()
        return
    
    def on_deactivate(self):
        return
    

    def get_modes(self):
        modes = {
                    '1' : self.device.is_enabled(1),
                    '2' : self.device.is_enabled(2),
                    '3' : self.device.is_enabled(3)
        }
        return modes
    
    def update_params(self, vals):
        self.device.setallparams(vals)

    def get_param(self, channel, param):
        return self.device.get_param(channel, param)
        

    def step_clicked(self, axis, sign="+"):
        if self.is_enabled(axis)==True:
            if sign=="+":
                value = 1
            if sign == "-":
                value = -1
            self.device.step(axis, value)

    def continuous_pressed(self, axis, direction):
        self.device.jog(axis, direction)

    def continuous_released(self):
        self.device.stop()

    def ground_axis(self, axis="all"):
        self.device.disable_axis(axis)
        # self.update_modes()

    def enable_axis(self, axis="all"):
        self.device.enable_axis(axis)
        return self.device.is_enabled(axis)
        # self.update_modes()

    def is_enabled(self, axis="all"):
        mode = self.device.is_enabled(axis)
        print(axis, mode)
        return mode
