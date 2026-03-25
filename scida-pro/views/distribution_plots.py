# -*- coding: utf-8 -*-
"""
Distribution Plots for SCiDA Pro
Contains distribution plot widgets (Low to High, Density, Walk-through, Rolling Mean)
"""

from __future__ import division
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget
from utils import ConfigManager


class DistLtoH(BasePlotWidget):
    """Low to High Distribution Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        self._colors = ConfigManager().get_colors()
        super().__init__(parent, title="Low to high", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = True
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        
        # Initialize plot selection (first dataset by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
                break  # Only take first dataset
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_ylabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_xlabel("Cell index", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot low to high distribution"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        if not self._plot_selection:
            return
        
        ds_id = self._plot_selection[0]
        dataset = self._parent.data_collection.get_dataset(ds_id)
        if dataset is None or dataset.is_empty():
            return
        
        data = dataset.data
        plot_selection_list = self._config.get_plot_selection_list()
        
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        values = dataset.get_column(column)
        
        # Sort values
        sorted_vals = np.sort(values.values)
        x_vals = np.arange(1, len(sorted_vals) + 1)
        
        # Plot with specific color from cycle (index 1)
        self._axes.plot(
            x_vals, sorted_vals,
            color=self._get_color(1),
            linewidth=self._linewidth_selection,
            label=column
        )


class DensEta(BasePlotWidget):
    """Eta Density Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        self._colors = ConfigManager().get_colors()
        super().__init__(parent, title="Density", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = True
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        
        # Initialize plot selection (first dataset by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
                break  # Only take first dataset
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_xlabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_yticks([])
        self._axes.set_yticklabels([])
    
    def _plot_data(self) -> None:
        """Plot density distribution"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        if not self._plot_selection:
            return
        
        ds_id = self._plot_selection[0]
        dataset = self._parent.data_collection.get_dataset(ds_id)
        if dataset is None or dataset.is_empty():
            return
        
        data = dataset.data
        plot_selection_list = self._config.get_plot_selection_list()
        
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        values = dataset.get_column(column)
        
        # Create KDE-like density plot
        from scipy.stats import gaussian_kde
        
        kde = gaussian_kde(values)
        x_vals = np.linspace(values.min(), values.max(), 1000)
        density = kde(x_vals)
        
        # Plot with specific color from cycle (index 1)
        self._axes.fill_between(
            x_vals, density,
            alpha=0.7,
            color=self._get_color(1),
            label=column
        )
        self._axes.plot(
            x_vals, density,
            color='black',
            linewidth=self._linewidth_selection
        )


class DistWT(BasePlotWidget):
    """Walk-through Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        super().__init__(parent, title="Walk-through", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = True
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        
        # Initialize plot selection (first dataset by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
                break  # Only take first dataset
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_ylabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_xlabel("Cell index", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot walk-through (unsorted data)"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        if not self._plot_selection:
            return
        
        ds_id = self._plot_selection[0]
        dataset = self._parent.data_collection.get_dataset(ds_id)
        if dataset is None or dataset.is_empty():
            return
        
        data = dataset.data
        plot_selection_list = self._config.get_plot_selection_list()
        
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        values = dataset.get_column(column)
        
        x_vals = np.arange(1, len(values) + 1)
        
        # Plot
        self._axes.plot(
            x_vals, values,
            color=self._get_color(0),
            linewidth=self._linewidth_selection,
            label=column
        )


class DistRM(BasePlotWidget):
    """Rolling Mean Plot"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        self._colors = ConfigManager().get_colors()
        super().__init__(parent, title="Rolling mean", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = True
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        
        # Initialize plot selection (first dataset by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
                break  # Only take first dataset
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_ylabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_xlabel("Cell index", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot rolling mean"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        if not self._plot_selection:
            return
        
        ds_id = self._plot_selection[0]
        dataset = self._parent.data_collection.get_dataset(ds_id)
        if dataset is None or dataset.is_empty():
            return
        
        data = dataset.data
        plot_selection_list = self._config.get_plot_selection_list()
        
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        values = dataset.get_column(column)
        
        # Calculate rolling mean
        window_size = max(1, len(values) // 20)  # 5% window
        rolling_mean = values.rolling(window=window_size, center=True).mean()
        
        x_vals = np.arange(1, len(values) + 1)
        
        # Plot raw data in gray
        self._axes.plot(
            x_vals, values,
            color='0.7',
            linewidth=1,
            alpha=0.5
        )
        
        # Plot rolling mean with specific color from cycle (index 1)
        self._axes.plot(
            x_vals, rolling_mean,
            color=self._get_color(1),
            linewidth=self._linewidth_selection,
            label=f"Rolling mean (window={window_size})"
        )
