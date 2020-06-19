# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1155, 497)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(230, 20, 251, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(610, 20, 251, 17))
        self.label_3.setObjectName("label_3")
        self.loadPatentBtn = QtWidgets.QPushButton(self.centralwidget)
        self.loadPatentBtn.setGeometry(QtCore.QRect(10, 350, 211, 41))
        self.loadPatentBtn.setObjectName("loadPatentBtn")
        self.saoTable = QtWidgets.QTableWidget(self.centralwidget)
        self.saoTable.setGeometry(QtCore.QRect(610, 40, 531, 291))
        self.saoTable.setObjectName("saoTable")
        self.saoTable.setColumnCount(3)
        self.saoTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.saoTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.saoTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.saoTable.setHorizontalHeaderItem(2, item)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 141, 17))
        self.label.setObjectName("label")
        self.patentsList = QtWidgets.QListWidget(self.centralwidget)
        self.patentsList.setGeometry(QtCore.QRect(10, 40, 211, 291))
        self.patentsList.setObjectName("patentsList")
        self.patentClaimsText = QtWidgets.QTextBrowser(self.centralwidget)
        self.patentClaimsText.setGeometry(QtCore.QRect(230, 40, 371, 291))
        self.patentClaimsText.setObjectName("patentClaimsText")
        self.loadPatentsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.loadPatentsBtn.setGeometry(QtCore.QRect(10, 400, 211, 41))
        self.loadPatentsBtn.setObjectName("loadPatentsBtn")
        self.extractSaoBtn = QtWidgets.QPushButton(self.centralwidget)
        self.extractSaoBtn.setGeometry(QtCore.QRect(610, 400, 251, 41))
        self.extractSaoBtn.setObjectName("extractSaoBtn")
        self.buildOntologyBtn = QtWidgets.QPushButton(self.centralwidget)
        self.buildOntologyBtn.setGeometry(QtCore.QRect(890, 400, 251, 41))
        self.buildOntologyBtn.setObjectName("buildOntologyBtn")
        self.buildPatentsOntologyBtn = QtWidgets.QPushButton(self.centralwidget)
        self.buildPatentsOntologyBtn.setGeometry(QtCore.QRect(890, 450, 251, 41))
        self.buildPatentsOntologyBtn.setObjectName("buildPatentsOntologyBtn")
        self.problemText = QtWidgets.QTextBrowser(self.centralwidget)
        self.problemText.setGeometry(QtCore.QRect(610, 360, 531, 31))
        self.problemText.setObjectName("problemText")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(610, 340, 251, 17))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Ontology Builder"))
        self.label_2.setText(_translate("MainWindow", "Описание патентного документа"))
        self.label_3.setText(_translate("MainWindow", "Извлеченные SAO"))
        self.loadPatentBtn.setText(_translate("MainWindow", "Загрузить патент"))
        item = self.saoTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Субъект"))
        item = self.saoTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Действие"))
        item = self.saoTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Объект"))
        self.label.setText(_translate("MainWindow", "Патентные документы"))
        self.loadPatentsBtn.setText(_translate("MainWindow", "Загрузить патенты"))
        self.extractSaoBtn.setText(_translate("MainWindow", "Извлечь SAO"))
        self.buildOntologyBtn.setText(_translate("MainWindow", "Построить онтологию для патента"))
        self.buildPatentsOntologyBtn.setText(_translate("MainWindow", "Построить онтологию для патентов"))
        self.label_4.setText(_translate("MainWindow", "Проблема-решение изобретения"))

