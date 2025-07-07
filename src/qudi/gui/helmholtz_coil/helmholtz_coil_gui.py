
import os
from PySide2 import QtCore, QtWidgets, QtGui
from qudi.core.connector import Connector
from qudi.util.colordefs import QudiPalettePale as palette
from qudi.core.module import GuiBase
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState
from qudi.interface.helmholtz_coil_relay_interface import HelmholtzCoilRelayInterface
from qudi.util.paths import get_artwork_dir
from .helmholtzcoil_control_dockwidget import HelmholtzControlDockWidget
from qtwidgets import Toggle

class HelmholtzCoilMainWindow(QtWidgets.QMainWindow):
    """ The main window for the Helmholtz Coil """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('qudi: Helmholtz Coil')
        
        # Create extra info dialog
        self.extra_info_dialog = QtWidgets.QDialog(self, QtCore.Qt.Dialog)
        self.extra_info_dialog.setWindowTitle('Coil Info')
        self.extra_info_label = QtWidgets.QLabel()
        self.extra_info_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        extra_info_button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        extra_info_button_box.setCenterButtons(True)
        extra_info_button_box.accepted.connect(self.extra_info_dialog.accept)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.extra_info_label)
        layout.addWidget(extra_info_button_box)
        self.extra_info_dialog.setLayout(layout)
        layout.setSizeConstraint(layout.SetFixedSize)


        menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(menu_bar)

        menu = menu_bar.addMenu('File')
        self.action_close = QtWidgets.QAction('Close')
        path = os.path.join(get_artwork_dir(), 'icons', 'application-exit')
        self.action_close.setIcon(QtGui.QIcon(path))
        self.action_close.triggered.connect(self.close)
        menu.addAction(self.action_close)

        menu = menu_bar.addMenu('View')
        self.action_view_controls = QtWidgets.QAction('Show Controls')
        self.action_view_controls.setCheckable(True)
        self.action_view_controls.setChecked(True)
        menu.addAction(self.action_view_controls)
        menu.addSeparator()
        self.action_view_default = QtWidgets.QAction('Restore Default')
        menu.addAction(self.action_view_default)

        status_bar = QtWidgets.QStatusBar(self)
        status_bar.setStyleSheet('QStatusBar::item { border: 0px}')
        self.setStatusBar(status_bar)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(1, 1)
        widget.setLayout(layout)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(12)
        label = QtWidgets.QLabel('Coil Status:')
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        layout.addWidget(label, 0, 0)

        self.coil_status_label = QtWidgets.QLabel('???')
        self.coil_status_label.setFont(font)
        self.field_onoff_toggle = Toggle()


        layout.addWidget(self.coil_status_label, 0, 1)
        layout.addWidget(self.field_onoff_toggle, 0, 2)
        status_bar.addPermanentWidget(widget, 1)
        


    
    def set_magnet_state(self, state):
        print("state for set magnet state from gui: ", state)
        if state == MagnetState.ON:
            text = 'ON'
            self.field_onoff_toggle.setChecked(True) 
        elif state == MagnetState.OFF:
            text = 'OFF'
            self.field_onoff_toggle.setChecked(False)

        self.coil_status_label.setText(text)


