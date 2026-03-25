# -*- coding: utf-8 -*-
"""
SCiDA Pro - Solar Cell Data Analysis
Main entry point
"""

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

# Import MVC components
from models import DataCollection
from views import MainWindow
from controllers import MainController
from utils import ConfigManager

# Import resources
import Required_resources


def main():
    """Main application entry point"""
    app = QtWidgets.QApplication.instance()
    if not app:
        # if no other PyQt program is running (such as the IDE) create a new instance
        app = QtWidgets.QApplication(sys.argv)
    
    # Set application style and palette
    app.setStyle("Fusion")
    
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(255, 79, 0))
    app.setPalette(palette)
    
    # Dependency injection setup
    config = ConfigManager()
    data_collection = DataCollection()
    
    # Create MVC components
    window = MainWindow(data_collection=data_collection, config=config)
    controller = MainController(
        data_collection=data_collection,
        config=config,
        view=window
    )
    
    # Connect controller to view
    controller.set_view(window)
    
    # Run application
    controller.run()
    
    app.exec_()
    sys.exit()


if __name__ == "__main__":
    main()
