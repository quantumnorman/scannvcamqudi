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
from nidaqmx import stream_readers

from qudi.util.mutex import RecursiveMutex
from qudi.core.configoption import ConfigOption
from qudi.util.helpers import natural_sort
from qudi.interface.apd_counter_interface_simple import APDCounterInterfaceSimple


class NIXSeriesAPDCounter(APDCounterInterfaceSimple):
#     """
#     A National Instruments device that can detect and count digital pulses and measure analog
#     voltages in a finite sampling way.

#     !!!!!! NI USB 63XX, NI PCIe 63XX and NI PXIe 63XX DEVICES ONLY !!!!!!

#     See [National Instruments X Series Documentation](@ref nidaq-x-series) for details.

#     Example config for copy-paste:

#     ni_single_counter:
#         module.Class: 'ni_x_series.ni_x_series_single_counter.NIXSeriesFiniteSamplingInput'
#         options:
#             device_name: 'Dev1'
#             counter_channel: 'ctr0'
#             apd_channel: 'PFI0'
#             trigger_edge: RISING  # optional
#             count_offset: 0 # optional
#             count_direction: COUNT_UP # optional
#     """
    _clock_channel = ConfigOption("clock channel", default = "Dev1/port0")
    _sampling_rate = ConfigOption("sampling rate", default = 100000)
    _counter_channel = ConfigOption("counter channel", default = "Dev1/ctr0")
    _edge_type = ConfigOption("edge type", default = Edge.RISING)
    _trig_type = ConfigOption("trigger type", default = TriggerType.DIGITAL_EDGE)
    _pfi_channel = ConfigOption("apd source channel", default= "/Dev1/PFI0")
    _acq_time = ConfigOption("acquisition time", default=1)
    last_value = 0
    _device_handle = ConfigOption("device", default = "Dev1")
#     # config options
    _initial_count = 0

    _max_channel_samples_buffer = ConfigOption(
        'max_channel_samples_buffer', default=25e6, missing='info')
#     # TODO: check limits
#     _sample_rate_limits = ConfigOption(name='sample_rate_limits', default=(1, 1e6))
#     _frame_size_limits = ConfigOption(name='frame_size_limits', default=(1, 1e9))
#     _channel_units = ConfigOption(name="digital_channel_units", default = 'c/s')
#     _rw_timeout = ConfigOption('read_write_timeout', default=1, missing='nothing')
#     _constraints = APDCounterConstraints()
#     # Hardcoded data type
    __data_type = np.float64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#         # NIDAQmx device handle
#         self._device_handle = None
#         # Task handles for NIDAQmx tasks
#         self._di_task_handles = list()
#         self._ai_task_handle = None
#         self._clk_task_handle = 'Dev1/port0'
#         # nidaqmx stream reader instances to help with data acquisition
#         self._di_readers = list()
#         self._ai_reader = None

#         # List of all available counters and terminals for this device
#         self.__all_counters = tuple()
#         self.__all_digital_terminals = tuple()


#         # currently active channels
#         self.__active_channels = {'counter' : self._counter_channel.lower(), 'apd' : self._apd_channel.lower()}

#         self._thread_lock = RecursiveMutex()
#         self._sample_rate = -1
#         self._frame_size = -1
#         self._constraints = None

    def on_activate(self):
        self.init_all()


    def on_deactivate(self):
        self.stop_tasks()
        self.close_tasks()
        return
    

#     pass

    def setup_clock(self):
        self.clock_task = ni.Task()
        self.clock_task.di_channels.add_di_chan(self._clock_channel)
        self.clock_task.timing.cfg_samp_clk_timing(rate= self._sampling_rate, sample_mode = AcquisitionType.CONTINUOUS)
        self.clock_task.control(TaskMode.TASK_COMMIT)

    def setup_read(self):
        self.read_task = ni.Task()
        self.read_task.ci_channels.add_ci_count_edges_chan(
                                    self._counter_channel,
                                    edge=self._edge_type,
                                    initial_count=self._initial_count,
                                    count_direction=CountDirection.COUNT_UP)
        self.read_task.ci_channels.all.ci_count_edges_term = self._pfi_channel
        
        self.read_task.timing.cfg_samp_clk_timing(self._sampling_rate, source="/" + self._device_handle + "/di/SampleClock",
            active_edge=Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)

        # read_task.in_stream.input_buf_size = 120000000
        
        self.read_task.triggers.arm_start_trigger.trig_type = self._trig_type
        self.read_task.triggers.arm_start_trigger.dig_edge_edge = self._edge_type
        self.read_task.triggers.arm_start_trigger.dig_edge_src = "/"+ self._device_handle+"/di/SampleClock"

        return self.read_task

    def start_tasks(self): 
            self.clock_task.start()
            self.read_task.start()
            self.reader = ni.stream_readers.CounterReader(self.read_task.in_stream)

    def acquire_frame(self, data_array):
        
        self.reader.read_many_sample_uint32(data_array, timeout=0.001*self._acq_time)
        return data_array

    def init_all(self):
        self.setup_clock()
        self.setup_read()
        self.start_tasks()

    def get_countrate(self):
        # self.run_counter()
        # counts = self.data_array[-1] - self.last_value

        # time = self._acq_time * 0.001
        # # print(counter)
        # self.countrate=counts/time
        # print(self.countrate)
        return self.data_array
    
    def stop_tasks(self):
        self.clock_task.stop()
        self.read_task.stop()
        
    def close_tasks(self):
        self.clock_task.close()
        self.read_task.close()
        