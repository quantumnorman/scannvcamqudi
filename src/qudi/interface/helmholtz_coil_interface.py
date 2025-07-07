from enum import IntEnum
from abc import abstractmethod
from qudi.core.module import Base

class MagnetState(IntEnum):
    OFF = 0
    ON = 1
    SETTING = 2
    UNKNOWN=  3

class HelmholtzCoilInterface(Base):
    @abstractmethod
    def _write(self):
        pass
    
    @abstractmethod
    def _query(self):
        pass

    @abstractmethod
    def activatemagnet(self):
        pass

    @abstractmethod
    def write3channels(self, TYPE, x, y, z):
        pass

    @abstractmethod
    def querychannel(self, channel, type):
        pass

    @abstractmethod
    def query3channels(self, type):
        pass

    @abstractmethod
    def set_magnet_state(self, state):
        pass
    
    @abstractmethod
    def get_magnet_state(self):
        pass
