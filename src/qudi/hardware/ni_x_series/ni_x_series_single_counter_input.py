# # -*- coding: utf-8 -*-

# """
# This file contains the qudi hardware module to use a National Instruments X-series card for input
# of data of a certain length at a given sampling rate and data type.

# Copyright (c) 2021, the qudi developers. See the AUTHORS.md file at the top-level directory of this
# distribution and on <https://github.com/Ulm-IQO/qudi-iqo-modules/>

# This file is part of qudi.

# Qudi is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Qudi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with qudi.
# If not, see <https://www.gnu.org/licenses/>.
# """

import ctypes
import time
import numpy as np
import nidaqmx as ni
from nidaqmx._lib import lib_importer  # Due to NIDAQmx C-API bug needed to bypass property getter
from nidaqmx.constants import *

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
    _device_name = ConfigOption(name='device_name', default='dev1', missing='warn')
    
    _trigger_edge = ConfigOption(name='trigger_edge', default="RISING",
                                 constructor=lambda x: ni.constants.Edge[x.upper()], missing='warn')

    _max_channel_samples_buffer = ConfigOption(
        'max_channel_samples_buffer', default=25e6, missing='info')
    _counter_channel = ConfigOption('counter_channel', default = 'ctr0')
    _apd_channel = ConfigOption('apd_channel', default = 'PFI0')
    # TODO: check limits
    _sample_rate_limits = ConfigOption(name='sample_rate_limits', default=(1, 1e6))
    _frame_size_limits = ConfigOption(name='frame_size_limits', default=(1, 1e9))
    _channel_units = ConfigOption(name="digital_channel_units", default = 'c/s')
    _rw_timeout = ConfigOption('read_write_timeout', default=1, missing='nothing')
    _constraints = APDCounterConstraints()
    # Hardcoded data type
    __data_type = np.float64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # NIDAQmx device handle
        self._device_handle = None
        # Task handles for NIDAQmx tasks
        self._di_task_handles = list()
        self._ai_task_handle = None
        self._clk_task_handle = 'Dev1/port0'
        # nidaqmx stream reader instances to help with data acquisition
        self._di_readers = list()
        self._ai_reader = None

        # List of all available counters and terminals for this device
        self.__all_counters = tuple()
        self.__all_digital_terminals = tuple()


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
            print(self._device_name+'/'+self._counter_channel)
            raise ValueError(
                f'Counter channel "{self._counter_channel}" not found in list of available counters: '
                f'{counters}\nActivation of NIXSeriesInStreamer failed!'
            )
            
        self._counter_channel_name = self._device_name+'/'+self._counter_channel

        terminals = self._device_handle.terminals
        if '/'+self._device_name+'/'+self._apd_channel.upper() not in terminals:
            print('/'+self._device_name+'/'+self._apd_channel)
            raise ValueError(
                f'APD channel "{self._apd_channel}" not found in list of available terminals: '
                f'{terminals}\nActivation of NIXSeriesInStreamer failed!'

            )
        self._apd_channel_name = '/'+self._device_name+'/'+self._apd_channel

        # Make sure the ConfigOptions have correct values and types
        # (ensured by FiniteSamplingInputConstraints)
        # self._sample_rate_limits = self._constraints.sample_rate_limits
        # self._frame_size_limits = self._constraints.frame_size_limits
        # self._channel_units = self._constraints.channel_units

        # initialize default settings
        # self._sample_rate = self._constraints.max_sample_rate
        # TODO: Get real sample rate limits depending on specified channels (see NI FSIO), or include in "ni helper".
        self._frame_size = 0

    def on_deactivate(self):
        """ Shut down the NI card.
        """
        self.terminate_all_tasks()
        return
    
    def set_up_clock(self, sampling_rate):
        self.sample_clock = ni.Task()
        self.sample_clock.di_channels.add_di_chan(self._clk_task_handle)
        self.sample_clock.timing.cfg_samp_clk_timing(rate= sampling_rate, sample_mode = AcquisitionType.CONTINUOUS)
        self.sample_clock.control(TaskMode.TASK_COMMIT)

    def set_up_counter(self,
                       counter_channel,
                       source,
                       sampling_rate):
        self.read_task = ni.Task()
        self.read_task.ci_channels.add_ci_count_edges_chan(
                                    self.,
                                    edge=self._trigger_edge,
                                    initial_count=0,
                                    count_direction=CountDirection.COUNT_UP)
        self.read_task.ci_channels.all.ci_count_edges_term = "/"+ self._device_handle + source
        
        self.read_task.timing.cfg_samp_clk_timing(sampling_rate, source="/" + self._device_handle + "di/SampleClock",
            active_edge=Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)

        # read_task.in_stream.input_buf_size = 120000000
        
        self.read_task.triggers.arm_start_trigger.trig_type = TriggerType.DIGITAL_EDGE
        self.read_task.triggers.arm_start_trigger.dig_edge_edge = self._trigger_edge
        self.read_task.triggers.arm_start_trigger.dig_edge_src = "/"+ self._device_handle+"di/SampleClock"

    def run_counter(self, read_task, clock_task, number_samples, acq_time):
        number_samples = int(number_samples)
        reader = ni.stream_readers.CounterReader(read_task.in_stream)
        try:
            clock_task.start()
            read_task.start()
        except: print('')
        
        data_array = np.empty(number_samples, dtype = np.uint32)
        
        reader.read_many_sample_uint32(data_array,
        number_of_samples_per_channel=number_samples, timeout=0.001*acq_time)
        return data_array

    def get_counter(self, sampling_rate, acq_time, number_samples, clock_port, count_dev, count_port, edge_type, trig_edge_type, trig_type, pfi_port, close=False):

        counter = self.run_counter(read_task, clock_task, number_samples, acq_time)

        self.stop_counter(read_task, clock_task)

        time = acq_time * 0.001
        # print(counter)
        countrate = counter[-1] /time
        print(countrate)
        if close==True:
            close_counter(read_task, clock_task)

        return countrate
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

    def close_counter(self):
        self.terminate_all_tasks()
        self.reset_hardware()

class NiInitError(Exception):
    pass