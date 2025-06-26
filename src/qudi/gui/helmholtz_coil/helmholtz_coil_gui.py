
import os
from PySide2 import QtCore, QtWidgets, QtGui

from qudi.core.connector import Connector
from qudi.util.colordefs import QudiPalettePale as palette
from qudi.core.module import GuiBase
from qudi.interface.helmholtz_coil_interface import HelmholtzCoilInterface, MagnetState
from qudi.util.paths import get_artwork_dir
from .helmholtzcoil_control_dockwidget import HelmholtzControlDockWidget


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
        layout.addWidget(self.coil_status_label, 0, 1)
        status_bar.addPermanentWidget(widget, 1)
        self.set_magnet_state(MagnetState)
        print(MagnetState.ON)

    
    def set_magnet_state(self, state):
        if state == MagnetState.ON:
            text = 'ON'
        elif state == MagnetState.OFF:
            text = 'OFF'
        elif state == MagnetState.SETTING:
            text = 'SETTING'
        else:
            text = 'unknown'
        self.coil_status_label.setText(text)
        print(MagnetState)


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

    sigFieldMagChanged = QtCore.Signal(float, object)
    sigFieldPhiChanged = QtCore.Signal(float, object)
    sigFieldThetaChanged = QtCore.Signal(float, object)
    sigXPolChanged = QtCore.Signal(object)
    sigYPolChanged = QtCore.Signal(object)
    sigZPolChanged = QtCore.Signal(object)
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
        self._magnet_state_updated(logic.magnet_state)


        # connect control dockwidget signals
        self.control_dock_widget.sigMagnetStateChanged.connect(self._set_magnet_clicked)
        # self.control_dock_widget.current_setpoint_spinbox.editingFinished.connect(
        #     self._current_setpoint_edited
        # )

        # # connect remaining main window actions
        self._mw.action_view_default.triggered.connect(self.restore_default_view)

        # # connect external signals to logic
        self.sigMagnetStateChanged.connect(logic.set_magnet_state)
        # self.sigCurrentChanged.connect(logic.set_current)

        # # connect update signals from logic
        # logic.sigPowerSetpointChanged.connect(
        #     self._power_setpoint_updated, QtCore.Qt.QueuedConnection
        # )
        # logic.sigCurrentSetpointChanged.connect(
        #     self._current_setpoint_updated, QtCore.Qt.QueuedConnection
        # )
        logic.sigMagnetStateChanged.connect(self._magnet_state_updated, QtCore.Qt.QueuedConnection)
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
        # logic = self._laser_logic()
        # logic.sigControlModeChanged.disconnect(self._control_mode_updated)

        # self.control_dock_widget.visibilityChanged.disconnect()
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
    def _set_magnet_clicked(self):
        """ Control mode button group callback. Disables control elements and sends a signal to the
        logic. Logic response will enable the control elements again.

        @param ControlMode mode: Selected ControlMode enum
        """
        # self.control_dock_widget.setbfield_button.setEnabled(False)
        # self.sigMagnetStateChanged.emit(self._coil_logic().magnet_state)
        return

    @QtCore.Slot(object)
    def _magnet_state_updated(self, state):
        # self.control_dock_widget.setbfield_button.setEnabled(True)
        # self._coil_logic().magnet_state_change()
        return


    # @QtCore.Slot()
    # def _current_setpoint_edited(self):
    #     """ ToDo: Document
    #     """
    #     value = self.control_dock_widget.current_setpoint_spinbox.value()
    #     self.control_dock_widget.current_slider.setValue(value)
    #     self.sigCurrentChanged.emit(value, self.module_uuid)

    # @QtCore.Slot(float, object)
    # def _current_setpoint_updated(self, value, caller_id):
    #     if caller_id != self.module_uuid:
    #         self.control_dock_widget.current_setpoint_spinbox.setValue(value)
    #         self.control_dock_widget.current_slider.setValue(value)