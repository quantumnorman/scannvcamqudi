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



class APDCounterInterfaceSimple(Base):
    """ Define the controls for a slow counter."""

    @abstractmethod
    def setup_clock(self, sampling_rate):
        pass

    @abstractmethod
    def setup_read(self, sampling_rate):
        pass

    @abstractmethod
    def start_tasks(self):
        pass

    @abstractmethod
    def acquire_frame(self, data_array):
        pass

    def init_all(self):
        pass

    @abstractmethod
    def get_countrate(self):
        pass
    @abstractmethod
    def stop_tasks(self):
        pass

    @abstractmethod
    def close_tasks(self):
        pass