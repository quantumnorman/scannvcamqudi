# -*- coding: utf-8 -*-

"""
This file contains the Qudi Interface for Slow counter.

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


from abc import abstractmethod
from qudi.core.module import Base



class APDCounterInterface(Base):
    """ Define the controls for a slow counter."""


    @abstractmethod
    def init_counter_task(device_name, 
                          counter_channel, 
                          apd_channel, 
                          edge_type, 
                          count_offset, 
                          count_dir):
        """ Configures the actual counter with a given APD trigger channel.
        
        @param str device_name: name of device connected to APD
        @param str counter_channel: counter channel used for counting (defaults to 'ctr0')
        @param str apd_channel: specifies the channel the APD is connected to, triggers the count channel to increase
        @param boolean edge_type: optional, defaults as TRUE for RISING edge trigger
        @param int count_offset: optional, defaults as 0 for no starting count offset
        @param boolean count_dir: optional, defaults as TRUE for increasing counts
        @return int: error code (0:OK, -1:error)

        """
        pass

    @abstractmethod
    def acquire_counts(self, samples, timing):
        """ Returns the current counts per second of the counter.
        @param NIDAQmx task: counter task to run
        @param int samples: if defined, number of samples to read in one go
        @param float timing: how long to count for before returning data

        @return int: counts registered for length of timing param
        """
        pass


    @abstractmethod
    def close_counter(self):
        """ Closes the counter and cleans up afterwards.

        @return int: error code (0:OK, -1:error)
        """
        pass

    @property
    @abstractmethod
    def active_channels(self):
        pass

class APDCounterConstraints:

    def __init__(self):
        # maximum numer of possible detectors for slow counter
        self.max_detectors = 0
        # frequencies in Hz
        self.min_count_frequency = 5e-5
        self.max_count_frequency = 5e5
        # add CountingMode enums to this list in instances
        self.counting_mode = []

