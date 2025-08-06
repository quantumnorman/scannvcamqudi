from qudi.core.module import GuiBase
from qudi.core.connector import Connector
from qudi.core.statusvariable import StatusVar
from qudi.core.configoption import ConfigOption
from qudi.util.widgets.fitting import FitConfigurationDialog, FitWidget
import qudi.gui.anc300.piezostepper_mainwindow as piezo_window
# Ensure specialized QMainWindow widget is reloaded as well when reloading this module



class PiezoStepperGUI(GuiBase):
    # """ The GUI class for piezostepper control.

    # Example config for copy-paste:

    #     spectrometer:
    #     module.Class: 'spectrometer.spectrometer_gui.SpectrometerGui'
    #     connect:
    #         spectrometer_logic: 'spectrometerlogic'
    #     options:
    #         progress_poll_interval: 1  # in seconds

    # """

    # declare connectors

    # # StatusVars
    # _delete_fit = StatusVar(name='delete_fit', default=True)
    # _target_x = StatusVar(name='target_x', default=0)

    # # ConfigOptions
    # _progress_poll_interval = ConfigOption(name='progress_poll_interval',
                                        #    default=1,
                                        #    missing='nothing')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self):
        self._mw = piezo_window.PiezoStepperMainWindow()
        self.show()
    
    def show(self):
        self._mw.show()
        self._mw.activateWindow()
        self._mw.raise_()

    def on_deactivate(self):
        return


        
        