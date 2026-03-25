# -*- coding: utf-8 -*-
"""
Correlation Plots for SCiDA Pro
Contains correlation scatter plot widgets (Voc-Isc, Eta-FF, Rsh-FF)
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget
from utils import ConfigManager


class CorrVocIsc(BasePlotWidget):
    """Voc vs Isc Correlation Scatter Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent, title="Correlation", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_labels = self._config.get_plot_labels()
        self._axes.set_ylabel(plot_labels.get('voc_axis_label', r'$\mathrm{\mathsf{V_{OC}}}$ [V]'), fontsize=24)
        self._axes.set_xlabel(plot_labels.get('isc_axis_label', r'$\mathrm{\mathsf{I_{SC}}}$ [A]'), fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot Voc vs Isc scatter data"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        for i, ds_id in enumerate(self._plot_selection):
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            data = dataset.data
            if not {'Isc', 'Uoc'}.issubset(data.columns):
                continue
            
            self._axes.scatter(
                data['Isc'], data['Uoc'],
                s=self._dotsize_selection,
                c=self._get_color(i),
                label=dataset.name
            )


class CorrEtaFF(BasePlotWidget):
    """Eta vs FF Correlation Scatter Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent, title="Correlation", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_labels = self._config.get_plot_labels()
        self._axes.set_ylabel(plot_labels.get('eta_axis_label', r'$\mathrm{\mathsf{Eta}}$ [%]'), fontsize=24)
        self._axes.set_xlabel(plot_labels.get('ff_axis_label', r'$\mathrm{\mathsf{FF}}$ [%]'), fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot Eta vs FF scatter data"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        for i, ds_id in enumerate(self._plot_selection):
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            data = dataset.data
            if not {'FF', 'Eta'}.issubset(data.columns):
                continue
            
            self._axes.scatter(
                data['FF'], data['Eta'],
                s=self._dotsize_selection,
                c=self._get_color(i),
                label=dataset.name
            )


class CorrRshFF(BasePlotWidget):
    """Rsh vs FF Correlation Scatter Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent, title="Correlation", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_labels = self._config.get_plot_labels()
        self._axes.set_ylabel(plot_labels.get('rshunt_axis_label', r'$\mathrm{\mathsf{R_{SHUNT}}}$ [kOhm]'), fontsize=24)
        self._axes.set_xlabel(plot_labels.get('ff_axis_label', r'$\mathrm{\mathsf{FF}}$ [%]'), fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot Rsh vs FF scatter data"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        for i, ds_id in enumerate(self._plot_selection):
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            data = dataset.data
            if not {'FF', 'Rsh'}.issubset(data.columns):
                continue
            
            # Convert Rsh to kOhm
            rsh_kohm = data['Rsh'] * 0.001
            
            self._axes.scatter(
                data['FF'], rsh_kohm,
                s=self._dotsize_selection,
                c=self._get_color(i),
                label=dataset.name
            )
