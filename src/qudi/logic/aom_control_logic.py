# -*- coding: utf-8 -*-

"""
Logic module for controlling power via AOM

John Jarman jcj27@cam.ac.uk

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import numpy as np
from datetime import datetime

from qudi.core.connector import Connector
from qudi.core.statusvariable import StatusVar
from qudi.util.mutex import Mutex
from qudi.core.module import LogicBase
from qtpy import QtCore

from qudi.core.configoption import ConfigOption

from nidaqmx.errors import DaqError

# from .pid_logic import PIDLogic
import simple_pid

class AomControlLogic(LogicBase):
    """
    Control laser power with AOM
    """

    sigAomUpdated = QtCore.Signal(dict)
    photodiode_channel = Connector(name= "photodiode_channel", interface='DataInStreamInterface')
    ao_nicard = Connector(name = "nicard_aom_ao", interface='ProcessSetpointInterface')

    # Config options
    photodiode_factor = ConfigOption('photodiode_factor')
    query_interval = ConfigOption('query_interval')
    ui_update_interval = ConfigOption('ui_update_interval')
    volt_range = ConfigOption('aom_volt_range')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """ Definition and initialisation of the GUI.
        """
        # Hardware
        self.daqcard = self.ao_nicard()
        self.pdread = self.photodiode_channel()
        self.aomchannel = self.daqcard.valid_channels[0]
        self.pdread.start_stream()
        self.daqcard.set_activity_state(self.aomchannel, True)


        # Kalman filter variables
        self.x = 0.0                 # A priori estimate of x
        self.P = 0.1                 # A priori estimate of x error

        # Kalman filter params
        self.R = 0.1**2     # Estimate of measurement variance (volts)
        self.Q = 5E-4       # Estimate of process variance (volts)

        self.pid_enabled = False
        self.pid = simple_pid.PID(
            Kp=2,
            Ki=5,
            Kd=0,
            setpoint=0,
            sample_time=None,
            output_limits=self.volt_range
        )

        self.current_volts = 0
        self.last_update_time = 0
        self.power = 0
        self.power_filtered = 0
        self.voltage_reading = 0

        self.start_poll()
        

    def on_deactivate(self):
        """Module deactivation
        """
        self.stop_poll()
        

    def start_poll(self):
        """
        Start polling DAQ
        """
        self._stop_poll = False
        QtCore.QTimer.singleShot(self.query_interval, self.update_power_reading)

    def stop_poll(self):
        """
        Stop polling DAQ
        """
        self._stop_poll = True


    def update_power_reading(self):
        """
        Get power reading from DAQ card.
        """
        if self._stop_poll == True:
            return

        try:
            # Read voltage from photodiode
            self._databuffer = np.zeros((10))
            self._samples_to_read = 10
            self._times_buffer = np.zeros(10, dtype=np.float64)
            
            # print("pre read pd databuffer", self._databuffer)
            # print("pd channel", self.pdread)
            self.pdread.read_data_into_buffer(data_buffer=self._databuffer,
                                                    samples_per_channel=self._samples_to_read,
                                                    timestamp_buffer=self._times_buffer)            
            # print("post read pd databuffer", self._databuffer)
            self.voltage_reading = np.mean(self._databuffer)

            # Do Kalman filtering
            prev_x = self.x
            estimate_P = self.P + self.Q

            # Estimate Kalman amplitude
            K = estimate_P / (estimate_P + self.R)

            self.x = prev_x + K * (self.voltage_reading - prev_x)
            self.P = (1-K) * estimate_P

            if self.pid_enabled:
                control_var = self.pid(self.x)
                self.set_aom_volts(control_var)
        
            if (self.last_update_time + (self.ui_update_interval - self.query_interval / 2)/1000
                < datetime.timestamp(datetime.now())):
                # If UI update interval has passed or will pass within the next
                # half of a query_interval, emit sigAomUpdated.
                
                self.last_update_time = datetime.timestamp(datetime.now())

                # Convert power to volts using factor
                self.power = self.voltage_reading * self.photodiode_factor
                self.power_filtered = self.x * self.photodiode_factor

                output_dict = {
                    'pd-voltage':self.voltage_reading,
                    'pd-power':self.power,
                    'pd-power-filtered':self.power_filtered,
                    'aom-output':self.current_volts
                }

                self.sigAomUpdated.emit(output_dict)
                
            QtCore.QTimer.singleShot(self.query_interval, self.update_power_reading)

        except DaqError as err:
            # Log any DAQ errors
            self.log.error('DAQ error {}'.format(err))

    def set_aom_volts(self, volts):
        """
        Set AOM output to specified volts.
        """
        volts = float(volts)
        if volts >= min(self.volt_range) and volts <= max(self.volt_range):
            # Check inside acceptable voltage range
            # Write to analogue output
            if self.aomchannel != '':
                self.daqcard.set_setpoint(self.aomchannel, volts)
                self.current_volts = volts
                return 0
            else:
                self.log.warn('No AOM channel specified - no output')
                return -1

    def enable_pid(self, state=True):
        """
        Enable/disable PID control.
        @param bool state: True to enable, False to disable.
        """
        if state:
            self.pid.set_auto_mode(True, last_output=self.current_volts)
            self.pid_enabled = True
        else:
            self.pid_enabled = False
            self.pid.set_auto_mode(False)

    @property
    def setpoint(self):
        return self.pid.setpoint * self.photodiode_factor

    @setpoint.setter
    def setpoint(self, val):
        volts = val / self.photodiode_factor
        self.pid.setpoint = volts