from qudi.core.module import GuiBase
from qudi.core.connector import Connector
from qudi.core.statusvariable import StatusVar
from qudi.core.configoption import ConfigOption
from qudi.util.widgets.fitting import FitConfigurationDialog, FitWidget
import qudi.gui.piezo_stepper.piezostepper_mainwindow as piezo_window
# Ensure specialized QMainWindow widget is reloaded as well when reloading this module
from PySide2.QtWidgets import QMainWindow


class PiezoStepperGui(GuiBase):
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
    piezo_logic = Connector(name= "piezo_stepper_logic", interface="PiezoStepperLogic")
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
        self.piezo = self.piezo_logic()

        self._mw.xpos_step_pushButton.clicked.connect(lambda : self.step_button_clicked(1, "+"))
        self._mw.ypos_step_pushButton.clicked.connect(lambda : self.step_button_clicked(2, "+"))
        self._mw.zpos_step_pushButton.clicked.connect(lambda : self.step_button_clicked(3, "+"))
        
        self._mw.xneg_step_pushButton.clicked.connect(lambda : self.step_button_clicked(1, "-"))
        self._mw.yneg_step_pushButton.clicked.connect(lambda : self.step_button_clicked(2, "-"))
        self._mw.zneg_step_pushButton.clicked.connect(lambda : self.step_button_clicked(3, "-"))


        self._mw.xpos_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(1, "+"))
        self._mw.xpos_cont_pushButton.released.connect(self.cont_button_released)
        self._mw.ypos_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(2, "+"))
        self._mw.ypos_cont_pushButton.released.connect(self.cont_button_released)
        self._mw.zpos_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(3, "+"))
        self._mw.zpos_cont_pushButton.released.connect(self.cont_button_released)

        self._mw.xneg_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(1, "-"))
        self._mw.xneg_cont_pushButton.released.connect(self.cont_button_released)
        self._mw.yneg_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(2, "-"))
        self._mw.yneg_cont_pushButton.released.connect(self.cont_button_released)
        self._mw.zneg_cont_pushButton.pressed.connect(lambda: self.cont_button_pressed(3, "-"))
        self._mw.zneg_cont_pushButton.released.connect(self.cont_button_released)

        self._mw.xground_pushButton.clicked.connect(lambda:self.ground_axis(1))
        self._mw.yground_pushButton.clicked.connect(lambda:self.ground_axis(2))
        self._mw.zground_pushButton.clicked.connect(lambda:self.ground_axis(3))


        self._mw.xenable_pushButton.clicked.connect(lambda:self.enable_axis(1))
        self._mw.yenable_pushButton.clicked.connect(lambda:self.enable_axis(2))
        self._mw.zenable_pushButton.clicked.connect(lambda:self.enable_axis(3))

        self._mw.groundall_pushButton.clicked.connect(lambda : self.ground_axis("all"))


        self._mw.xfreq_lineEdit.returnPressed.connect(self.get_params)
        self._mw.xfreq_lineEdit.setText(str(self.piezo.get_param(1, 'frequency')))

        self._mw.yfreq_lineEdit.returnPressed.connect(self.get_params)
        self._mw.yfreq_lineEdit.setText(str(self.piezo.get_param(2, 'frequency')))

        self._mw.zfreq_lineEdit.returnPressed.connect(self.get_params)
        self._mw.zfreq_lineEdit.setText(str(self.piezo.get_param(3, 'frequency')))

        self._mw.xamp_lineEdit.returnPressed.connect(self.get_params)
        self._mw.xamp_lineEdit.setText(str(self.piezo.get_param(1, 'voltage')))
        self._mw.yamp_lineEdit.returnPressed.connect(self.get_params)
        self._mw.yamp_lineEdit.setText(str(self.piezo.get_param(2, 'voltage')))
        self._mw.zamp_lineEdit.returnPressed.connect(self.get_params)
        self._mw.zamp_lineEdit.setText(str(self.piezo.get_param(3, 'voltage')))




        self.show()
    
    def show(self):
        QMainWindow.show(self._mw)

    def on_deactivate(self):
        return

    def step_button_clicked(self, axis, direction):
        self.piezo.step_clicked(axis, direction)


    def cont_button_pressed(self, axis, direction):
        self.piezo.continuous_pressed(axis, direction)
    
    def cont_button_released(self):
        self.piezo.continuous_released()

    def enable_axis(self, axis="all"):
        self.piezo.enable_axis(axis)
        self.get_modes()

    def ground_axis(self, axis="all"):
        self.piezo.ground_axis(axis)
        self.get_modes()


    
    def get_params(self):
        values = {
                    '1' :{
                        'voltage': float(self._mw.xamp_lineEdit.text()), 
                        'frequency' : float(self._mw.xfreq_lineEdit.text())},
                    '2' :{
                        'voltage': float(self._mw.yamp_lineEdit.text()), 
                        'frequency' : float(self._mw.yfreq_lineEdit.text())},
                    '3' :{
                        'voltage': float(self._mw.zamp_lineEdit.text()), 
                        'frequency' : float(self._mw.zfreq_lineEdit.text())},
                  }
        print(values)

        self.update_params(values)

        return values
    
    def update_params(self, vals):
        self.piezo.update_params(vals)
        self._mw.xfreq_lineEdit.setText(str(vals['1']["frequency"]))
        self._mw.yfreq_lineEdit.setText(str(vals['2']["frequency"]))
        self._mw.zfreq_lineEdit.setText(str(vals['3']["frequency"]))

        self._mw.xamp_lineEdit.setText(str(vals['1']["voltage"]))
        self._mw.yamp_lineEdit.setText(str(vals['2']["voltage"]))
        self._mw.zamp_lineEdit.setText(str(vals['3']["voltage"]))

    
    def get_modes(self):
        if self.piezo.is_enabled(1)==True:
            self._mw.xgroundlabel.setText("x axis enabled")
        else: self._mw.xgroundlabel.setText("x axis grounded")

        if self.piezo.is_enabled(2)==True:
            self._mw.ygroundlabel.setText("y axis enabled")
        else: self._mw.ygroundlabel.setText("y axis grounded")

        if self.piezo.is_enabled(3)==True:
            self._mw.zgroundlabel.setText("z axis enabled")
        else: self._mw.zgroundlabel.setText("z axis grounded")
