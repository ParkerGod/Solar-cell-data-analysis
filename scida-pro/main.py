# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import Required_resources

from views import MainWindow


def main() -> int:
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(255, 79, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
