
from abc import abstractmethod
from qudi.core.module import Base



class PiezoStepperInterface(Base):
    """ Define the controls for a piezo stepper."""
    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    # @abstractmethod
    # def __init__(self, config):
    #     pass

    # @abstractmethod
    # def get_param(self, channel, param):
    #     pass

    @abstractmethod
    def set_param(self, channel, param, value):
        pass

    # def axis_status(self, channel):
    #     pass

    @abstractmethod
    def step(self, channel, value):
        pass

    @abstractmethod
    def jog(self, channel, direction):
        pass

    @abstractmethod
    def stop(self,axis="all"):
        pass

    @abstractmethod
    def disable_axis(self, axis="all"):
        pass

    @abstractmethod
    def enable_axis(self, axis="all"):
        pass

    @abstractmethod
    def is_enabled(self, axis):
        pass
