# -*- coding: utf-8 -*-
"""
Statistical Plots for SCiDA Pro
Contains box plot, violin plot, and histogram widgets
"""

from __future__ import division
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget
from utils import ConfigManager


class IVBoxPlot(BasePlotWidget):
    """Box Plot Widget"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        super().__init__(parent, title="Boxplot", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        self._dotsize_enabled = False
        self._linewidth_enabled = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_ylabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_xlabel("Data set", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot box plots for selected datasets"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        plot_selection_list = self._config.get_plot_selection_list()
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        box_data = []
        box_labels = []
        
        for ds_id in self._plot_selection:
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            values = dataset.get_column(column)
            box_data.append(values.values)
            box_labels.append(f"{dataset.name}\n(n={len(values)})")
        
        if box_data:
            box_plot = self._axes.boxplot(
                box_data,
                patch_artist=True,
                labels=box_labels
            )
            
            # Color boxes
            for i, patch in enumerate(box_plot['boxes']):
                patch.set_facecolor(self._get_color(i))


class ViolinPlot(BasePlotWidget):
    """Violin Plot Widget"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        super().__init__(parent, title="Violinplot", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        self._dotsize_enabled = False
        self._linewidth_enabled = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_ylabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_xlabel("Data set", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot violin plots for selected datasets"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        plot_selection_list = self._config.get_plot_selection_list()
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        violin_data = []
        violin_labels = []
        
        for ds_id in self._plot_selection:
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            values = dataset.get_column(column)
            violin_data.append(values.values)
            violin_labels.append(f"{dataset.name}\n(n={len(values)})")
        
        if violin_data:
            violin_parts = self._axes.violinplot(
                violin_data,
                showmeans=False,
                showmedians=True
            )
            
            # Color violins
            for i, pc in enumerate(violin_parts['bodies']):
                pc.set_facecolor(self._get_color(i))
                pc.set_alpha(0.8)
            
            # Set x-tick labels
            self._axes.set_xticks(np.arange(1, len(violin_labels) + 1))
            self._axes.set_xticklabels(violin_labels)


class IVHistPlot(BasePlotWidget):
    """Histogram Plot Widget"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        super().__init__(parent, title="Histogram", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        self._dotsize_enabled = False
        self._linewidth_enabled = False
        
        # Initialize plot selection (all datasets by default)
        self._plot_selection = []
        if hasattr(self._parent, 'data_collection'):
            for ds_id, _ in self._parent.data_collection.items():
                self._plot_selection.append(ds_id)
    
    def _setup_axes(self) -> None:
        """Setup axes labels"""
        plot_selection_list = self._config.get_plot_selection_list()
        plot_label_list = self._config.get_plot_label_list()
        plot_labels = self._config.get_plot_labels()
        
        if 0 <= self._selection < len(plot_selection_list):
            label_key = plot_label_list[self._selection]
            self._axes.set_xlabel(plot_labels.get(label_key, ''), fontsize=24)
        
        self._axes.set_ylabel("Frequency", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot histograms"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        plot_selection_list = self._config.get_plot_selection_list()
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        
        # Determine bin range from all data
        all_values = []
        for ds_id in self._plot_selection:
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is not None and not dataset.is_empty():
                values = dataset.get_column(column)
                all_values.extend(values.values)
        
        if not all_values:
            return
        
        bin_range = (np.min(all_values), np.max(all_values))
        bins = 30
        
        # Plot each histogram
        for i, ds_id in enumerate(self._plot_selection):
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            values = dataset.get_column(column)
            
            self._axes.hist(
                values.values,
                bins=bins,
                range=bin_range,
                histtype='step',
                linewidth=2,
                color=self._get_color(i),
                label=dataset.name
            )


class IVHistDenPlot(BasePlotWidget):
    """Histogram + Density Plot Widget"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        self._colors = ConfigManager().get_colors()
        super().__init__(parent, title="Histogram + density", two_axes=True)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = True
        self._dotsize_enabled = False
        self._linewidth_enabled = False
        
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
        
        self._axes.set_ylabel("Frequency", fontsize=24)
        if self._axes2:
            self._axes2.set_ylabel("Density", fontsize=24)
    
    def _plot_data(self) -> None:
        """Plot histogram with density curve"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        if not self._plot_selection:
            return
        
        ds_id = self._plot_selection[0]
        dataset = self._parent.data_collection.get_dataset(ds_id)
        if dataset is None or dataset.is_empty():
            return
        
        plot_selection_list = self._config.get_plot_selection_list()
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        values = dataset.get_column(column)
        
        # Plot histogram on primary axis
        n, bins, patches = self._axes.hist(
            values.values,
            bins=30,
            color=self._get_color(0),
            alpha=0.7,
            label='Histogram'
        )
        
        # Plot density curve on secondary axis
        if self._axes2 and len(values) > 1:
            try:
                from scipy.stats import gaussian_kde
                
                kde = gaussian_kde(values)
                x_vals = np.linspace(values.min(), values.max(), 1000)
                density = kde(x_vals)
                
                self._axes2.plot(
                    x_vals, density,
                    color=self._get_color(1),
                    linewidth=3,
                    label='Density'
                )
            except ImportError:
                # Fall back to simple density if scipy not available
                pass
