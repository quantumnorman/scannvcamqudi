from abc import abstractmethod
from qudi.core.module import Base

class HelmholtzCoilRelayInterface(Base):

    @abstractmethod
    def setbfieldrelaypol(self, pols):
        pass

    @abstractmethod
    def getbfieldrelaypol(self):
        pass