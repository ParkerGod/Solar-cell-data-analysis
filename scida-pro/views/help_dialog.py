# -*- coding: utf-8 -*-
"""
Help Dialog for SCiDA Pro
About and Help dialogs
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class HelpDialog(QtWidgets.QDialog):
    """Help and About dialogs"""
    
    # About dialog content
    ABOUT_HTML = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; }
            h1 { color: #2c3e50; }
            .version { color: #7f8c8d; font-size: small; }
        </style>
    </head>
    <body>
        <h1>SCiDA Pro</h1>
        <p class="version">Version 2.0</p>
        <p><strong>Solar Cell Data Analysis</strong></p>
        <p>A tool for analyzing and visualizing solar cell IV measurement data.</p>
        <p>&nbsp;</p>
        <p><strong>Features:</strong></p>
        <ul>
            <li>Multiple data set comparison</li>
            <li>Statistical analysis</li>
            <li>Various visualization types</li>
            <li>Data filtering</li>
            <li>Excel report generation</li>
        </ul>
        <p>&nbsp;</p>
        <p>© 2024 SCiDA Pro</p>
    </body>
    </html>
    """
    
    # Help dialog content
    HELP_HTML = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; line-height: 1.6; }
            h1, h2, h3 { color: #2c3e50; }
            .note { background: #f8f9fa; padding: 10px; border-left: 4px solid #2c3e50; }
        </style>
    </head>
    <body>
        <h1>SCiDA Pro Help</h1>
        
        <h2>Getting Started</h2>
        <p>To begin analyzing your solar cell data:</p>
        <ol>
            <li>Click the <strong>Open</strong> button or use <em>File &gt; Open...</em></li>
            <li>Select one or more CSV or Excel files containing your IV measurement data</li>
            <li>Your data will be loaded and displayed in the table</li>
        </ol>
        
        <h2>Data Format</h2>
        <p>Your data files should contain at least the following columns:</p>
        <ul>
            <li><strong>Uoc</strong> or <strong>Voc</strong> - Open circuit voltage [V]</li>
            <li><strong>Isc</strong> - Short circuit current [A]</li>
            <li><strong>FF</strong> - Fill factor [%]</li>
            <li><strong>Eta</strong> or <strong>Eff</strong> - Efficiency [%]</li>
            <li><strong>Rser</strong> or <strong>Rs</strong> - Series resistance [Ohm]</li>
            <li><strong>Rsh</strong> or <strong>Rshunt</strong> - Shunt resistance [Ohm]</li>
            <li><strong>IRev</strong> or <strong>Irev</strong> - Reverse current [A]</li>
        </ul>
        
        <h2>Filtering Data</h2>
        <p>Use the filter panel to exclude outlier cells from your analysis:</p>
        <ol>
            <li>Enable filters by checking the checkbox</li>
            <li>Select the parameter to filter</li>
            <li>Choose the operator (&lt; or &gt;)</li>
            <li>Enter the threshold value</li>
            <li>Click <strong>Apply filter to all data sets</strong></li>
        </ol>
        
        <div class="note">
            <strong>Note:</strong> Filters are applied in sequence. Cells that do not meet
            the filter criteria are removed from the analysis.
        </div>
        
        <h2>Creating Plots</h2>
        <p>To visualize your data:</p>
        <ol>
            <li>Select a <strong>Plot type</strong> from the dropdown menu</li>
            <li>Select the <strong>Data property</strong> to plot</li>
            <li>Click <strong>Add plot</strong></li>
        </ol>
        
        <p>Available plot types:</p>
        <ul>
            <li><strong>Boxplot/Violinplot</strong> - Statistical distribution</li>
            <li><strong>Category scatter</strong> - Individual cell values</li>
            <li><strong>Walk-through/Rolling mean</strong> - Spatial distribution</li>
            <li><strong>Low to high</strong> - Sorted values</li>
            <li><strong>Histogram/Density</strong> - Value frequency</li>
            <li><strong>Voc-Isc/Eta-FF/Rsh-FF</strong> - Correlation plots</li>
        </ul>
        
        <h2>Generating Reports</h2>
        <p>Click <strong>Create report</strong> to generate an Excel file containing:</p>
        <ul>
            <li>Summary statistics</li>
            <li>Yield loss analysis</li>
            <li>Correlation matrices</li>
        </ul>
        
        <h2>Keyboard Shortcuts</h2>
        <ul>
            <li><strong>Ctrl+O</strong> - Open data file(s)</li>
            <li><strong>Ctrl+Q</strong> - Quit application</li>
        </ul>
    </body>
    </html>
    """
    
    @staticmethod
    def show_about(parent: QtWidgets.QWidget) -> None:
        """Show about dialog"""
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("About SCiDA Pro")
        dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Text browser
        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(HelpDialog.ABOUT_HTML)
        text_browser.setMinimumSize(400, 300)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        
        # Button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    @staticmethod
    def show_help(parent: QtWidgets.QWidget) -> None:
        """Show help dialog"""
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("SCiDA Pro Help")
        dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Text browser
        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(HelpDialog.HELP_HTML)
        text_browser.setMinimumSize(600, 500)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        
        # Button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
