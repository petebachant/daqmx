# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Thu May 30 10:30:42 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(553, 371)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.start_button = QtGui.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(230, 280, 75, 23))
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.figure = Qwt5.QwtPlot(self.centralwidget)
        self.figure.setGeometry(QtCore.QRect(50, 10, 451, 231))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.figure.setFont(font)
        self.figure.setStyleSheet(_fromUtf8("font: 8pt \"MS Shell Dlg 2\";"))
        self.figure.setFrameShape(QtGui.QFrame.NoFrame)
        self.figure.setFrameShadow(QtGui.QFrame.Plain)
        self.figure.setLineWidth(1)
        self.figure.setObjectName(_fromUtf8("figure"))
        self.stop_button = QtGui.QPushButton(self.centralwidget)
        self.stop_button.setGeometry(QtCore.QRect(310, 280, 75, 23))
        self.stop_button.setObjectName(_fromUtf8("stop_button"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(270, 250, 46, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.clear_button = QtGui.QPushButton(self.centralwidget)
        self.clear_button.setGeometry(QtCore.QRect(390, 280, 75, 23))
        self.clear_button.setObjectName(_fromUtf8("clear_button"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 110, 41, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.combo_box = QtGui.QComboBox(self.centralwidget)
        self.combo_box.setGeometry(QtCore.QRect(130, 280, 91, 22))
        self.combo_box.setObjectName(_fromUtf8("combo_box"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 553, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_save = QtGui.QAction(MainWindow)
        self.action_save.setObjectName(_fromUtf8("action_save"))
        self.menuFile.addAction(self.action_save)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "DAQmx with PyQt", None))
        self.start_button.setText(_translate("MainWindow", "Start", None))
        self.stop_button.setText(_translate("MainWindow", "Stop", None))
        self.label.setText(_translate("MainWindow", "Time (s)", None))
        self.clear_button.setText(_translate("MainWindow", "Clear", None))
        self.label_2.setText(_translate("MainWindow", "Voltage", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.action_save.setText(_translate("MainWindow", "Save", None))

from PyQt4 import Qwt5
