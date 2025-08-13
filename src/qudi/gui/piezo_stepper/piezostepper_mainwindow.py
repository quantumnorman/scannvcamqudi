from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
import sys

##TODO: fix groupbox spacing to stop labels from squishing


class PiezoStepperMainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()      
        self.setGeometry(0,0, 551, 360)
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

        self.xground_pushButton = QPushButton(self.xgridLayoutWidget, text="Ground x piezo")
        self.xgridLayout.addWidget(self.xground_pushButton, 1, 5, 1, 1)

        self.xenable_pushButton = QPushButton(self.xgridLayoutWidget, text="Enable x piezo")
        self.xgridLayout.addWidget(self.xenable_pushButton, 1, 4, 1, 1)

        self.xneg_step_pushButton = QPushButton(self.xgridLayoutWidget, text= "< Step")
        self.xgridLayout.addWidget(self.xneg_step_pushButton, 0, 1, 1, 1)

        self.xfreq_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xfreq_lineEdit, 0, 3, 1, 1)

        self.xamp_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xamp_lineEdit, 0, 2, 1, 1)
        self.xamp_lineEdit.setText("x amplitude")

        self.xpos_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="Continuous >>")
        self.xgridLayout.addWidget(self.xpos_cont_pushButton, 0, 5, 1, 1)

        self.xneg_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="<< Continuous")
        self.xgridLayout.addWidget(self.xneg_cont_pushButton, 0, 0, 1, 1)
    
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

        self.ypos_step_pushButton = QPushButton(self.ygridLayoutWidget, text="Step >")
        self.ygridLayout.addWidget(self.ypos_step_pushButton, 0,  4, 1, 1)

        self.yground_pushButton = QPushButton(self.ygridLayoutWidget, text="Ground y piezo")
        self.ygridLayout.addWidget(self.yground_pushButton, 1, 5, 1, 1)

        self.yenable_pushButton = QPushButton(self.ygridLayoutWidget, text="Enable y piezo")
        self.ygridLayout.addWidget(self.yenable_pushButton, 1, 4, 1, 1)

        self.yneg_step_pushButton = QPushButton(self.ygridLayoutWidget, text="< Step")
        self.ygridLayout.addWidget(self.yneg_step_pushButton, 0, 1, 1, 1)

        self.yfreq_lineEdit = QLineEdit(self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.yfreq_lineEdit, 0, 3, 1, 1)

        self.ypos_cont_pushButton = QPushButton(self.ygridLayoutWidget, text= "Continuous >>")
        self.ygridLayout.addWidget(self.ypos_cont_pushButton, 0, 5, 1, 1)

        self.yneg_cont_pushButton = QPushButton(self.ygridLayoutWidget, text="<< Continuous")
        self.ygridLayout.addWidget(self.yneg_cont_pushButton, 0, 0, 1, 1)

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


        self.zpos_step_pushButton = QPushButton(self.zgridLayoutWidget, text="Step >")
        self.zgridLayout.addWidget(self.zpos_step_pushButton, 0, 4, 1, 1)


        self.zground_pushButton = QPushButton(self.zgridLayoutWidget, text= "Ground z piezo")
        self.zgridLayout.addWidget(self.zground_pushButton, 1, 5, 1, 1)

        self.zenable_pushButton = QPushButton(self.zgridLayoutWidget, text="Enable z piezo")
        self.zgridLayout.addWidget(self.zenable_pushButton, 1, 4, 1, 1)

        self.zneg_step_pushButton = QPushButton(self.zgridLayoutWidget, text= "< Step")
        self.zgridLayout.addWidget(self.zneg_step_pushButton, 0, 1, 1, 1)

        self.zfreq_lineEdit = QLineEdit(self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.zfreq_lineEdit, 0, 3, 1, 1)


        self.zpos_cont_pushButton = QPushButton(self.zgridLayoutWidget, text= "Continuous >>")
        self.zgridLayout.addWidget(self.zpos_cont_pushButton, 0, 5, 1, 1)

        self.zneg_cont_pushButton = QPushButton(self.zgridLayoutWidget, text="<< Continuous")
        self.zgridLayout.addWidget(self.zneg_cont_pushButton, 0, 0, 1, 1)

        self.zgroundlabel = QLabel("z axis grounded", self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.zgroundlabel, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.zaxis_groupBox)


        self.horizontalLayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groundall_pushButton = QPushButton(self.verticalLayoutWidget, text="Ground all piezos")
        self.horizontalLayout.addWidget(self.groundall_pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralwidget)