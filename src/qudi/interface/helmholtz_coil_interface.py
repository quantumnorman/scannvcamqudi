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
    def get_magnet_state(self):
        pass

    @abstractmethod
    def setfield(self, bnorm, phi, theta):
        pass

    def getfield(self):
        pass

class HelmholtzCoilRelayInterface(Base):
    @abstractmethod
    def _readline(self):
        pass

    @abstractmethod
    def _write(self, command):
        pass

    @abstractmethod
    def _flush(self):
        pass

    @abstractmethod
    def _sendBreak(self):
        pass