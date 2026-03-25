# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from PyQt5 import QtGui, QtWidgets

if TYPE_CHECKING:
    from views.base_plot_widget import BasePlotWidget

help_text = """
<html>
<head><head/>
<body>
<h1>SCiDA Pro</h1>

<ul>
<li><a href="#general">Introduction</a></li>
<li><a href="#input">Data format requirements</a></li>
<li><a href="#load">How to load and filter IV data</a></li>
<li><a href="#evaluation">How to generate data plots and a data summary report</a></li>
<li><a href="#example">A quick usage example</a></li>
</ul>

<p><h2><a name="general">Introduction</a></h2></p>
<p>
The purpose of the SCiDA Pro program is to help with processing solar cell production data.
It has the following features:
<ul>
<li>Able to handle large data sets in a fast way (e.g. plotting 100k cell data takes a few seconds)</li>
<li>Easy data filtering</li>
<li>Easy generation of a data summary report</li>
<li>Extensive data plotting features</li>
<li>Cross-platform (Windows/Linux/MacOS)</li>
<li>Supports multiple languages</li>
</ul>
</p>

<p><h2><a name="input">Data format requirements</a></h2></p>
<p>
The program accepts Excel files and CSV (comma separated values) files as input.
The filename will become the name of the data set inside the program.
For Excel files with multiple sheets only the first sheet will be read.
When reading the data the program will try to recognize the data labels of the columns, which need to be in the first row of each column.
It will use only the data in the columns that it recognizes and ignores any others.
An appropriate set of data labels could be as follows: Uoc; Isc; RserLfDfIEC; Rsh; FF; Eta; IRev1.
Other data label sets can be selected in the 'Data labels' menu.
Upon reading the input files these alternative data labels will be converted to the default labels.
If the data labels in your files are different than any of the provided sets you can change them in your files and/or contact the program author to add another data label set.
</p>
<p>
While reading the data SCiDA Pro will already apply some data filtering.
Any cells that do not contain a positive number in one of 7 data set columns will be ignored.
The reason for filtering the data in this way is that such inconsistent data values usually indicate a measurement issue.
</p>

<p><h2><a name="load">How to load and filter IV data</a></h2></p>
<p>
The left panel of the main screen is used for loading and managing data sets.
With the three available icons the user can select input files, combine the current data sets into one data set and remove all the currently loaded data sets.
Before loading a data set it may be necessary to select the correct data label set used in the input files in the 'Data labels' menu.
It is possible to rename datasets by double-clicking on an item in the list.
</p>
<p>
When there are data sets available then the right panel can be used to apply data filtering.
To apply the filters on all the data sets simply click on 'Execute filters'.
The data sets that were filtered will change from bold to non-bold to indicate that they have been processed.
The filters are applied one at a time from top to bottom.
The amount of cells that are discarded in this way are recorded for each filter and will be included in the data summary report.
Each filter consists of three elements: an IV parameter name, a smaller or larger symbol and a numerical value.
</p>
<p>
The IV parameter names need to be one of the default names that the program uses internally.
These parameter names are Uoc, Isc, RserLfDfIEC, Rsh, FF, Eta and IRev1.
To check whether all the filter definitions are readable to the program before applying them the user can click on the 'Check filters' icon.
If a filter is unreadable then the program will delete it.
The filter definition list can be manipulated using CTRL-C/CTRL-V and can be saved and loaded using the available buttons.
There is also a 'Reload default filters' button to go back to the default filter definitions.
</p>

<p><h2><a name="evaluation">How to generate data plots and a data summary report</a></h2></p>
<p>
The top button bar can be used to generate a report and to open a new window with data plots.
The 'Make report' button opens a file dialog to save the report and the 'Open report' can be used afterwards to open it directly.
The data report is in the Excel format (xlsx) and will contain the following pages:
<ul>
<li>Summary - contains information such median, average and standard deviation for each data set</li>
<li>Yield loss - if data filtering was applied it shows how many cells were discarded by each filter</li>
<li>Correlation - presents calculated correlaction values for all the main IV parameters (Uoc, Isc, FF, Eta)</li>
</ul>
</p>
<p>
The two dropdown menus in the buttonbar allow the user to select the desired IV parameters to plot and the type of plot. 
For some plot types only the 'Eta' parameter may be available.
Once selected the 'Plot selection' button will open a new window with the data plot.
Depending on the type of plot there are various options available in the top buttonbar, such as showing or hiding selected data sets.
There is a 'Save the figure' button to export the plot to an image file and a 'Edit curve lines and axis parameters' button to manipulate the curves and axes.
</p>

<p><h2><a name="example">A quick usage example</a></h2></p>
<p>
To help you get started the program comes with three CSV data files that contain random IV data.
To process this data you can perform the following steps:
<ol>
<li>Click on the 'Load files' button underneath the 'Data series' panel and select the 'Random IV numbers' data sets</li>
<li>Click on the 'Execute filters' button underneath the right panel to apply the default data filters</li>
<li>Click on 'Make report'  in the top buttonbar and select a file location to save the data summary report</li>
<li>Click on 'Open report' to see the data summary report</li>
<li>Click on 'Plot selection' to open a new window with a boxplot that represents the cell efficiency data</li>
</ol>
</p>

</body>
</html>
"""


class HelpDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        
        self.setWindowTitle(self.tr("Help"))
        vbox = QtWidgets.QVBoxLayout()
        
        browser = QtWidgets.QTextBrowser()
        browser.insertHtml(help_text)
        browser.moveCursor(QtGui.QTextCursor.Start)
        
        vbox.addWidget(browser)
        
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.close)
        hbox.addStretch(1)
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 0, 4)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.setMinimumHeight(576)
        self.setMinimumWidth(1024)


class PlotSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent: 'BasePlotWidget') -> None:
        super().__init__(parent)
        
        self._parent = parent
        
        self.setWindowTitle(self.tr("Plot settings"))
        vbox = QtWidgets.QVBoxLayout()
        
        self.dataset_cb = []
        
        if self._parent.single_dataset:
            for i in range(len(self._parent.ad)):
                self.dataset_cb.append(QtWidgets.QRadioButton(self._parent.ad[i].index.name))
                if i in self._parent.plot_selection:
                    self.dataset_cb[i].setChecked(True)
        else:
            for i in range(len(self._parent.ad)):
                self.dataset_cb.append(QtWidgets.QCheckBox(self._parent.ad[i].index.name))
                if i in self._parent.plot_selection:
                    self.dataset_cb[i].setChecked(True)
        
        group_area = QtWidgets.QGroupBox()
        group_area.setFlat(True)
        group_vbox = QtWidgets.QVBoxLayout()
        
        if self._parent.linewidth_enabled:
            self.linewidth_sb = QtWidgets.QSpinBox()
            self.linewidth_sb.setAccelerated(True)
            self.linewidth_sb.setMaximum(999)
            self.linewidth_sb.setMinimum(1)
            self.linewidth_sb.setValue(self._parent.linewidth_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Line width"))
            hbox.addWidget(self.linewidth_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        if self._parent.dotsize_enabled:
            self.dotsize_sb = QtWidgets.QSpinBox()
            self.dotsize_sb.setAccelerated(True)
            self.dotsize_sb.setMaximum(999)
            self.dotsize_sb.setMinimum(1)
            self.dotsize_sb.setValue(self._parent.dotsize_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Dot size"))
            hbox.addWidget(self.dotsize_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        if self._parent.scatter_enabled:
            self.scatter_sb = QtWidgets.QDoubleSpinBox()
            self.scatter_sb.setAccelerated(True)
            self.scatter_sb.setMaximum(0.5)
            self.scatter_sb.setMinimum(0)
            self.scatter_sb.setSingleStep(0.01)
            self.scatter_sb.setDecimals(2)
            self.scatter_sb.setValue(self._parent.scatter_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Scatter amount"))
            hbox.addWidget(self.scatter_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        if self._parent.title_enabled:
            self.title_cb = QtWidgets.QCheckBox(self.tr("Title"))
            if self._parent.title_selection:
                self.title_cb.setChecked(True)
            group_vbox.addWidget(self.title_cb)
        
        if self._parent.legend_enabled:
            self.legend_cb = QtWidgets.QCheckBox(self.tr("Legend"))
            if self._parent.legend_selection:
                self.legend_cb.setChecked(True)
            group_vbox.addWidget(self.legend_cb)
        
        if self._parent.grid_enabled:
            self.grid_cb = QtWidgets.QCheckBox(self.tr("Grid"))
            if self._parent.grid_selection:
                self.grid_cb.setChecked(True)
            group_vbox.addWidget(self.grid_cb)
        
        group_area.setLayout(group_vbox)
        
        if (self._parent.grid_enabled or self._parent.legend_enabled or 
                self._parent.title_enabled or self._parent.dotsize_enabled or 
                self._parent.linewidth_enabled or self._parent.scatter_enabled):
            vbox.addWidget(group_area)
        
        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()
        
        for i in range(len(self.dataset_cb)):
            self.dataset_cb[i].setMinimumWidth(400)
            checkbox_vbox.addWidget(self.dataset_cb[i])
        
        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)
        
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttonbox.accepted.connect(self._read)
        buttonbox.rejected.connect(self.reject)
        hbox.addStretch(1)
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 0, 4)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.setMinimumWidth(800)
    
    def _read(self) -> None:
        if self._parent.title_enabled:
            self._parent.title_selection = self.title_cb.isChecked()
        
        if self._parent.legend_enabled:
            self._parent.legend_selection = self.legend_cb.isChecked()
        
        if self._parent.grid_enabled:
            self._parent.grid_selection = self.grid_cb.isChecked()
        
        if self._parent.dotsize_enabled:
            self._parent.dotsize_selection = self.dotsize_sb.value()
        
        if self._parent.linewidth_enabled:
            self._parent.linewidth_selection = self.linewidth_sb.value()
        
        if self._parent.scatter_enabled:
            self._parent.scatter_selection = self.scatter_sb.value()
        
        self._parent.plot_selection = []
        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                self._parent.plot_selection.append(i)
        
        self._parent.on_draw()
        self.close()
