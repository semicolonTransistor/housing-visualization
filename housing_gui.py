# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\brent\OneDrive\Documents\untitled1\form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from housing_visualization.gui.Map import Map


class Ui_mapgui(object):
    def setupUi(self, mapgui):
        mapgui.setObjectName("mapgui")
        mapgui.resize(845, 702)
        self.centralwidget = QtWidgets.QWidget(mapgui)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 761, 481))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.widget.setObjectName("widget")
        self.mapping = Map()

        self.verticalLayout.addWidget(self.mapping)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 500, 761, 61))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalSlider = QtWidgets.QSlider(self.verticalLayoutWidget_2)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(len(self.mapping.dates)-1)
        self.horizontalSlider.valueChanged.connect(self.update_from_slider)
        self.horizontalSlider.sliderReleased.connect(self.update_date)

        self.verticalLayout_2.addWidget(self.horizontalSlider)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        mapgui.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mapgui)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 845, 21))
        self.menubar.setObjectName("menubar")
        mapgui.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mapgui)
        self.statusbar.setObjectName("statusbar")
        mapgui.setStatusBar(self.statusbar)

        self.retranslateUi(mapgui)
        QtCore.QMetaObject.connectSlotsByName(mapgui)

    def update_from_slider(self, slider_val):
        self.label_3.setText(str(self.mapping.dates[slider_val]))

    def update_date(self):
        self.mapping.update_date_by_idx(self.horizontalSlider.value())
        self.mapping.update_plot()

    def retranslateUi(self, mapgui):
        _translate = QtCore.QCoreApplication.translate
        mapgui.setWindowTitle(_translate("mapgui", "mapgui"))
        self.label_2.setText(_translate("mapgui", self.mapping.dates[0]))
        self.label.setText(_translate("mapgui", self.mapping.dates[-1]))
        self.label_3.setText(_translate("mapgui", self.mapping.cur_date))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mapgui = QtWidgets.QMainWindow()
    ui = Ui_mapgui()
    ui.setupUi(mapgui)
    mapgui.show()
    sys.exit(app.exec_())
