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
from qudi.util.network import netobtain

from qudi.interface.data_instream_interface import DataInStreamConstraints

from qudi.core.configoption import ConfigOption

from nidaqmx.errors import DaqError

# from .pid_logic import PIDLogic
import simple_pid

class APDLogic(LogicBase):
    """
    Control laser power with AOM
    """

    sigAPDUpdated = QtCore.Signal(dict)
    apd_channel = Connector(name= "apd_channel", interface='DataInStreamInterface')

    # Config options
    query_interval = ConfigOption('query_interval')
    ui_update_interval = ConfigOption('ui_update_interval')
    
    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """ Definition and initialisation of the GUI.
        """
        # Hardware
        self.apdread = self.apd_channel()
        self.apdread.start_stream()

        self.count_reading = 0

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
        QtCore.QTimer.singleShot(self.query_interval, self.update_count)

    def stop_poll(self):
        """
        Stop polling DAQ
        """
        self._stop_poll = True


    def update_count(self):
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
            self.apdread.read_data_into_buffer(data_buffer=self._databuffer,
                                                    samples_per_channel=self._samples_to_read,
                                                    timestamp_buffer=self._times_buffer)            
            # print("post read pd databuffer", self._databuffer)
            self.count = self._databuffer
        
            if (self.last_update_time + (self.ui_update_interval - self.query_interval / 2)/1000
                < datetime.timestamp(datetime.now())):
                # If UI update interval has passed or will pass within the next
                # half of a query_interval, emit sigAomUpdated.
                
                self.last_update_time = datetime.timestamp(datetime.now())

                output_dict = {
                    'counts':self.count_reading}

                self.sigAPDUpdated.emit(output_dict)
                
            QtCore.QTimer.singleShot(self.query_interval, self.update_count)

        except DaqError as err:
            # Log any DAQ errors
            self.log.error('DAQ error {}'.format(err))