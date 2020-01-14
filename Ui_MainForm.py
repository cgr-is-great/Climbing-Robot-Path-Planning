# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'J:\eric6\word directory\MainForm.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from CameraC_Form import *
from PaintBoardInterface import *


class Ui_MainWindow(QWidget):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.fileNewAction = QtWidgets.QAction(MainWindow)
        self.fileNewAction.setObjectName("fileNewAction")
        self.fileOpenAction = QtWidgets.QAction(MainWindow)
        self.fileOpenAction.setObjectName("fileOpenAction")
        self.fileCloseAction = QtWidgets.QAction(MainWindow)
        self.fileCloseAction.setObjectName("fileCloseAction")
        self.menu.addAction(self.fileNewAction)
        self.menu.addAction(self.fileOpenAction)
        self.menu.addAction(self.fileCloseAction)
        self.CameraControl = QtWidgets.QAction(MainWindow)
        self.CameraControl.setObjectName("CameraControl")
        self.RoutePlan = QtWidgets.QAction(MainWindow)
        self.RoutePlan.setObjectName("RoutePlan")
        self.menu_2.addAction(self.CameraControl)
        self.menu_2.addAction(self.RoutePlan)        
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Robot Positioning System", "Robot Positioning System"))
        self.menu.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_2.setTitle(_translate("MainWindow", "编辑(&E)"))
        self.fileNewAction.setText(_translate("MainWindow", "新建工程"))
        self.fileNewAction.setShortcut(_translate("MainWindow", "Alt+N"))
        self.fileOpenAction.setText(_translate("MainWindow", "打开工程"))
        self.fileOpenAction.setShortcut(_translate("MainWindow", "Alt+O"))
        self.fileCloseAction.setText(_translate("MainWindow", "关闭"))
        self.fileCloseAction.setShortcut(_translate("MainWindow", "Alt+C"))
        self.CameraControl.setText(_translate("MainWindow", "摄像头控制"))
        self.CameraControl.setShortcut(_translate("MainWindow", "Alt+A"))
        self.RoutePlan.setText(_translate("MainWindow", "路径规划"))
        self.RoutePlan.setShortcut(_translate("MainWindow", "Alt+P"))

'''
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
'''     


class MainForm(QMainWindow,Ui_MainWindow):
    filepath_signal = pyqtSignal(str)

    def __init__(self):
        super(MainForm, self).__init__()
        self.setupUi(self)
        self.fileCloseAction.triggered.connect(self.close)          # 菜单的点击事件，当点击关闭菜单时连接槽函数close()
        self.fileOpenAction.triggered.connect(self.openMsg)         # 菜单的点击事件，当点击打开菜单时连接槽函数openMsg()
        self.CameraControl.triggered.connect(self.openCameraC)      # 菜单的点击事件，当点击摄像头控制时连接槽函数openCameraC()
        self.RoutePlan.triggered.connect(self.openRoutePlan)        # 菜单的点击事件，当点击摄像头控制时连接槽函数openCameraC()
 
    def openMsg(self):   
        file, ok = QFileDialog.getOpenFileName(self, "打开", "C:/", "All Files (*);;Text Files (*.txt)")
        self.statusbar.showMessage(file)                            # 在状态栏显示文件地址
        self.filepath = file
        self.filepath_signal.emit(self.filepath)  

    def openCameraC(self):
        self.newWindow = CameraC_MainWindow()
        self.newWindow.show()

    def openRoutePlan(self):
        self.routeWindow = PaintBoardInterface()
        self.routeWindow.show()


class CameraCWindow(QWidget):
    def __init__(self):
        super(CameraCWindow,self).__init__()
        self.newWindowUI()

    def newWindowUI(self):
        self.resize(300, 300)
        self.move(200, 200)

    def handle_close(self):
        self.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = MainForm()
    win.show()
    sys.exit(app.exec_())
