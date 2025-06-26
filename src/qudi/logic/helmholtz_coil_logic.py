import time
import numpy as np
from PySide2 import QtCore

from qudi.util.mutex import RecursiveMutex
from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.module import LogicBase
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState, HelmholtzCoilRelayInterface

class HelmholtzCoilLogic(LogicBase):
    _current = Connector(name="coil_current_source", interface = "HelmholtzCoilInterface")
    _relay = Connector(name="coil_polarity_relay", interface="HelmholtzCoilRelayInterface")

    # sigFieldMagSetChanged = QtCore.Signal(float, object)
    # sigFieldPhiSetChanged = QtCore.Signal(float, object)
    # sigFieldThetaSetChanged = QtCore.Signal(float, object)
    sigMagnetStateChanged = QtCore.Signal(object)
    # sigMagnetFieldChanged = QtCore.Signal(object)
    # sigXCurrentChanged = QtCore.Signal(object)
    # sigYCurrentChanged = QtCore.Signal(object)
    # sigZCurrentChanged = QtCore.Signal(object)
    # sigFieldMagReadChanged = QtCore.Signal(float, object)
    # sigFieldPhiReadChanged = QtCore.Signal(float, object)
    # sigFieldThetaReadChanged = QtCore.Signal(float, object)


    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_lock = RecursiveMutex()
        self._last_magnet_state = None
        self._last_magnet_field = [None, None, None]

    def on_activate(self):
        self.current = self._current()
        self.relay = self._relay()
        self._query = self.current._query
        self._write = self.current._write
        self._last_magnet_state = self.current.get_magnet_state()

    def on_deactivate(self):
        self.stop_query_loop()

    @property
    def magnet_state(self):
        with self._thread_lock:
            self._last_magnet_state = self.current.get_magnet_state()
            print ("get magnet state value: ", self.current.get_magnet_state())
            print("last magnet state now:", self._last_magnet_state)
            return self._last_magnet_state

    @property
    def magnet_setpoint(self):
        with self._thread_lock:
            self._last_magnet_setpoint = self._current().get_field()
        return self._last_magnet_setpoint

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop.
        Offload self.start_query_loop() from the caller to the module's thread.
        ATTENTION: Do not call this from within thread lock protected code to avoid deadlock (PR #178).
        :return:
        """
        if self.thread() is not QtCore.QThread.currentThread():
            QtCore.QMetaObject.invokeMethod(self,
                                            'start_query_loop',
                                            QtCore.Qt.BlockingQueuedConnection)
            return

        with self._thread_lock:
            if self.module_state() == 'idle':
                self.module_state.lock()
                self.__timer.start()

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop.
        Offload self.stop_query_loop() from the caller to the module's thread.
        ATTENTION: Do not call this from within thread lock protected code to avoid deadlock (PR #178).
        :return:
        """
        if self.thread() is not QtCore.QThread.currentThread():
            QtCore.QMetaObject.invokeMethod(self,
                                            'stop_query_loop',
                                            QtCore.Qt.BlockingQueuedConnection)
            return

        with self._thread_lock:
            if self.module_state() == 'locked':
                self.__timer.stop()
                self.module_state.unlock()

    @QtCore.Slot(object)
    def set_magnet_state(self, state):
        """ Change whether the laser output is controlled by current or power setpoint
        """
        with self._thread_lock:
            if state is MagnetState.UNKNOWN:
                self.log.error(f'Invalid magnet state "{state}" for laser encountered.')
            else:
                try:
                    self._current().set_magnet_state(state)
                except:
                    self.log.exception('Error while setting magnet state mode:')
            self.sigMagnetStateChanged.emit(self.magnet_state)

    @magnet_setpoint.setter
    def magnet_setout(self, bnorm, phi, theta):
        self.set_field(bnorm, phi, theta)

    @magnet_state.setter
    def magnet_state(self, state):#
        self.set_magnet_state(state)

    @QtCore.Slot(float, object)
    def set_field(self, bnorm, phi, theta):
        """ Set laser (diode) current """
        with self._thread_lock:
            self.current.setfield(bnorm, phi, theta)


            self.sigXCurrentChanged.emit(self.xcurrent_read)
            self.sigYCurrentChanged.emit(self.ycurrent_read)
            self.sigZCurrentChanged.emit(self.zcurrent_read)

            self.sigFieldMagSetChanged.emit(self.bnorm_setpoint)
            self.sigFieldPhiSetChanged.emit(self.phi_setpoint)
            self.sigFieldThetaSetChanged.emit(self.theta_setpoint)

            self.sigFieldMagReadChanged.emit(self.bnorm_read)
            self.sigFieldPhiReadChanged.emit(self.phi_read)
            self.sigFieldThetaReadChanged.emit(self.theta_read)

    @QtCore.Slot()
    def magnet_state_change(self):
        coil = self._current()
        magnet_state = coil.get_magnet_state()
        if magnet_state != self._last_magnet_state:
            self._last_magnet_state = magnet_state
            self.sigMagnetStateChanged.emit(self._last_magnet_state)
    # @QtCore.Slot()
    # def _query_loop_body(self):
    #     with self._thread_lock:
    #         if self.module_state() != "locked":
    #             return
    #         coil = self._current()
    #         try:
    #             magnet_state = coil.get_magnet_state()
    #             if magnet_state != self._last_magnet_state:
    #                 self._last_magnet_state = magnet_state
    #                 self.sigMagnetStateChanged.emit(self._last_magnet_state)
    #         except: pass
    #         try:
    #             magnet_field = coil.getfield()
    #             if magnet_field != self._last_magnet_field:
    #                 self._last_magnet_field = magnet_field
    #                 self.sigMagnetFieldChanged.emit(self._last_magnet_field)
    #         except: pass