class HelmholtzCoilGui(GuiBase):
    """ Main gui class for controlling a laser.

    Example config for copy-paste:

    laser_gui:
        module.Class: 'laser.laser_gui.LaserGui'
        connect:
            laser_logic: laser_logic
    """

    # declare connectors
    _coil_logic = Connector(name='helmholtz_coil_logic', interface='HelmholtzCoilLogic')


    sigFieldSetPointChanged = QtCore.Signal(float, float, float, float)

    sigMagnetStateChanged = QtCore.Signal(object)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._mw = None
        self.control_dock_widget = None
        self.output_graph_dock_widget = None


    def on_activate(self):
        """ Definition and initialisation of the GUI plus staring the measurement.
        """
        logic = self._coil_logic()
        logic.start_query_loop()

        # initialize data and start the laser data query loop
        #####################
        # create main window
        self._mw = HelmholtzCoilMainWindow()
        self._mw.setDockNestingEnabled(True)
        # set up dock widgets
        self.control_dock_widget = HelmholtzControlDockWidget()
        self.control_dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self._mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_dock_widget)

        self.control_dock_widget.visibilityChanged.connect(self._mw.action_view_controls.setChecked)
        self._mw.action_view_controls.triggered[bool].connect(self.control_dock_widget.setVisible)

        self.restore_default_view()

        #Initialize data from logic
        # self._magnet_state_updated(logic.magnet_state)

        self._mw.field_onoff_toggle.stateChanged.connect(self.on_checked_box)
        self.control_dock_widget.setbfield_button.clicked.connect(self._set_bfield_clicked)

        # connect control dockwidget signals
        # self.control_dock_widget.sigMagnetStateChanged.connect(self._set_magnet_clicked)
        # self.control_dock_widget.setbfield_button.clicked.connect(self._set_magnet_clicked)
        # self.control_dock_widget.current_setpoint_spinbox.editingFinished.connect(
        #     self._current_setpoint_edited
        # )

        # # connect remaining main window actions
        self._mw.action_view_default.triggered.connect(self.restore_default_view)

        # # connect external signals to logic
        self.sigMagnetStateChanged.connect(logic.set_magnet_state)
        self.sigFieldSetPointChanged.connect(logic.setfield, QtCore.Qt.QueuedConnection)
        logic.sigFieldReadChanged.connect(self.on_updated_fieldscurrents, QtCore.Qt.QueuedConnection)
        # self.sigCurrentChanged.connect(logic.set_current)

        # # connect update signals from logic
        # logic.sigPowerSetpointChanged.connect(
        #     self._power_setpoint_updated, QtCore.Qt.QueuedConnection
        # )
        # logic.sigCurrentSetpointChanged.connect(
        #     self._current_setpoint_updated, QtCore.Qt.QueuedConnection
        # )
        # logic.sigMagnetStateChanged.connect(self._magnet_state_updated, QtCore.Qt.QueuedConnection)
        # logic.sigLaserStateChanged.connect(self._laser_state_updated, QtCore.Qt.QueuedConnection)
        # logic.sigShutterStateChanged.connect(
        #     self._shutter_state_updated, QtCore.Qt.QueuedConnection
        # )
        # logic.sigDataChanged.connect(self._data_updated, QtCore.Qt.QueuedConnection)

        # self.show()


    def on_deactivate(self):
        """ Deactivate the module properly.
        """
        self._mw.close()
        # # disconnect all signals
        # logic.sigControlModeChanged.disconnect(self._control_mode_updated)
        logic = self._coil_logic()
        self.control_dock_widget.visibilityChanged.disconnect()
        # self._mw.action_view_controls.triggered.disconnect()
        # self.control_dock_widget.sigControlModeChanged.disconnect()
        # self._mw.action_view_default.triggered.disconnect()
        # self.sigCurrentChanged.disconnect()
        # self.sigControlModeChanged.disconnect()

    def show(self):
        """Make window visible and put it above all other windows.
        """
        self._mw.show()
        self._mw.raise_()
        self._mw.activateWindow()


    def restore_default_view(self):
        """ Restore the arrangement of DockWidgets to the default
        """
        # Show any hidden dock widgets
        self.control_dock_widget.show()

        # Arrange docks widgets
        self._mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_dock_widget)


    @QtCore.Slot(object)
    def _set_bfield_clicked(self):
        """ Control mode button group callback. Disables control elements and sends a signal to the
        logic. Logic response will enable the control elements again.

        @param ControlMode mode: Selected ControlMode enum
        """
        # self.control_dock_widget.setbfield_button.setEnabled(False)
        print("clicked")
        
        bnorm_set= float(self.control_dock_widget.bnorm_set_lineedit.text())
        phi_set = float(self.control_dock_widget.phi_set_lineedit.text())
        theta_set = float(self.control_dock_widget.theta_set_lineedit.text())
        wait_set = float(self.control_dock_widget.lineEdit_4.text())

        self.sigFieldSetPointChanged.emit(bnorm_set, phi_set, theta_set, wait_set)
        print("emitted")
        # currents, field = self._coil_logic().set_field(0, 0, 0)
        # self.control_dock_widget.bnorm_read.setText(str(field[0]))
        # self.control_dock_widget.phi_read.setText(str(field[1]))
        # self.control_dock_widget.theta_read.setText(str(field[2]))
        # self.control_dock_widget.currentx_read.setText(str(currents[0]))
        # self.control_dock_widget.currenty_read.setText(str(currents[1]))
        # self.control_dock_widget.currentz_read.setText(str(currents[2]))

        return

    @QtCore.Slot(object, object)
    def on_updated_fieldscurrents(self, currents, field):
        self.control_dock_widget.bnorm_read.setText(str(field[0]))
        self.control_dock_widget.phi_read.setText(str(field[1]))
        self.control_dock_widget.theta_read.setText(str(field[2]))

        self.control_dock_widget.currentx_read.setText(str(currents[0]))
        self.control_dock_widget.currenty_read.setText(str(currents[1]))
        self.control_dock_widget.currentz_read.setText(str(currents[2]))

    # def _magnet_state_updated(self, state):
    #     self._mw.set_magnet_state(state)
    #     # self.control_dock_widget.setbfield_button.setEnabled(True)
    #     # self._coil_logic().magnet_state_change()
    #     if state == MagnetState.ON:
    #         self.control_dock_widget.setbfield_button.setEnabled(True)
        
    #     elif state == MagnetState.OFF:
    #         self.control_dock_widget.setbfield_button.setEnabled(False)
    #     else:
    #         print("error setting magnet state")
    #     return

    @QtCore.Slot()
    def on_checked_box(self, state):
        if state == 2:
            self._mw.coil_status_label.setText("ON")
            self.control_dock_widget.setbfield_button.setEnabled(True)
            self._coil_logic().set_magnet_state(MagnetState.ON)
            

        if state == 0:
            self._mw.coil_status_label.setText("OFF")
            self._coil_logic().set_magnet_state(MagnetState.OFF)
            # self._magnet_state_updated(MagnetState.OFF)
            self.control_dock_widget.setbfield_button.setEnabled(False)