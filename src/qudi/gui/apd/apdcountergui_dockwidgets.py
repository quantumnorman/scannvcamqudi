# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_slow_counter.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from pyqtgraph import PlotWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(506, 370)
        self.start_counter_Action = QAction(MainWindow)
        self.start_counter_Action.setObjectName(u"start_counter_Action")
        self.start_counter_Action.setCheckable(True)
        counterstart_icon = QIcon()
        counterstart_icon.addFile(u"../../../../.venv/Lib/site-packages/qudi/artwork/icons/start-counter.svg", QSize(), QIcon.Normal, QIcon.Off)
        counterstart_icon.addFile(u"../../../../.venv/Lib/site-packages/qudi/artwork/icons/stop-counter.svg", QSize(), QIcon.Normal, QIcon.On)
        self.start_counter_Action.setIcon(counterstart_icon)
        self.record_counts_Action = QAction(MainWindow)
        self.record_counts_Action.setObjectName(u"record_counts_Action")
        self.record_counts_Action.setCheckable(True)
        recordstart_icon = QIcon()
        recordstart_icon.addFile(u"../../../../.venv/Lib/site-packages/qudi/artwork/icons/record-counter.svgz", QSize(), QIcon.Normal, QIcon.Off)
        recordstart_icon.addFile(u"../../../../.venv/Lib/site-packages/qudi/artwork/icons/stop-counter.svg", QSize(), QIcon.Normal, QIcon.On)
        self.record_counts_Action.setIcon(recordstart_icon)
        self.slow_counter_view_Action = QAction(MainWindow)
        self.slow_counter_view_Action.setObjectName(u"slow_counter_view_Action")
        self.slow_counter_view_Action.setCheckable(True)
        self.slow_counter_parameters_view_Action = QAction(MainWindow)
        self.slow_counter_parameters_view_Action.setObjectName(u"slow_counter_parameters_view_Action")
        self.slow_counter_parameters_view_Action.setCheckable(True)
        self.restore_default_view_Action = QAction(MainWindow)
        self.restore_default_view_Action.setObjectName(u"restore_default_view_Action")
        self.counting_controls_view_Action = QAction(MainWindow)
        self.counting_controls_view_Action.setObjectName(u"counting_controls_view_Action")
        self.counting_controls_view_Action.setCheckable(True)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        icon2 = QIcon()
        icon2.addFile(u"../../artwork/icons/oxygen/22x22/application-exit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionClose.setIcon(icon2)
        self.trace_selection_view_Action = QAction(MainWindow)
        self.trace_selection_view_Action.setObjectName(u"trace_selection_view_Action")
        self.trace_selection_view_Action.setCheckable(True)
        self.trace_selection_view_Action.setChecked(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 506, 21))
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuToolbars = QMenu(self.menuView)
        self.menuToolbars.setObjectName(u"menuToolbars")
        MainWindow.setMenuBar(self.menubar)
        self.counter_trace_DockWidget = QDockWidget(MainWindow)
        self.counter_trace_DockWidget.setObjectName(u"counter_trace_DockWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.counter_trace_DockWidget.sizePolicy().hasHeightForWidth())
        self.counter_trace_DockWidget.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.count_value_Label = QLabel(self.dockWidgetContents)
        self.count_value_Label.setObjectName(u"count_value_Label")
        font = QFont()
        font.setPointSize(60)
        font.setBold(True)
        font.setWeight(75)
        self.count_value_Label.setFont(font)
        self.count_value_Label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout.addWidget(self.count_value_Label)

        self.counter_trace_PlotWidget = PlotWidget(self.dockWidgetContents)
        self.counter_trace_PlotWidget.setObjectName(u"counter_trace_PlotWidget")

        self.verticalLayout.addWidget(self.counter_trace_PlotWidget)

        self.counter_trace_DockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.TopDockWidgetArea, self.counter_trace_DockWidget)
        self.slow_counter_parameters_DockWidget = QDockWidget(MainWindow)
        self.slow_counter_parameters_DockWidget.setObjectName(u"slow_counter_parameters_DockWidget")
        self.slow_counter_parameters_DockWidget.setMaximumSize(QSize(524287, 100))
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.horizontalLayout = QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.dockWidgetContents_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.count_length_SpinBox = QSpinBox(self.dockWidgetContents_2)
        self.count_length_SpinBox.setObjectName(u"count_length_SpinBox")
        self.count_length_SpinBox.setMinimum(1)
        self.count_length_SpinBox.setMaximum(1000000)
        self.count_length_SpinBox.setSingleStep(10)
        self.count_length_SpinBox.setValue(300)

        self.horizontalLayout.addWidget(self.count_length_SpinBox)

        self.label_2 = QLabel(self.dockWidgetContents_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.count_freq_SpinBox = QSpinBox(self.dockWidgetContents_2)
        self.count_freq_SpinBox.setObjectName(u"count_freq_SpinBox")
        self.count_freq_SpinBox.setMinimum(1)
        self.count_freq_SpinBox.setMaximum(1000000)
        self.count_freq_SpinBox.setSingleStep(10)
        self.count_freq_SpinBox.setValue(50)

        self.horizontalLayout.addWidget(self.count_freq_SpinBox)

        self.label_3 = QLabel(self.dockWidgetContents_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.oversampling_SpinBox = QSpinBox(self.dockWidgetContents_2)
        self.oversampling_SpinBox.setObjectName(u"oversampling_SpinBox")
        self.oversampling_SpinBox.setMinimum(1)
        self.oversampling_SpinBox.setMaximum(10000)
        self.oversampling_SpinBox.setValue(1)

        self.horizontalLayout.addWidget(self.oversampling_SpinBox)

        self.slow_counter_parameters_DockWidget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.slow_counter_parameters_DockWidget)
        self.counting_control_ToolBar = QToolBar(MainWindow)
        self.counting_control_ToolBar.setObjectName(u"counting_control_ToolBar")
        self.counting_control_ToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.counting_control_ToolBar)

        self.menubar.addAction(self.menuView.menuAction())
        self.menuView.addAction(self.slow_counter_view_Action)
        self.menuView.addAction(self.slow_counter_parameters_view_Action)
        self.menuView.addAction(self.trace_selection_view_Action)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuToolbars.menuAction())
        self.menuView.addSeparator()
        self.menuView.addAction(self.restore_default_view_Action)
        self.menuView.addAction(self.actionClose)
        self.menuToolbars.addAction(self.counting_controls_view_Action)
        self.counting_control_ToolBar.addAction(self.start_counter_Action)
        self.counting_control_ToolBar.addAction(self.record_counts_Action)

        self.retranslateUi(MainWindow)
        self.slow_counter_view_Action.triggered.connect(self.counter_trace_DockWidget.setVisible)
        self.counter_trace_DockWidget.visibilityChanged.connect(self.slow_counter_view_Action.setChecked)
        self.slow_counter_parameters_view_Action.triggered.connect(self.slow_counter_parameters_DockWidget.setVisible)
        self.slow_counter_parameters_DockWidget.visibilityChanged.connect(self.slow_counter_parameters_view_Action.setChecked)
        self.counting_controls_view_Action.triggered.connect(self.counting_control_ToolBar.setVisible)
        self.counting_control_ToolBar.visibilityChanged.connect(self.counting_controls_view_Action.setChecked)
        self.actionClose.triggered.connect(MainWindow.close)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"qudi: Slow Counter", None))
        self.start_counter_Action.setText(QCoreApplication.translate("MainWindow", u"Start counter", None))
