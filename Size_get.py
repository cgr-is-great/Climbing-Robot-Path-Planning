# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 21:10:40 2018

@author: pc
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys  


class Size_get(QDialog):  
    def __init__(self ):  
        super().__init__()
         
        self.setWindowTitle('投影视平面尺寸')
        nameLb1 = QLabel('&高度(米)', self)
        self.nameEd1 = QLineEdit(self)
        nameLb1.setBuddy(self.nameEd1)
        
        nameLb2 = QLabel('&宽度(米)', self)
        self.nameEd2 = QLineEdit(self)
        nameLb2.setBuddy(self.nameEd2)
        
        btnOk = QPushButton('&OK')
        btnOk.clicked.connect(self.textreturn)
        mainLayout = QGridLayout(self)
        mainLayout.addWidget(nameLb1, 0, 0)
        mainLayout.addWidget(self.nameEd1, 0, 1, 1, 2)
        
        mainLayout.addWidget(nameLb2, 1, 0)
        mainLayout.addWidget(self.nameEd2, 1, 1, 1, 2)
         
        mainLayout.addWidget(btnOk, 2, 1)

    def textreturn(self):
        text = self.nameEd1.text()
        self.BHeight = int(text)
        text = self.nameEd2.text()
        self.BWidth = int(text)
        self.reject()


if __name__ == "__main__":   
    app = QApplication(sys.argv)
    Sizeget = Size_get()
    Sizeget.setWindowModality(Qt.ApplicationModal)
    Sizeget.exec_()
