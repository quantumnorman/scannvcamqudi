# -*- coding: utf-8 -*-

"""
This file contains the qudi hardware module to use a National Instruments X-series card for input
of data of a certain length at a given sampling rate and data type.

Copyright (c) 2021, the qudi developers. See the AUTHORS.md file at the top-level directory of this
distribution and on <https://github.com/Ulm-IQO/qudi-iqo-modules/>

This file is part of qudi.

Qudi is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Qudi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with qudi.
If not, see <https://www.gnu.org/licenses/>.
"""

import ctypes
import time
import numpy as np
import nidaqmx as ni
from nidaqmx._lib import lib_importer  # Due to NIDAQmx C-API bug needed to bypass property getter
from nidaqmx.stream_readers import AnalogMultiChannelReader, CounterReader

from qudi.util.mutex import RecursiveMutex
from qudi.core.configoption import ConfigOption
from qudi.util.helpers import natural_sort
from qudi.interface.apd_counter_interface import APDCounterInterface, APDCounterConstraints


class NIXSeriesAPDCounter(APDCounterInterface):
    """
    A National Instruments device that can detect and count digital pulses and measure analog
    voltages in a finite sampling way.

    !!!!!! NI USB 63XX, NI PCIe 63XX and NI PXIe 63XX DEVICES ONLY !!!!!!

    See [National Instruments X Series Documentation](@ref nidaq-x-series) for details.

    Example config for copy-paste:

    ni_single_counter:
        module.Class: 'ni_x_series.ni_x_series_single_counter.NIXSeriesFiniteSamplingInput'
        options:
            device_name: 'Dev1'
            counter_channel: 'ctr0'
            apd_channel: 'PFI0'
            trigger_edge: RISING  # optional
            count_offset: 0 # optional
            count_direction: COUNT_UP # optional
    """

    # config options
    _device_name = ConfigOption(name='device_name', default='Dev1', missing='warn')
    _
    _physical_sample_clock_output = ConfigOption(name='sample_clock_output', default=None)
    _trigger_edge = ConfigOption(name='trigger_edge', default="RISING",
                                 constructor=lambda x: ni.constants.Edge[x.upper()], missing='warn')

    _adc_voltage_range = ConfigOption('adc_voltage_range', default=(-10, 10), missing='info')
    _max_channel_samples_buffer = ConfigOption(
        'max_channel_samples_buffer', default=25e6, missing='info')
    _counter_channel = ConfigOption('counter_channel', default = 'ctr0')
    _apd_channel = ConfigOption('apd_channel', default = 'PFI0')
    # TODO: check limits
    _sample_rate_limits = ConfigOption(name='sample_rate_limits', default=(1, 1e6))
    _frame_size_limits = ConfigOption(name='frame_size_limits', default=(1, 1e9))

    _rw_timeout = ConfigOption('read_write_timeout', default=10, missing='nothing')

    # Hardcoded data type
    __data_type = np.float64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # NIDAQmx device handle
        self._device_handle = None
        # Task handles for NIDAQmx tasks
        self._di_task_handles = list()
        self._ai_task_handle = None
        self._clk_task_handle = None
        # nidaqmx stream reader instances to help with data acquisition
        self._di_readers = list()
        self._ai_reader = None

        # List of all available counters and terminals for this device
        self.__all_counters = tuple()
        self.__all_digital_terminals = tuple()
        self.__all_analog_terminals = tuple()

        # currently active channels
        self.__active_channels = {'counter' : self._counter_channel.lower(), 'apd' : self._apd_channel.lower()}

        self._thread_lock = RecursiveMutex()
        self._sample_rate = -1
        self._frame_size = -1
        self._constraints = None

    def on_activate(self):
        """
        Starts up the NI-card and performs sanity checks.
        """

        self._device_name = self._device_name.lower()
        self._apd_channel = self._apd_channel.lower()
        self._counter_channel = self._counter_channel.lower()
        # Check if device is connected and set device to use
        dev_names = [name.lower() for name in ni.system.System().devices.device_names]
        if self._device_name not in dev_names:
            raise ValueError(
                f'Device name "{self._device_name}" not found in list of connected devices: '
                f'{dev_names}\nActivation of NIXSeriesInStreamer failed!'
            )
        self._device_handle = ni.system.Device(self._device_name)

        counters = [name.lower() for name in self._device_handle.ci_physical_chans.channel_names]
        if self._device_name+'/'+self._counter_channel not in counters:
            raise ValueError(
                f'Counter channel "{self._counter_channel}" not found in list of available counters: '
                f'{counters}\nActivation of NIXSeriesInStreamer failed!'
            )
            

        terminals = self._device_handle.terminals
        if '/'+self._device_name+'/'+self._apd_channel not in terminals:
            raise ValueError(
                f'APD channel "{self._apd_channel}" not found in list of available terminals: '
                f'{terminals}\nActivation of NIXSeriesInStreamer failed!'

            )

        # Make sure the ConfigOptions have correct values and types
        # (ensured by FiniteSamplingInputConstraints)
        self._sample_rate_limits = self._constraints.sample_rate_limits
        self._frame_size_limits = self._constraints.frame_size_limits
        self._channel_units = self._constraints.channel_units

        # initialize default settings
        self._sample_rate = self._constraints.max_sample_rate
        # TODO: Get real sample rate limits depending on specified channels (see NI FSIO), or include in "ni helper".
        self._frame_size = 0

    def on_deactivate(self):
        """ Shut down the NI card.
        """
        self.terminate_all_tasks()
        return

    @property
    def constraints(self):
        return self._constraints

    @property
    def active_channels(self):
        return self.__active_channels['counter'].union(self.__active_channels['apd'])

    @property
    def sample_rate(self):
        """
        The currently set sample rate

        @return float: current sample rate in Hz
        """
        return self._sample_rate

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def samples_in_buffer(self):
        """ Currently available samples per channel being held in the input buffer.
        This is the current minimum number of samples to be read with "get_buffered_samples()"
        without blocking.

        @return int: Number of unread samples per channel
        """
        with self._thread_lock:
            if self.module_state() == 'locked':
                if self._ai_task_handle is None:
                    return self._di_task_handles[0].in_stream.avail_samp_per_chan
                else:
                    return self._ai_task_handle.in_stream.avail_samp_per_chan
            return 0

    def set_sample_rate(self, rate):
        sample_rate = float(rate)
        assert self._constraints.sample_rate_in_range(sample_rate)[0], \
            f'Sample rate "{sample_rate}Hz" to set is out of ' \
            f'bounds {self._constraints.sample_rate_limits}'
        with self._thread_lock:
            assert self.module_state() == 'idle', \
                'Unable to set sample rate. Data acquisition in progress.'
            self._sample_rate = sample_rate
            self.log.debug(f'set sample_rate to {self._sample_rate}')
        return



    def set_frame_size(self, size):
        """ Will set the number of samples per channel to acquire within one frame.

        @param int size: The sample rate to set
        """
        samples = int(round(size))
        assert self._constraints.frame_size_in_range(samples)[0], \
            f'frame size "{samples}" to set is out of bounds {self._constraints.frame_size_limits}'
        with self._thread_lock:
            assert self.module_state() == 'idle', \
                'Unable to set frame size. Data acquisition in progress.'
            self._frame_size = samples
            self.log.debug(f'set frame_size to {self._frame_size}')

    def start_buffered_acquisition(self):
        """ Will start the acquisition of a data frame in a non-blocking way.
        Must return immediately and not wait for the data acquisition to finish.

        Must raise exception if data acquisition can not be started.
        """
        assert self.module_state() == 'idle', \
            'Unable to start data acquisition. Data acquisition already in progress.'
        self.module_state.lock()

        # set up tasks
        if self._init_sample_clock() < 0:
            self.terminate_all_tasks()
            self.module_state.unlock()
            raise NiInitError('Sample clock initialization failed; all tasks terminated')
        if self._init_digital_tasks() < 0:
            self.terminate_all_tasks()
            self.module_state.unlock()
            raise NiInitError('Counter task initialization failed; all tasks terminated')
        if self._init_analog_task() < 0:
            self.terminate_all_tasks()
            self.module_state.unlock()
            raise NiInitError('Analog in task initialization failed; all tasks terminated')

        # start tasks
        if len(self._di_task_handles) > 0:
            try:
                for task in self._di_task_handles:
                    task.start()
            except ni.DaqError:
                self.terminate_all_tasks()
                self.module_state.unlock()
                raise

        if self._ai_task_handle is not None:
            try:
                self._ai_task_handle.start()
            except ni.DaqError:
                self.terminate_all_tasks()
                self.module_state.unlock()
                raise

        try:
            self._clk_task_handle.start()
        except ni.DaqError:
            self.terminate_all_tasks()
            self.module_state.unlock()
            raise

    def stop_buffered_acquisition(self):
        """ Will abort the currently running data frame acquisition.
        Will return AFTER the data acquisition has been terminated without waiting for all samples
        to be acquired (if possible).

        Must NOT raise exceptions if no data acquisition is running.
        """
        if self.module_state() == 'locked':
            self.terminate_all_tasks()
            self.module_state.unlock()

    def get_buffered_samples(self, number_of_samples=None):
        """ Returns a chunk of the current data frame for all active channels read from the frame
        buffer.
        If parameter <number_of_samples> is omitted, this method will return the currently
        available samples within the frame buffer (i.e. the value of property <samples_in_buffer>).
        If <number_of_samples> is exceeding the currently available samples in the frame buffer,
        this method will block until the requested number of samples is available.
        If the explicitly requested number of samples is exceeding the number of samples pending
        for acquisition in the rest of this frame, raise an exception.

        Samples that have been already returned from an earlier call to this method are not
        available anymore and can be considered discarded by the hardware. So this method is
        effectively decreasing the value of property <samples_in_buffer> (until new samples have
        been read).

        If the data acquisition has been stopped before the frame has been acquired completely,
        this method must still return all available samples already read into buffer.

        @param int number_of_samples: optional, the number of samples to read from buffer

        @return dict: Sample arrays (values) for each active channel (keys)
        """
        data = dict()
        if self.module_state() == 'idle' and self.samples_in_buffer < 1:
            self.log.error('Unable to read data. Device is not running and no data in buffer.')
            return data

        number_of_samples = self.samples_in_buffer if number_of_samples is None else number_of_samples

        if number_of_samples > self._frame_size:
            raise ValueError(
                f'Number of requested samples ({number_of_samples}) exceeds number of samples '
                f'pending for acquisition ({self._frame_size}).'
            )

        if number_of_samples is not None and self.module_state() == 'locked':
            request_time = time.time()
            while number_of_samples > self.samples_in_buffer:  # TODO: Check whether this works with a real HW
                # TODO could one use the ni timeout of the reader class here?
                if time.time() - request_time < 1.1 * self._frame_size / self._sample_rate:  # TODO Is this timeout ok?
                    time.sleep(0.05)
                else:
                    self.terminate_all_tasks()
                    self.module_state.unlock()
                    raise TimeoutError(f'Acquiring {number_of_samples} samples took longer than the whole frame.')
        try:
            # TODO: What if counter stops while waiting for samples?

            # Read digital channels
            for i, reader in enumerate(self._di_readers):
                data_buffer = np.zeros(number_of_samples)
                # read the counter value. This function is blocking.
                read_samples = reader.read_many_sample_double(
                    data_buffer,
                    number_of_samples_per_channel=number_of_samples,
                    timeout=self._rw_timeout)
                if read_samples != number_of_samples:
                    return data
                data_buffer *= self._sample_rate
                # TODO Multiplication by self._sample_rate to convert to c/s, from counts/clock cycle
                #  What if unit not c/s?
                data[reader._task.name.split('_')[-1]] = data_buffer

            # Read analog channels
            if self._ai_reader is not None:
                data_buffer = np.zeros(number_of_samples * len(self.__active_channels['ai_channels']))
                read_samples = self._ai_reader.read_many_sample(
                    data_buffer,
                    number_of_samples_per_channel=number_of_samples,
                    timeout=self._rw_timeout)
                if read_samples != number_of_samples:
                    return data
                for num, ai_channel in enumerate(self.__active_channels['ai_channels']):
                    data[ai_channel] = data_buffer[num * number_of_samples:(num + 1) * number_of_samples]

        except ni.DaqError:
            self.log.exception('Getting samples from streamer failed.')
            return data
        return data

    def acquire_counts(self, frame_size=None):
        """ Acquire a single data frame for all active channels.
        This method call is blocking until the entire data frame has been acquired.

        If an explicit frame_size is given as parameter, it will not overwrite the property
        <frame_size> but just be valid for this single frame.

        See <start_buffered_acquisition>, <stop_buffered_acquisition> and <get_buffered_samples>
        for more details.

        @param int frame_size: optional, the number of samples to acquire in this frame

        @return dict: Sample arrays (values) for each active channel (keys)
        """
        with self._thread_lock:
            if frame_size is None:
                buffered_frame_size = None
            else:
                buffered_frame_size = self._frame_size
                self.set_frame_size(frame_size)

            self.start_buffered_acquisition()
            data = self.get_buffered_samples(self._frame_size)
            self.stop_buffered_acquisition()

            if buffered_frame_size is not None:
                self._frame_size = buffered_frame_size
            return data

    # =============================================================================================


    def init_counter_task(self, edge_type = ni.constants.Edge.RISING, count_offset=0, count_dir=ni.constants.CountDirection.COUNT_UP):
        try:
            self.counter_task = ni.Task()
            
            channel = self.counter_task.ci_channels.add_ci_count_edges_chan(self._device_name+'/'+self._counter_channel, 'counter channel', edge = edge_type, initial_count=count_offset, count_direction=count_dir)
            channel.ci_count_edges_term = '/'+self._device_name+'/'+self._apd_channel
            try:
                self.counter_task.control(ni.constants.TaskMode.TASK_RESERVE)
            except ni.DaqError:
                try:
                    self.counter_task.close()
                except: 'Unable to reserve task and unable to close task'
        except: print('already initialized')



    def reset_hardware(self):
        """
        Resets the NI hardware, so the connection is lost and other programs can access it.
        @return int: error code (0:OK, -1:error)
        """
        try:
            self._device_handle.reset_device()
            self.log.info('Reset device {0}.'.format(self._device_name))
        except ni.DaqError:
            self.log.exception('Could not reset NI device {0}'.format(self._device_name))
            return -1
        return 0

    def terminate_all_tasks(self):
        self.counter_task.close()



class NiInitError(Exception):
    pass
