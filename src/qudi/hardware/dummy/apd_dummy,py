import ctypes
import time
import numpy as np

from qudi.util.mutex import RecursiveMutex
from qudi.core.configoption import ConfigOption
from qudi.util.helpers import natural_sort
from qudi.interface.apd_counter_interface import APDCounterInterface


class APDDummy(APDCounterInterface):
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
        return 0

    def start_counter_task(self):
        return 0, 0

    def close_counter(self):
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
            data = np.random.randint(low=0, high = 200, size=samples, dtype=self.__data_type)
            
            return data[np.nonzero(data)[-1][-1]]
    
    @property
    def active_channels(self):
        return self.__active_channels