from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
import sys

###check status at ini
###check status before movement
###make qlabels reflect status
###connect ground/unground




class PiezoStepperMainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()      
        self.setGeometry(0,0, 551, 360)
        self.piezocontrol = anccontrols()
        # if not MainWindow.objectName():
        #     MainWindow.setObjectName(u"MainWindow")
        # MainWindow.resize(549, 460)
        self.centralwidget = QWidget()
        self.verticalLayoutWidget = QWidget(self.centralwidget)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.xaxis_groupBox = QGroupBox(self.verticalLayoutWidget, title="x axis")
        self.xgridLayoutWidget = QWidget(self.xaxis_groupBox)
        self.xgridLayoutWidget.setGeometry(QRect(0, 19, 531, 81))

        self.xgridLayout = QGridLayout(self.xgridLayoutWidget)
        self.xgridLayout.setContentsMargins(0, 0, 0, 0)

        self.xpos_step_pushButton = QPushButton(self.xgridLayoutWidget, text="Step >")
        self.xgridLayout.addWidget(self.xpos_step_pushButton, 0, 4, 1, 1)
        self.xpos_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("1", "+"))

        self.xground_pushButton = QPushButton(self.xgridLayoutWidget, text="Ground x piezo")
        self.xgridLayout.addWidget(self.xground_pushButton, 1, 5, 1, 1)
        self.xground_pushButton.clicked.connect(lambda:self.ground_channel("1"))

        self.xenable_pushButton = QPushButton(self.xgridLayoutWidget, text="Enable x piezo")
        self.xgridLayout.addWidget(self.xground_pushButton, 1, 4, 1, 1)
        self.xenable_pushButton.clicked.connect(lambda:self.enable_channel("1"))


        self.xneg_step_pushButton = QPushButton(self.xgridLayoutWidget, text= "< Step")
        self.xgridLayout.addWidget(self.xneg_step_pushButton, 0, 1, 1, 1)
        self.xneg_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("1", "-"))


        self.xfreq_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xfreq_lineEdit, 0, 3, 1, 1)
        self.xfreq_lineEdit.setText("x frequency")
        self.xfreq_lineEdit.returnPressed.connect(self.get_params)


        self.xamp_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xamp_lineEdit, 0, 2, 1, 1)
        self.xamp_lineEdit.setText("x amplitude")
        self.xamp_lineEdit.returnPressed.connect(self.get_params)

        self.xpos_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="Continuous >>")
        self.xgridLayout.addWidget(self.xpos_cont_pushButton, 0, 5, 1, 1)
        self.xpos_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('1', "+"))
        self.xpos_cont_pushButton.released.connect(self.continuous_released)
        

        self.xneg_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="<< Continuous")
        self.xgridLayout.addWidget(self.xneg_cont_pushButton, 0, 0, 1, 1)
        self.xneg_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('2', "-"))
        self.xneg_cont_pushButton.released.connect(self.continuous_released)

    
        self.xgroundlabel = QLabel("x axis grounded", self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xgroundlabel, 1, 0, 1, 1)
        


        self.verticalLayout.addWidget(self.xaxis_groupBox)


        self.yaxis_groupBox = QGroupBox(self.verticalLayoutWidget, title="y axis")
        self.ygridLayoutWidget = QWidget(self.yaxis_groupBox)
        self.ygridLayoutWidget.setGeometry(QRect(0, 20, 531, 81))

        self.ygridLayout = QGridLayout(self.ygridLayoutWidget)
        self.ygridLayout.setContentsMargins(0, 0, 0, 0)

        self.yamp_lineEdit = QLineEdit(self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.yamp_lineEdit, 0, 2, 1, 1)
        self.yamp_lineEdit.returnPressed.connect(self.get_params)


        self.ypos_step_pushButton = QPushButton(self.ygridLayoutWidget, text="Step >")
        self.ygridLayout.addWidget(self.ypos_step_pushButton, 0,  4, 1, 1)
        self.ypos_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("2", "+"))


        self.yground_pushButton = QPushButton(self.ygridLayoutWidget, text="Ground y piezo")
        self.ygridLayout.addWidget(self.yground_pushButton, 1, 5, 1, 1)
        self.yground_pushButton.clicked.connect(lambda: self.ground_channel("2"))

        self.yenable_pushButton = QPushButton(self.ygridLayoutWidget, text="Enable y piezo")
        self.ygridLayout.addWidget(self.yenable_pushButton, 1, 4, 1, 1)
        self.yenable_pushButton.clicked.connect(lambda: self.enable_channel("2"))

        self.yneg_step_pushButton = QPushButton(self.ygridLayoutWidget, text="< Step")
        self.ygridLayout.addWidget(self.yneg_step_pushButton, 0, 1, 1, 1)
        self.yneg_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("2", "-"))

        self.yfreq_lineEdit = QLineEdit(self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.yfreq_lineEdit, 0, 3, 1, 1)
        self.yfreq_lineEdit.returnPressed.connect(self.get_params)


        self.ypos_cont_pushButton = QPushButton(self.ygridLayoutWidget, text= "Continuous >>")
        self.ygridLayout.addWidget(self.ypos_cont_pushButton, 0, 5, 1, 1)
        self.ypos_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('2', "+"))
        self.ypos_cont_pushButton.released.connect(self.continuous_released)

        self.yneg_cont_pushButton = QPushButton(self.ygridLayoutWidget, text="<< Continuous")
        self.ygridLayout.addWidget(self.yneg_cont_pushButton, 0, 0, 1, 1)
        self.yneg_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('2', "-"))
        self.yneg_cont_pushButton.released.connect(self.continuous_released)

        self.ygroundlabel = QLabel("y axis grounded", self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.ygroundlabel, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.yaxis_groupBox)


        self.zaxis_groupBox = QGroupBox(self.verticalLayoutWidget, title="z axis")
        self.zgridLayoutWidget = QWidget(self.zaxis_groupBox)
        self.zgridLayoutWidget.setGeometry(QRect(0, 30, 531, 81))

        self.zgridLayout = QGridLayout(self.zgridLayoutWidget)
        self.zgridLayout.setContentsMargins(0, 0, 0, 0)

        
        self.zamp_lineEdit = QLineEdit(self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.zamp_lineEdit, 0, 2, 1, 1)
        self.zamp_lineEdit.returnPressed.connect(self.get_params)


        self.zpos_step_pushButton = QPushButton(self.zgridLayoutWidget, text="Step >")
        self.zgridLayout.addWidget(self.zpos_step_pushButton, 0, 4, 1, 1)
        self.zpos_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("3", "+"))


        self.zground_pushButton = QPushButton(self.zgridLayoutWidget, text= "Ground z piezo")
        self.zgridLayout.addWidget(self.zground_pushButton, 1, 5, 1, 1)
        self.zground_pushButton.clicked.connect(lambda: self.ground_channel("3"))

        self.zenable_pushButton = QPushButton(self.zgridLayoutWidget, text="Enable z piezo")
        self.zgridLayout.addWidget(self.zenable_pushButton, 1, 4, 1, 1)
        self.zenable_pushButton.clicked.connect(lambda: self.enable_channel("3"))

        self.zneg_step_pushButton = QPushButton(self.zgridLayoutWidget, text= "< Step")
        self.zgridLayout.addWidget(self.zneg_step_pushButton, 0, 1, 1, 1)
        self.zneg_step_pushButton.clicked.connect(lambda : self.piezocontrol.step("3", "-"))

        self.zfreq_lineEdit = QLineEdit(self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.zfreq_lineEdit, 0, 3, 1, 1)
        self.zfreq_lineEdit.returnPressed.connect(self.get_params)


        self.zpos_cont_pushButton = QPushButton(self.zgridLayoutWidget, text= "Continuous >>")
        self.zgridLayout.addWidget(self.zpos_cont_pushButton, 0, 5, 1, 1)
        self.zpos_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('3', "+"))
        self.zpos_cont_pushButton.released.connect(self.continuous_released)

        self.zneg_cont_pushButton = QPushButton(self.zgridLayoutWidget, text="<< Continuous")
        self.zgridLayout.addWidget(self.zneg_cont_pushButton, 0, 0, 1, 1)
        self.zneg_cont_pushButton.pressed.connect(lambda: self.continuous_pressed('3', "-"))
        self.zneg_cont_pushButton.released.connect(self.continuous_released)

        self.zgroundlabel = QLabel("z axis grounded", self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.zgroundlabel, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.zaxis_groupBox)


        self.horizontalLayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groundall_pushButton = QPushButton(self.verticalLayoutWidget, text="Ground all piezos")
        self.horizontalLayout.addWidget(self.groundall_pushButton)
        self.groundall_pushButton.clicked.connect(lambda : self.piezocontrol.ground_channel("all"))


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralwidget)

    def get_params(self):
        values = {
                    '1' :{
                        'voltage': float(self.xamp_lineEdit.text()), 
                        'frequency' : float(self.xfreq_lineEdit.text())},
                    '2' :{
                        'voltage': float(self.yamp_lineEdit.text()), 
                        'frequency' : float(self.yfreq_lineEdit.text())},
                    '3' :{
                        'voltage': float(self.zamp_lineEdit.text()), 
                        'frequency' : float(self.zfreq_lineEdit.text())},
                  }
        print(values)

        self.update_params(values)

        return values
    
    def get_modes(self):
        modes = {
                    '1' : self.piezocontrol.is_enabled("1"),
                    '2' : self.piezocontrol.is_enabled("2"),
                    '3' : self.piezocontrol.is_enabled("3")
        }
        return modes
    
    def update_modes(self):
        modes = self.get_modes()
        if modes['1'] == True:
            self.xgroundlabel.setText("x axis active")
        if modes['1'] == False:
            self.xgroundlabel.setText("x axis grounded")

        if modes['2'] == True:
            self.ygroundlabel.setText("y axis active")
        if modes['2'] == False:
            self.ygroundlabel.setText("y axis grounded")

        if modes['3'] == True:
            self.zgroundlabel.setText("z axis active")
        if modes['3'] == False:
            self.zgroundlabel.setText("z axis grounded")

    
    def update_params(self, vals):
        self.piezocontrol.setallparams(vals)
        
    def step_clicked(self, channel):
        self.piezocontrol.step(channel, steps=1)
    
    def continuous_pressed(self, channel, direction):
        self.piezocontrol.jog(channel, direction)

    def continuous_released(self):
        self.piezocontrol.stop_jog()

    def ground_channel(self, axis="all"):
        self.piezocontrol.ground_channel(axis)
        self.update_modes()

    def enable_channel(self, axis="all"):
        self.piezocontrol.enable_channel(axis)
        self.update_modes()


