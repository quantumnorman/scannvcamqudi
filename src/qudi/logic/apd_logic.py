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

    sigGatedCounterFinished = QtCore.Signal()
    sigGatedCounterContinue = QtCore.Signal(bool)
    sigCountingSamplesChanged = QtCore.Signal(int)
    sigCountLengthChanged = QtCore.Signal(int)
    sigCountFrequencyChanged = QtCore.Signal(float)
    sigSavingStatusChanged = QtCore.Signal(bool)
    sigCountStatusChanged = QtCore.Signal(bool)
    
    counter1 = Connector(name= "apd_channel", interface='APDCounterInterface')

    # Config options
    _count_length = StatusVar("count_length", default=300)
    _smooth_window_length = StatusVar("smooth_window_length", default=10)
    _counting_samples = StatusVar('counting_samples', 10)
    _count_frequency = StatusVar('count_frequency', 50)
    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.threadlock = Mutex()

    def on_activate(self):
        """ Definition and initialisation of the GUI.
        """
        # Hardware
        self._counting_device = self.counter1()

        self.countdata = np.zeros([len(self.get_channels()), self._count_length])
        self.countdata_smoothed = np.zeros([len(self.get_channels()), self._count_length])
        self.rawdata = np.zeros([len(self.get_channels()), self._counting_samples])
        self._already_counted_samples = 0  # For gated counting
        self._data_to_save = []
        
        self.stopRequested = False

        self._saving_start_time = time.time()
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


    def get_hardware_constraints(self):
        """
        Retrieve the hardware constrains from the counter device.

        @return SlowCounterConstraints: object with constraints for the counter
        """


        return self._counting_device._constraints
    
    def get_channels(self):
        """ Shortcut for hardware get_counter_channels.

            @return list(str): return list of active counter channel names
        """
        channels = []
        for channel in self._counting_device._channel_units:
            channels.append(channel)
        return channels
        return


    def set_counting_samples(self, samples=1):
        """
        Sets the length of the counted bins.
        The counter is stopped first and restarted afterwards.

        @param int samples: oversampling in units of bins (positive int ).

        @return int: oversampling in units of bins.
        """
        # Determine if the counter has to be restarted after setting the parameter
        if self.module_state() == 'locked':
            restart = True
        else:
            restart = False

        if samples > 0:
            self._stopCount_wait()
            self._counting_samples = int(samples)
            # if the counter was running, restart it
            if restart:
                self.startCount()
        else:
            self.log.warning('counting_samples has to be larger than 0! Command ignored!')
        self.sigCountingSamplesChanged.emit(self._counting_samples)
        return self._counting_samples
    
    def set_count_length(self, length=300):
        """ Sets the time trace in units of bins.

        @param int length: time trace in units of bins (positive int).

        @return int: length of time trace in units of bins

        This makes sure, the counter is stopped first and restarted afterwards.
        """
        if self.module_state() == 'locked':
            restart = True
        else:
            restart = False

        if length > 0:
            self._stopCount_wait()
            self._count_length = int(length)
            # if the counter was running, restart it
            if restart:
                self.startCount()
        else:
            self.log.warning('count_length has to be larger than 0! Command ignored!')
        self.sigCountLengthChanged.emit(self._count_length)
        return self._count_length
    
    def set_count_frequency(self, frequency=50):
        """ Sets the frequency with which the data is acquired.

        @param float frequency: the desired frequency of counting in Hz

        @return float: the actual frequency of counting in Hz

        This makes sure, the counter is stopped first and restarted afterwards.
        """
        constraints = self.get_hardware_constraints()

        if self.module_state() == 'locked':
            restart = True
        else:
            restart = False

        if constraints.min_sample_rate <= frequency <= constraints.max_sample_rate:
            self._stopCount_wait()
            self._count_frequency = frequency
            # if the counter was running, restart it
            if restart:
                self.startCount()
        else:
            self.log.warning('count_frequency not in range! Command ignored!')
        self.sigCountFrequencyChanged.emit(self._count_frequency)
        return self._count_frequency

    def get_count_length(self):
        """ Returns the currently set length of the counting array.

        @return int: count_length
        """
        return self._count_length

    #FIXME: get from hardware
    def get_count_frequency(self):
        """ Returns the currently set frequency of counting (resolution).

        @return float: count_frequency
        """
        return self._count_frequency

    def get_counting_samples(self):
        """ Returns the currently set number of samples counted per readout.

        @return int: counting_samples
        """
        return self._counting_samples

    def draw_figure(self, data):
        """ Draw figure to save with data file.

        @param: nparray data: a numpy array containing counts vs time for all detectors

        @return: fig fig: a matplotlib figure object to be saved to file.
        """
        count_data = data[:, 1:len(self.get_channels())+1]
        time_data = data[:, 0]

        # Scale count values using SI prefix
        prefix = ['', 'k', 'M', 'G']
        prefix_index = 0
        while np.max(count_data) > 1000:
            count_data = count_data / 1000
            prefix_index = prefix_index + 1
        counts_prefix = prefix[prefix_index]

        # Use qudi style

        # Create figure
        fig, ax = plt.subplots()
        ax.plot(time_data, count_data, linestyle=':', linewidth=0.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Fluorescence (' + counts_prefix + 'c/s)')
        return fig
    def startCount(self):
        """ This is called externally, and is basically a wrapper that
            redirects to the chosen counting mode start function.

            @return error: 0 is OK, -1 is error
        """
        # Sanity checks
        constraints = self.get_hardware_constraints()
        with self.threadlock:
            # Lock module
            if self.module_state() != 'locked':
                self.module_state.lock()
            else:
                self.log.warning('Counter already running. Method call ignored.')
                return 0
            # Set up clock
            
            # Set up counter
            counter_status = self._counting_device.set_active_channels(self.get_channels())

            # initialising the data arrays
            self.rawdata = np.zeros([len(self.get_channels()), self._counting_samples])
            self.countdata = np.zeros([len(self.get_channels()), self._count_length])
            self.countdata_smoothed = np.zeros([len(self.get_channels()), self._count_length])
            self._sampling_data = np.empty([len(self.get_channels()), self._counting_samples])
            # the sample index for gated counting
            self._already_counted_samples = 0

            # Start data reader loop
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
                    cnt_err = self._counting_device.close_counter()
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
        for i, ch in enumerate(self.get_channels()):
            # remember the new count data in circular array
            self.countdata[i, 0] = np.average(self.rawdata[i])
        # move the array to the left to make space for the new data
        self.countdata = np.roll(self.countdata, -1, axis=1)
        # also move the smoothing array
        self.countdata_smoothed = np.roll(self.countdata_smoothed, -1, axis=1)
        # calculate the median and save it
        window = -int(self._smooth_window_length / 2) - 1
        for i, ch in enumerate(self.get_channels()):
            self.countdata_smoothed[i, window:] = np.median(self.countdata[i,
                                                            -self._smooth_window_length:])

        # save the data if necessary
        if self._saving:
             # if oversampling is necessary
            if self._counting_samples > 1:
                chans = self.get_channels()
                self._sampling_data = np.empty([len(chans) + 1, self._counting_samples])
                self._sampling_data[0, :] = time.time() - self._saving_start_time
                for i, ch in enumerate(chans):
                    self._sampling_data[i+1, 0] = self.rawdata[i]

                self._data_to_save.extend(list(self._sampling_data))
            # if we don't want to use oversampling
            else:
                # append tuple to data stream (timestamp, average counts)
                chans = self.get_channels()
                newdata = np.empty((len(chans) + 1, ))
                newdata[0] = time.time() - self._saving_start_time
                for i, ch in enumerate(chans):
                    newdata[i+1] = self.countdata[i, -1]
                self._data_to_save.append(newdata)
        return

    def _process_data_gated(self):
        """
        Processes the raw data from the counting device
        @return:
        """
        # remember the new count data in circular array
        self.countdata[0] = np.average(self.rawdata[0])
        # move the array to the left to make space for the new data
        self.countdata = np.roll(self.countdata, -1)
        # also move the smoothing array
        self.countdata_smoothed = np.roll(self.countdata_smoothed, -1)
        # calculate the median and save it
        self.countdata_smoothed[-int(self._smooth_window_length / 2) - 1:] = np.median(
            self.countdata[-self._smooth_window_length:])

        # save the data if necessary
        if self._saving:
            # if oversampling is necessary
            if self._counting_samples > 1:
                self._sampling_data = np.empty((self._counting_samples, 2))
                self._sampling_data[:, 0] = time.time() - self._saving_start_time
                self._sampling_data[:, 1] = self.rawdata[0]
                self._data_to_save.extend(list(self._sampling_data))
            # if we don't want to use oversampling
            else:
                # append tuple to data stream (timestamp, average counts)
                self._data_to_save.append(np.array((time.time() - self._saving_start_time,
                                                    self.countdata[-1])))
        return

    def _process_data_finite_gated(self):
        """
        Processes the raw data from the counting device
        @return:
        """
        if self._already_counted_samples+len(self.rawdata[0]) >= len(self.countdata):
            needed_counts = len(self.countdata) - self._already_counted_samples
            self.countdata[0:needed_counts] = self.rawdata[0][0:needed_counts]
            self.countdata = np.roll(self.countdata, -needed_counts)
            self._already_counted_samples = 0
            self.stopRequested = True
        else:
            # replace the first part of the array with the new data:
            self.countdata[0:len(self.rawdata[0])] = self.rawdata[0]
            # roll the array by the amount of data it had been inserted:
            self.countdata = np.roll(self.countdata, -len(self.rawdata[0]))
            # increment the index counter:
            self._already_counted_samples += len(self.rawdata[0])
        return

    def _stopCount_wait(self, timeout=5.0):
        """
        Stops the counter and waits until it actually has stopped.

        @param timeout: float, the max. time in seconds how long the method should wait for the
                        process to stop.

        @return: error code
        """
        self.stopCount()
        start_time = time.time()
        while self.module_state() == 'locked':
            time.sleep(0.1)
            if time.time() - start_time >= timeout:
                self.log.error('Stopping the counter timed out after {0}s'.format(timeout))
                return -1
        return 0
    
    def get_saving_state(self):
        """ Returns if the data is saved in the moment.

        @return bool: saving state
        """
        return False