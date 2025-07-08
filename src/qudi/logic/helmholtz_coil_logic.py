import time
import numpy as np
from PySide2 import QtCore

from qudi.util.mutex import Mutex
from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.module import LogicBase
from qudi.interface.helmholtz_coil_interface import MagnetState



class HelmholtzCoilLogic(LogicBase):
    _current = Connector(name="current_source", interface = "HelmholtzCoilInterface")
    _relay = Connector(name="relay_source", interface="HelmholtzCoilRelayInterface")
    _fieldcoeffs = ConfigOption("field_coeffs")
    _current_min = ConfigOption("current_min", -3)
    _current_max = ConfigOption("current_max", 3)
    _voltage_max = ConfigOption("voltage_max", 3)    
    # sigFieldMagSetChanged = QtCore.Signal(float, object)
    # sigFieldPhiSetChanged = QtCore.Signal(float, object)
    # sigFieldThetaSetChanged = QtCore.Signal(float, object)
    sigMagnetStateChanged = QtCore.Signal(object)
    # sigMagnetFieldChanged = QtCore.Signal(object)
    sigFieldReadChanged = QtCore.Signal(object, object)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_lock = Mutex()
        self._last_magnet_state = None
        self._last_magnet_field = [None, None, None]
    

    def on_activate(self):
        self.current = self._current()
        self.relay = self._relay()
        self._last_magnet_state = self.current.get_magnet_state()

    def on_deactivate(self):
        self.stop_query_loop()


    def setpolarity(self, x,y,z):

        "Determines the 3-bit polarity string to send to the Arduino Relay. 0 for positive polarity, 1 for negative polarity"
        pols = []
        if abs(x) == x: pols.append(0)
        else: pols.append(1)

        if abs(y) == y: pols.append(0)
        else: pols.append(1)

        if abs(z) == z: pols.append(0)
        else: pols.append(1)

        pols = "".join(str(pol) for pol in pols)
        d = self.relay.setbfieldrelaypol(pols)
        d = self.relay.getbfieldrelaypol()
        pols = d[::2]
        print(pols)
        return d, pols
    
    @QtCore.Slot(float, float, float, float)
    def setfield(self, bnorm, phi, theta, wait):
        print("setting field starting now")
        if self.magnet_state != MagnetState.ON:
            self._write("OUTP:STAT:ALL ON")
            print('magnet state check')
            self.magnet_state = MagnetState.ON
        if MagnetState == 3:
            print("Error with magnet state!")
        else: 
            print("Magnet on")

        x,y,z, errs = self.fieldtocurrent(bnorm, phi, theta) ## Step 1 Convert input B field values to current values
        # print("Any clipped currents? ", errs)
        # print("x,y,z", x, y, z)

        d,pols = self.setpolarity(x,y,z) ##Step 2 set the Arduino relay polarities
        # print("String sent to Arduino relay and string read from Arduino: ", d, pols) ###d and pols should be the same (pols is what you're trying to set, d is what is read out)

        s = self.current.write3channels("CURR", x,y,z) ##Step 3 sets the current (using absolute values since this is setting to the Keithley and the Arduino will deal with the polarities)
        print("String sent to ketihley: ", s)
        time.sleep(wait*0.001)
        dat = self.current.query3channels("CURR")
        print("Final readings from Keithley: ", dat)
        currents, field = self.getfield(dat, pols)
        print(currents, field)
        self.sigFieldReadChanged.emit(currents, field)
        print("signal emitted")
        return currents, field


    def getfield(self, dat, d):
        pols = []
        for i in d:
            if i == 0: pols.append(1)
            else: pols.append(-1)
        print(pols)
        self.xcurrent_read = pols[0] * float(dat["X"]["CURR"])
        self.ycurrent_read = pols[1] * float(dat["Y"]["CURR"])
        self.zcurrent_read = pols[2] * float(dat["Z"]["CURR"])
        print(self.xcurrent_read, self.ycurrent_read, self.zcurrent_read)
        self.bnorm_read, self.phi_read, self.theta_read = self.currenttofield(self.xcurrent_read, self.ycurrent_read, self.zcurrent_read) ##Convert read values to field values

        print([self.xcurrent_read, self.ycurrent_read, self.zcurrent_read],  [self.bnorm_read, self.phi_read, self.theta_read], d)

        return [self.xcurrent_read, self.ycurrent_read, self.zcurrent_read],  [self.bnorm_read, self.phi_read, self.theta_read]


    def currenttofield(self, x1, y1, z1):
        "Converts the x,y,z current input values into bnorm, phi, and theta values using calibration parameters in fieldcoeffs"
        x = self.calibcurrtobfield(self._fieldcoeffs["X"], x1)
        print('x', x)
        y = self.calibcurrtobfield(self._fieldcoeffs["Y"], y1)
        print('y', y)
        z = self.calibcurrtobfield(self._fieldcoeffs["Z"], z1)
        print('z', z)
        bnorm = np.sqrt(x**2 + y**2 + z**2)
        print('b', bnorm)
        phi1= y/x
        print(phi1)
        phi = np.arctan(phi1)
        print(phi)
        theta = np.arccos(z/bnorm)
        
        print(theta)
        print(x,y,z, bnorm, phi, theta)

        return bnorm, phi, theta

    def calibcurrtobfield(self, fieldcoeffs, x):
        "Calibrates the current to field conversion using parameters in fieldcoeffs"
        return (x * fieldcoeffs[0]) + fieldcoeffs[1]
    
    def calibbfieldtocurr(self, fieldcoeffs, x):
        "Calibrates the field to current conversion using parameters in fieldcoeffs"
        y = (x - fieldcoeffs[1])/fieldcoeffs[0]
        if self._current_min<=y<=self._current_max:
            return y, None
        elif y>self._current_max: return self._current_max, "Current clipped to " + str(self._current_max) + "A"
        elif y<self._current_min: return self._current_min, "Current clipped to " + str(self._current_min) + "A"

    def fieldtocurrent(self, B, phi, theta):
        "Converts the Bnorm, phi, and theta input values into x, y, z, current values using calibration parameters in fieldcoeffs"
        # print(self._fieldcoeffs['X'])
        x, errx = self.calibbfieldtocurr(self._fieldcoeffs['X'], B * np.sin(theta)* np.cos(phi))
        y, erry = self.calibbfieldtocurr(self._fieldcoeffs['Y'], B * np.sin(theta) * np.sin(phi))
        z, errz = self.calibbfieldtocurr(self._fieldcoeffs['Z'], B * np.cos(theta))
        print(x,y,z,)

        if errx==erry==errz==None: return x,y,z, None
        
        else: return x,y,z, [errx, erry, errz]
        

    @property
    def magnet_state(self):
        with self._thread_lock:
            self._last_magnet_state = self.current.get_magnet_state()
            print ("get magnet state value: ", self.current.get_magnet_state())
            return self._last_magnet_state

    @property
    def magnet_setpoint(self):
        with self._thread_lock:
            self._last_magnet_setpoint = self.current.get_field()
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
                # self.__timer.start()

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
                # self.__timer.stop()
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
                    self.current.set_magnet_state(state)
                except:
                    self.log.exception('Error while setting magnet state mode:')
            self.sigMagnetStateChanged.emit(self.magnet_state)

    @magnet_setpoint.setter
    def magnet_setout(self, bnorm, phi, theta):
        self.set_field(bnorm, phi, theta)

    @magnet_state.setter
    def magnet_state(self, state):#
        self.set_magnet_state(state)

    @QtCore.Slot(float, float, float)
    def set_field(self, bnorm, phi, theta):
        # with self._thread_lock:
        currents, field = self.setfield(bnorm, phi, theta)
        # self.sigFieldReadChanged.emit([currents, field])

        return currents, field


    @QtCore.Slot()
    def magnet_state_change(self):
        coil = self._current()
        magnet_state = coil.get_magnet_state()
        if magnet_state != self._last_magnet_state:
            self._last_magnet_state = magnet_state
            self.sigMagnetStateChanged.emit(self._last_magnet_state)

