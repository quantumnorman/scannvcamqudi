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

from qudi.interface.finite_sampling_input_interface import FiniteSamplingInputConstraints
from qudi.core.configoption import ConfigOption

from nidaqmx.errors import DaqError
import matplotlib.pyplot as plt
import time

# from .pid_logic import PIDLogic
import simple_pid

class CountingLogic(LogicBase):
    """
    Control laser power with AOM
    """
    sigCounterUpdated = QtCore.Signal()

    sigCountDataNext = QtCore.Signal()

    sigCountingSamplesChanged = QtCore.Signal(int)
    sigCountLengthChanged = QtCore.Signal(int)
    sigCountFrequencyChanged = QtCore.Signal(float)
    sigSavingStatusChanged = QtCore.Signal(bool)
    sigCountStatusChanged = QtCore.Signal(bool)
    
    counter1 = Connector(name= "apd_channel", interface='APDCounterInterfaceSimple')

    # Config options
    _count_length = StatusVar("count_length", default=300)
    _smooth_window_length = StatusVar("smooth_window_length", default=10)
    _counting_samples = StatusVar('counting_samples', 10)
    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.threadlock = Mutex()

    def on_activate(self):
        """ Definition and initialisation of the GUI.
        """
        # Hardware
        self._counting_device = self.counter1()

        self.countdata = np.zeros( self._count_length)
        self.countdata_smoothed = np.zeros(self._count_length)
        self.rawdata = np.zeros( self._counting_samples)
        self._already_counted_samples = 0  # For gated counting
        
        self.stopRequested = False

        self.sigCountDataNext.connect(self.count_loop_body, QtCore.Qt.QueuedConnection)


    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        # Save parameters to disk

        # Stop measurement
        if self.module_state() == 'locked':
            self._stopCount_wait()

        self.sigCountDataNext.disconnect()
        return

    # def set_counting_samples(self, samples=1):
    #     """
    #     Sets the length of the counted bins.
    #     The counter is stopped first and restarted afterwards.

    #     @param int samples: oversampling in units of bins (positive int ).

    #     @return int: oversampling in units of bins.
    #     """
    #     # Determine if the counter has to be restarted after setting the parameter
    #     if self.module_state() == 'locked':
    #         restart = True
    #     else:
    #         restart = False

    #     if samples > 0:
    #         self._stopCount_wait()
    #         self._counting_samples = int(samples)
    #         # if the counter was running, restart it
    #         if restart:
    #             self.startCount()
    #     else:
    #         self.log.warning('counting_samples has to be larger than 0! Command ignored!')
    #     self.sigCountingSamplesChanged.emit(self._counting_samples)
    #     return self._counting_samples
    
    # def set_count_length(self, length=300):
    #     """ Sets the time trace in units of bins.

    #     @param int length: time trace in units of bins (positive int).

    #     @return int: length of time trace in units of bins

    #     This makes sure, the counter is stopped first and restarted afterwards.
    #     """
    #     if self.module_state() == 'locked':
    #         restart = True
    #     else:
    #         restart = False

    #     if length > 0:
    #         self._stopCount_wait()
    #         self._count_length = int(length)
    #         # if the counter was running, restart it
    #         if restart:
    #             self.startCount()
    #     else:
    #         self.log.warning('count_length has to be larger than 0! Command ignored!')
    #     self.sigCountLengthChanged.emit(self._count_length)
    #     return self._count_length

    def startCount(self):
    #     """ This is called externally, and is basically a wrapper that
    #         redirects to the chosen counting mode start function.

    #         @return error: 0 is OK, -1 is error
    #     """
    #     # Sanity checks
    #     constraints = self.get_hardware_constraints()
        with self.threadlock:
            # Lock module
            if self.module_state() != 'locked':
                self.module_state.lock()
            else:
                self.log.warning('Counter already running. Method call ignored.')
                return 0
            # Set up clock and counter
            self._counting_device.init_all()


    #         # initialising the data arrays
            self.rawdata = np.zeros(self._counting_samples)
            self.countdata = np.zeros(self._count_length)
            self.countdata_smoothed = np.zeros(self._count_length)
            self._sampling_data = np.empty(self._counting_samples)

    #         # Start data reader loop
            self.sigCountStatusChanged.emit(True)
            self.sigCountDataNext.emit()
            return

    def stopCount(self):
        """ Set a flag to request stopping counting.
        """
        if self.module_state() == 'locked':
            with self.threadlock:
                self.stopRequested = True
        return

    def count_loop_body(self):
        """ This method gets the count data from the hardware for the continuous counting mode (default).

        It runs repeatedly in the logic module event loop by being connected
        to sigCountContinuousNext and emitting sigCountContinuousNext through a queued connection.
        """
        if self.module_state() == 'locked':
            with self.threadlock:
                # check for aborts of the thread in break if necessary
                if self.stopRequested:
                    # close off the actual counter
                    cnt_err = self._counting_device.close_tasks()
                    if cnt_err < 0:
                        self.log.error('Could not even close the hardware, giving up.')
                    # switch the state variable off again
                    self.stopRequested = False
                    self.module_state.unlock()
                    self.sigCounterUpdated.emit()
                    return
                # read the current counter value
                self.rawdata = self._counting_device.acquire_frame(self._counting_samples)
            # call this again from event loop
            self.sigCounterUpdated.emit()
            self.sigCountDataNext.emit()

    def _process_data_continous(self):
        """
        Processes the raw data from the counting device
        @return:
        """
            # remember the new count data in circular array
        self.countdata[0] = np.average(self.rawdata)
        # move the array to the left to make space for the new data
        self.countdata = np.roll(self.countdata, -1, axis=1)
        # also move the smoothing array
        self.countdata_smoothed = np.roll(self.countdata_smoothed, -1, axis=1)
        # calculate the median and save it
        window = -int(self._smooth_window_length / 2) - 1
        
        self.countdata_smoothed[window:] = np.median(self.countdata[
                                                        -self._smooth_window_length:])
        # if we don't want to use oversampling
        newdata = np.empty((2, ))
        newdata[1] = self.countdata[-1]
        return


    # def _stopCount_wait(self, timeout=5.0):
    #     """
    #     Stops the counter and waits until it actually has stopped.

    #     @param timeout: float, the max. time in seconds how long the method should wait for the
    #                     process to stop.

    #     @return: error code
    #     """
    #     self.stopCount()
    #     start_time = time.time()
    #     while self.module_state() == 'locked':
    #         time.sleep(0.1)
    #         if time.time() - start_time >= timeout:
    #             self.log.error('Stopping the counter timed out after {0}s'.format(timeout))
    #             return -1
    #     return 0