class anccontrols():
    def __init__(self):

        self.config = {'name' : "ANC300_attempt1",
                  'address' : 'COM3'}
        self.values = {
                    '1' : {
                        'voltage': 25, #piezo amplitude in Volts
                        'frequency' : 1000 #piezo frequency in Hz
                        },
                    '2' : {
                        'voltage' : 25,
                        'frequency' : 1000
                    },
                    '3' : {
                        'voltage' : 25,
                        'frequency' : 1000
                    }
                  }
        print(self.values)
        self.setallparams(self.values)

        return

    def setallparams(self, vals):
        for i in self.values:
            # self.device.set_param(vals[i], 'voltage', vals[i]['voltage'])
            # self.device.set_param(vals(i), 'frequency', vals[i]['frequency'])
            # print(vals[i], 'voltage', vals[i]['voltage'])
            # print(vals[i], 'frequency', vals[i]['frequency'])
            print(vals[i])

    def step(self, channel, sign="+"):
        if self.is_enabled(channel)==True:
            if sign=="+":
                value = 1
            if sign == "-":
                value = -1
            # self.device.step(channel, value)
            print('step', channel, sign)
        else: print("channel grounded, cannot move")

    def jog(self, channel, direction="+"):
        if self.is_enabled(channel)==True:
            # self.device.jog(channel, direction)
            print('jog', channel, direction)
        else: print("channel disabled, cannot move")

    def stop_jog(self, axis = "all"):
        # self.device.stop()
        print('stop')

    def ground_channel(self, axis="all"):
        # self.device.disable_axis(axis)
        print("grounded", axis)

    def is_enabled(self, axis="all"):
        # mode = self.device.is_enabled(axis)
        print(axis, "enabled?")
        # return mode

    def enable_channel(self, axis="all"):
        # self.device.enable_channel(axis)
        print(axis, "enabled")


app = QApplication(sys.argv)

window = PiezoStepperMainWindow()
window.show()

app.exec_()