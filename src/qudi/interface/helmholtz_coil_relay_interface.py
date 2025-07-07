from abc import abstractmethod
from qudi.core.module import Base

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

    @abstractmethod
    def setbfieldrelaypol(self, pols):
        pass

    @abstractmethod
    def getbfieldrelaypol(self):
        pass