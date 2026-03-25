# -*- coding: utf-8 -*-
"""
Plot Settings Dialog for SCiDA Pro
Dialog for configuring plot settings
"""

from __future__ import division
from typing import Any, List
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget


class PlotSettingsDialog(QtWidgets.QDialog):
    """Dialog for configuring plot settings"""
    
    def __init__(self, parent: BasePlotWidget):
        """
        Initialize plot settings dialog
        Args:
            parent: Parent plot widget
        """
        super().__init__(parent)
        self._parent = parent
        
        self.setWindowTitle(self.tr("Plot settings"))
        vbox = QtWidgets.QVBoxLayout()
        
        self._dataset_cb: List[QtWidgets.QAbstractButton] = []
        
        # Create dataset selection checkboxes/radio buttons
        if self._parent.single_dataset:
            # Use radio buttons for single dataset plots
            for i in range(len(self._parent.ad)):
                if i in self._parent.ad:
                    name = self._parent.ad[i].index.name
                else:
                    name = f"Dataset {i}"
                self._dataset_cb.append(QtWidgets.QRadioButton(name))
                if i in self._parent.plot_selection:
                    self._dataset_cb[i].setChecked(True)
        else:
            # Use checkboxes for multi-dataset plots
            for i in range(len(self._parent.ad)):
                if i in self._parent.ad:
                    name = self._parent.ad[i].index.name
                else:
                    name = f"Dataset {i}"
                self._dataset_cb.append(QtWidgets.QCheckBox(name))
                if i in self._parent.plot_selection:
                    self._dataset_cb[i].setChecked(True)
        
        group_area = QtWidgets.QGroupBox()
        group_area.setFlat(True)
        group_vbox = QtWidgets.QVBoxLayout()
        
        # Line width setting
        if self._parent.linewidth_enabled:
            self._linewidth_sb = QtWidgets.QSpinBox()
            self._linewidth_sb.setAccelerated(True)
            self._linewidth_sb.setMaximum(999)
            self._linewidth_sb.setMinimum(1)
            self._linewidth_sb.setValue(self._parent.linewidth_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Line width"))
            hbox.addWidget(self._linewidth_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # Dot size setting
        if self._parent.dotsize_enabled:
            self._dotsize_sb = QtWidgets.QSpinBox()
            self._dotsize_sb.setAccelerated(True)
            self._dotsize_sb.setMaximum(999)
            self._dotsize_sb.setMinimum(1)
            self._dotsize_sb.setValue(self._parent.dotsize_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Dot size"))
            hbox.addWidget(self._dotsize_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # Scatter amount setting
        if self._parent.scatter_enabled:
            self._scatter_sb = QtWidgets.QDoubleSpinBox()
            self._scatter_sb.setAccelerated(True)
            self._scatter_sb.setMaximum(0.5)
            self._scatter_sb.setMinimum(0)
            self._scatter_sb.setSingleStep(0.01)
            self._scatter_sb.setDecimals(2)
            self._scatter_sb.setValue(self._parent.scatter_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Scatter amount"))
            hbox.addWidget(self._scatter_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # Title setting
        if self._parent.title_enabled:
            self._title_cb = QtWidgets.QCheckBox(self.tr("Title"))
            if self._parent.title_selection:
                self._title_cb.setChecked(True)
            group_vbox.addWidget(self._title_cb)
        
        # Legend setting
        if self._parent.legend_enabled:
            self._legend_cb = QtWidgets.QCheckBox(self.tr("Legend"))
            if self._parent.legend_selection:
                self._legend_cb.setChecked(True)
            group_vbox.addWidget(self._legend_cb)
        
        # Grid setting
        if self._parent.grid_enabled:
            self._grid_cb = QtWidgets.QCheckBox(self.tr("Grid"))
            if self._parent.grid_selection:
                self._grid_cb.setChecked(True)
            group_vbox.addWidget(self._grid_cb)
        
        group_area.setLayout(group_vbox)
        
        # Add settings group to layout if there are any settings
        if (self._parent.grid_enabled or self._parent.legend_enabled or 
            self._parent.title_enabled or self._parent.dotsize_enabled or 
            self._parent.linewidth_enabled or self._parent.scatter_enabled):
            vbox.addWidget(group_area)
        
        # Create scrollable area for dataset selection
        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()
        
        for cb in self._dataset_cb:
            cb.setMinimumWidth(400)  # Prevent obscured text
            checkbox_vbox.addWidget(cb)
        
        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        scroll_area.setWidgetResizable(True)
        vbox.addWidget(scroll_area)
        
        # Button box for OK/Cancel
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttonbox.accepted.connect(self._read_settings)
        buttonbox.rejected.connect(self.reject)
        hbox.addStretch(1)
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 0, 4)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.setMinimumWidth(800)
    
    def _read_settings(self) -> None:
        """Read settings from dialog and apply to parent plot"""
        # Apply settings to parent plot
        if self._parent.title_enabled:
            self._parent.title_selection = self._title_cb.isChecked()
        
        if self._parent.legend_enabled:
            self._parent.legend_selection = self._legend_cb.isChecked()
        
        if self._parent.grid_enabled:
            self._parent.grid_selection = self._grid_cb.isChecked()
        
        if self._parent.dotsize_enabled:
            self._parent.dotsize_selection = self._dotsize_sb.value()
        
        if self._parent.linewidth_enabled:
            self._parent.linewidth_selection = self._linewidth_sb.value()
        
        if self._parent.scatter_enabled:
            self._parent.scatter_selection = self._scatter_sb.value()
        
        # Update plot selection
        self._parent.plot_selection = []
        for i in range(len(self._dataset_cb)):
            if self._dataset_cb[i].isChecked():
                self._parent.plot_selection.append(i)
        
        # Redraw the plot
        self._parent.on_draw()
        self.close()