#if QT_CONFIG(tooltip)
        self.start_counter_Action.setToolTip(QCoreApplication.translate("MainWindow", u"Start the counter", None))
#endif // QT_CONFIG(tooltip)
        self.record_counts_Action.setText(QCoreApplication.translate("MainWindow", u"Record counts", None))
#if QT_CONFIG(tooltip)
        self.record_counts_Action.setToolTip(QCoreApplication.translate("MainWindow", u"Save count trace to file", None))
#endif // QT_CONFIG(tooltip)
        self.slow_counter_view_Action.setText(QCoreApplication.translate("MainWindow", u"&Slow counter", None))
#if QT_CONFIG(tooltip)
        self.slow_counter_view_Action.setToolTip(QCoreApplication.translate("MainWindow", u"Show the Slow counter", None))
#endif // QT_CONFIG(tooltip)
        self.slow_counter_parameters_view_Action.setText(QCoreApplication.translate("MainWindow", u"Slow &counter parameters", None))
#if QT_CONFIG(tooltip)
        self.slow_counter_parameters_view_Action.setToolTip(QCoreApplication.translate("MainWindow", u"Show Slow counter parameters", None))
#endif // QT_CONFIG(tooltip)
        self.restore_default_view_Action.setText(QCoreApplication.translate("MainWindow", u"&Restore default", None))
        self.counting_controls_view_Action.setText(QCoreApplication.translate("MainWindow", u"&Counting controls", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.trace_selection_view_Action.setText(QCoreApplication.translate("MainWindow", u"Trace Selection", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.menuToolbars.setTitle(QCoreApplication.translate("MainWindow", u"&Toolbars", None))
        self.counter_trace_DockWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Slow Counter", None))
        self.count_value_Label.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.slow_counter_parameters_DockWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Slow counter control", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Count length (#):", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Count frequency (Hz):", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MainWindow", u"If bigger than 1, the number of samples is averaged over the given number and then displayed. \n"
"Use for extremely fast counting, since all the raw data is saved. \n"
"Timestamps in oversampling interval are all equal to the averaging time.", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Oversampling (#):", None))
#if QT_CONFIG(tooltip)
        self.oversampling_SpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"If bigger than 1, the number of samples is averaged over the given number and then displayed. \n"
"Use for extremely fast counting, since all the raw data is saved. \n"
"Timestamps in oversampling interval are all equal to the averaging time.", None))
#endif // QT_CONFIG(tooltip)
        self.counting_control_ToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"Counting Controls", None))
    # retranslateUi

