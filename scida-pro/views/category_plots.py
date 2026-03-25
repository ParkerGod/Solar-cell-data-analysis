# -*- coding: utf-8 -*-
"""
Category Plots for SCiDA Pro
Contains category scatter plot widget
"""

from __future__ import division
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget
from utils import ConfigManager


class CategoryScatter(BasePlotWidget):
    """Category Scatter Plot Widget"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, plot_selection: int = 0):
        self._selection = plot_selection
        super().__init__(parent, title="Category scatter", two_axes=False)
    
    def _plot_specific_init(self) -> None:
        """Initialize plot-specific settings"""
        self._single_dataset = False
        self._scatter_enabled = True
        self._legend_enabled = False
        
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
        """Plot category scatter plot"""
        if not hasattr(self._parent, 'data_collection'):
            return
        
        plot_selection_list = self._config.get_plot_selection_list()
        if self._selection >= len(plot_selection_list):
            return
        
        column = plot_selection_list[self._selection]
        xtick_labels = []
        
        for i, ds_id in enumerate(self._plot_selection):
            dataset = self._parent.data_collection.get_dataset(ds_id)
            if dataset is None or dataset.is_empty():
                continue
            
            values = dataset.get_column(column)
            
            # Create x positions with scatter
            x_pos = np.full(len(values), i + 1)
            if self._scatter_selection > 0:
                x_pos += np.random.uniform(
                    -self._scatter_selection,
                    self._scatter_selection,
                    size=len(values)
                )
            
            # Plot scatter points
            self._axes.scatter(
                x_pos, values,
                s=self._dotsize_selection,
                c=self._get_color(i),
                alpha=0.6,
                label=dataset.name
            )
            
            # Add median line
            median_val = values.median()
            self._axes.plot(
                [i + 0.7, i + 1.3],
                [median_val, median_val],
                color='black',
                linestyle='-',
                linewidth=2
            )
            
            xtick_labels.append(f"{dataset.name}\n(n={len(values)})")
        
        # Set x-ticks
        if xtick_labels:
            self._axes.set_xticks(np.arange(1, len(xtick_labels) + 1))
            self._axes.set_xticklabels(xtick_labels)
