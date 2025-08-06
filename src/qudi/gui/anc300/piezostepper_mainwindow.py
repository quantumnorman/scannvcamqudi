# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'piezostepper_gui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
import sys

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

        self.xneg_step_pushButton = QPushButton(self.xgridLayoutWidget, text= "< Step")
        self.xgridLayout.addWidget(self.xneg_step_pushButton, 0, 1, 1, 1)

        self.xfreq_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xfreq_lineEdit, 0, 3, 1, 1)
        self.xfreq_lineEdit.setText("x frequency")

        self.xamplitude_lineEdit = QLineEdit(self.xgridLayoutWidget)
        self.xgridLayout.addWidget(self.xamplitude_lineEdit, 0, 2, 1, 1)
        self.xamplitude_lineEdit.setText("x amplitude")

        self.xpos_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="Continuous >>")
        self.xgridLayout.addWidget(self.xpos_cont_pushButton, 0, 5, 1, 1)

        self.xneg_cont_pushButton = QPushButton(self.xgridLayoutWidget, text="<< Continuous")
        self.xgridLayout.addWidget(self.xneg_cont_pushButton, 0, 0, 1, 1)

        # self.label = QLabel(self.gridLayoutWidget)
        # self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.xaxis_groupBox)


        self.yaxis_groupBox = QGroupBox(self.verticalLayoutWidget, title="y axis")
        self.ygridLayoutWidget = QWidget(self.yaxis_groupBox)
        self.ygridLayoutWidget.setGeometry(QRect(0, 20, 531, 81))

        self.ygridLayout = QGridLayout(self.ygridLayoutWidget)
        self.ygridLayout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit_3 = QLineEdit(self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.lineEdit_3, 0, 2, 1, 1)

        self.ypos_step_pushButton = QPushButton(self.ygridLayoutWidget, text="Step >")
        self.ygridLayout.addWidget(self.ypos_step_pushButton, 0, 4, 1, 1)

        self.yground_pushButton = QPushButton(self.ygridLayoutWidget, text="Ground y piezo")
        self.ygridLayout.addWidget(self.yground_pushButton, 1, 5, 1, 1)

        self.yneg_step_pushButton = QPushButton(self.ygridLayoutWidget, text="< Step")
        self.ygridLayout.addWidget(self.yneg_step_pushButton, 0, 1, 1, 1)

        self.lineEdit_4 = QLineEdit(self.ygridLayoutWidget)
        self.ygridLayout.addWidget(self.lineEdit_4, 0, 3, 1, 1)

        self.ypos_cont_pushButton = QPushButton(self.ygridLayoutWidget, text= "Continuous >>")
        self.ygridLayout.addWidget(self.ypos_cont_pushButton, 0, 5, 1, 1)

        self.yneg_cont_pushButton = QPushButton(self.ygridLayoutWidget, text="<< Continuous")
        self.ygridLayout.addWidget(self.yneg_cont_pushButton, 0, 0, 1, 1)

        # self.label_2 = QLabel(self.ygridLayoutWidget)
        # self.ygridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.yaxis_groupBox)


        self.zaxis_groupBox = QGroupBox(self.verticalLayoutWidget, title="z axis")
        self.zgridLayoutWidget = QWidget(self.zaxis_groupBox)
        self.zgridLayoutWidget.setGeometry(QRect(0, 30, 531, 81))

        self.zgridLayout = QGridLayout(self.zgridLayoutWidget)
        self.zgridLayout.setContentsMargins(0, 0, 0, 0)

        
        self.lineEdit_5 = QLineEdit(self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.lineEdit_5, 0, 2, 1, 1)

        self.zpos_step_pushButton = QPushButton(self.zgridLayoutWidget, text="Step >")
        self.zgridLayout.addWidget(self.zpos_step_pushButton, 0, 4, 1, 1)

        self.zground_pushButton = QPushButton(self.zgridLayoutWidget, text= "Ground z piezo")
        self.zgridLayout.addWidget(self.zground_pushButton, 1, 5, 1, 1)

        self.zneg_step_pushButton = QPushButton(self.zgridLayoutWidget, text= "< Step")
        self.zgridLayout.addWidget(self.zneg_step_pushButton, 0, 1, 1, 1)

        self.lineEdit_6 = QLineEdit(self.zgridLayoutWidget)
        self.zgridLayout.addWidget(self.lineEdit_6, 0, 3, 1, 1)

        self.zpos_cont_pushButton = QPushButton(self.zgridLayoutWidget, text= "Continuous >>")
        self.zgridLayout.addWidget(self.zpos_cont_pushButton, 0, 5, 1, 1)

        self.zneg_cont_pushButton = QPushButton(self.zgridLayoutWidget, text="<< Continuous")
        self.zgridLayout.addWidget(self.zneg_cont_pushButton, 0, 0, 1, 1)

        # self.label_3 = QLabel(self.zgridLayoutWidget)
        # self.zgridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.zaxis_groupBox)


        self.horizontalLayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groundall_pushButton = QPushButton(self.verticalLayoutWidget, text="Ground all piezos")
        self.horizontalLayout.addWidget(self.groundall_pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralwidget)



# app = QApplication(sys.argv)

# window = PiezoStepperMainWindow()
# window.show()

# app.exec_()