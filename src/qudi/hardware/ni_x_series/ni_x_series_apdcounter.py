
import ctypes
import time
import numpy as np
import nidaqmx as ni
from nidaqmx._lib import lib_importer  # Due to NIDAQmx C-API bug needed to bypass property getter
from nidaqmx.stream_readers import  CounterReader

from qudi.util.mutex import RecursiveMutex
from qudi.core.configoption import ConfigOption
from qudi.util.helpers import natural_sort
from qudi.interface.apd_counter_interface import APDCounterInterface, APDCounterConstraints
import nidaqmx.constants


class NIXSeriesAPDCounter(APDCounterInterface):
    
    # config options
    _device_name = ConfigOption(name='device_name', default='Dev1', missing='warn')
    
    _physical_sample_clock_output = ConfigOption(name='sample_clock_output', default=None)
    _edge_type = ConfigOption(name='edge_type', default="RISING",
                                constructor=lambda x: ni.constants.Edge[x.upper()], missing='warn')
    _count_offset = ConfigOption(name='count_offset', default=0)
    _count_direction = ConfigOption(name = 'count_direction', default = 'COUNT_UP', 
                                    constructor=lambda x: nidaqmx.constants.CountDirection[x.upper()], missing='warn' )
    _max_channel_samples_buffer = ConfigOption(
        'max_channel_samples_buffer', default=1e6, missing='info')
    _counter_channel = ConfigOption('counter_channel', default = 'ctr0')
    _apd_channel = ConfigOption('apd_channel', default = 'PFI0')
    # TODO: check limits
    _sample_rate_limits = ConfigOption(name='sample_rate_limits', default=(1, 1e6))
    _frame_size_limits = ConfigOption(name='frame_size_limits', default=(1, 1e9))

    _rw_timeout = ConfigOption('read_write_timeout', default=.1, missing='nothing')

    # Hardcoded data type
    __data_type = np.uint32

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._device_name = self._device_name.lower()
        self._apd_channel = self._apd_channel.lower()
        self._counter_channel = self._counter_channel.lower()
        # NIDAQmx device handle
        self._device_handle = None
        # Task handles for NIDAQmx tasks

        # nidaqmx stream reader instances to help with data acquisition


        # List of all available counters and terminals for this device
        self.__all_counters = tuple()


        # currently active channels
        self.__active_channels = [('counter', self._counter_channel.lower()), ('apd' , self._apd_channel.lower())]

        self._thread_lock = RecursiveMutex()
        self._sample_rate = -1
        self._frame_size = -1
        self._constraints = None
        
    
    def init_counter_task(self):
        try:
            self.counter_task = ni.Task()
            
            channel = self.counter_task.ci_channels.add_ci_count_edges_chan(self._device_name+'/'+self._counter_channel, 'counter channel', edge = self._edge_type, initial_count=self._count_offset, count_direction=self._count_direction)
            channel.ci_count_edges_term = '/'+self._device_name+'/'+self._apd_channel
        except: print('already initialized')

    def start_counter_task(self):
        self.counter_task.start()
        self.reader = CounterReader(self.counter_task.in_stream)
        return self.counter_task, self.reader

    def close_counter(self):

        daq_device=nidaqmx.system.system.System.local().devices[self._device_name]

        self.counter_task.stop()
        daq_device.reset_device()
        return 0

        
    
    def acquire_counts(self, samples, timing):
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
            counter_task, reader = self.start_counter_task()
            data = np.zeros(samples, dtype=self.__data_type)
            try:
                reader.read_many_sample_uint32(data = data, number_of_samples_per_channel=samples, timeout=timing)
            except: -1
            try:
                print('counts/s', data[np.nonzero(data)[-1][-1]]/timing)
            except: print('counts/s', 0)
            counter_task.stop()
            return data[np.nonzero(data)[-1][-1]]
