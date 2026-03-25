# -*- coding: utf-8 -*-
"""
Base Plot Widget for SCiDA Pro
Abstract base class for all plot widgets using Template Method pattern
"""

# Note: Using explicit NotImplementedError instead of ABC due to
# metaclass conflicts with PyQt's QMainWindow
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
from PyQt5 import QtGui, QtWidgets

from utils import ConfigManager

# Configure matplotlib
rcParams.update({'figure.autolayout': True})
font = {'family': 'sans-serif', 'size': 14}
matplotlib.rc('font', **font)


class BasePlotWidget(QtWidgets.QMainWindow):
    """
    Abstract base class for all plot widgets
    Implements Template Method pattern for common plot functionality
    """
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, 
                 title: str = "Plot", 
                 two_axes: bool = False):
        """
        Initialize base plot widget
        Args:
            parent: Parent widget
            title: Window title
            two_axes: Whether to create a secondary Y-axis
        """
        super().__init__(parent)
        self._parent = parent
        self._config = ConfigManager()
        
        # Plot configuration
        self._title = title
        self._two_axes = two_axes
        self._single_dataset = False
        self._colors = self._config.get_colors()
        
        # Plot selection and settings
        self._plot_selection: List[int] = []
        self._title_enabled = False
        self._title_selection = False
        self._grid_enabled = True
        self._grid_selection = True
        self._legend_enabled = True
        self._legend_selection = True
        self._dotsize_enabled = True
        self._dotsize_selection = 20
        self._linewidth_enabled = False
        self._linewidth_selection = 3
        self._scatter_enabled = False
        self._scatter_selection = 0.5
        
        # Figure components
        self._main_frame: Optional[QtWidgets.QWidget] = None
        self._fig: Optional[Figure] = None
        self._canvas: Optional[FigureCanvas] = None
        self._axes: Optional[matplotlib.axes.Axes] = None
        self._axes2: Optional[matplotlib.axes.Axes] = None
        self._mpl_toolbar: Optional[NavigationToolbar] = None
        self._status_text: Optional[QtWidgets.QLabel] = None
        
        # Initialize UI
        self.setWindowTitle(self.tr(title))
        self._setup_window_geometry()
        self._create_menu()
        self._create_main_frame()
        
        # Template method: call plot-specific initialization
        self._plot_specific_init()
        
        # Draw plot
        self.on_draw()
    
    def _setup_window_geometry(self) -> None:
        """Setup window size and position (concrete method)"""
        window_size = self._config.get_app_setting('plot_window_size', [1020, 752])
        self.resize(window_size[0], window_size[1])
        
        frame_geom = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())
    
    def _create_menu(self) -> None:
        """Create menu bar (concrete method)"""
        self.file_menu = self.menuBar().addMenu(self.tr("File"))
        tip = self.tr("Quit")
        quit_action = QtWidgets.QAction(tip, self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')
        self.file_menu.addAction(quit_action)
    
    def _create_main_frame(self) -> None:
        """Create main frame with plot canvas and toolbar (concrete method)"""
        self._main_frame = QtWidgets.QWidget()
        
        # Create matplotlib figure and canvas
        dpi = self._config.get_app_setting('dpi', 100)
        fig_size = self._config.get_app_setting('figure_size', [10.0, 10.0])
        
        self._fig = Figure((fig_size[0], fig_size[1]), dpi=dpi, facecolor='White')
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setParent(self._main_frame)
        
        # Create axes
        self._axes = self._fig.add_subplot(111, facecolor='White')
        if self._two_axes:
            self._axes2 = self._axes.twinx()
        
        # Create navigation toolbar
        self._mpl_toolbar = NavigationToolbar(self._canvas, self._main_frame)
        
        # Create plot settings button
        settings_button = QtWidgets.QPushButton()
        settings_button.clicked.connect(self._show_plot_settings)
        settings_button.setIcon(QtGui.QIcon(":gear.png"))
        settings_button.setToolTip(self.tr("Plot settings"))
        settings_button.setStatusTip(self.tr("Plot settings"))
        
        # Add button to toolbar
        self._mpl_toolbar.addWidget(settings_button)
        
        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._mpl_toolbar)
        vbox.addWidget(self._canvas)
        
        self._main_frame.setLayout(vbox)
        self.setCentralWidget(self._main_frame)
        
        # Status bar
        self._status_text = QtWidgets.QLabel("")
        self.statusBar().addWidget(self._status_text, 1)
    
    def _show_plot_settings(self) -> None:
        """Show plot settings dialog"""
        from .plot_settings_dialog import PlotSettingsDialog
        dialog = PlotSettingsDialog(self)
        dialog.setModal(True)
        dialog.show()
    
    def _get_color(self, index: int) -> str:
        """Get color for given index (cycles through color list)"""
        return self._colors[index % len(self._colors)]
    
    def _plot_specific_init(self) -> None:
        """
        Plot-specific initialization (abstract method)
        Override in subclasses to set plot-specific configuration
        """
        raise NotImplementedError(
            "Subclasses must implement _plot_specific_init method"
        )
    
    def _setup_axes(self) -> None:
        """
        Setup axes labels, limits, etc. (abstract method)
        Override in subclasses to configure plot-specific axes
        """
        raise NotImplementedError(
            "Subclasses must implement _setup_axes method"
        )
    
    def _plot_data(self) -> None:
        """
        Plot the data (abstract method)
        Override in subclasses to implement specific plotting logic
        """
        raise NotImplementedError(
            "Subclasses must implement _plot_data method"
        )
    
    def _add_legend(self) -> None:
        """Add legend to plot (hook method - can be overridden)"""
        if self._legend_selection and hasattr(self, '_parent') and hasattr(self._parent, 'data_collection'):
            handles, labels = self._axes.get_legend_handles_labels()
            if handles:
                self._axes.legend(
                    loc='lower left',
                    scatterpoints=1,
                    markerscale=3,
                    frameon=False
                )
    
    def _add_title(self) -> None:
        """Add title to plot (hook method - can be overridden)"""
        if self._title_selection and self._plot_selection:
            first_id = self._plot_selection[0]
            if hasattr(self._parent, 'data_collection'):
                dataset = self._parent.data_collection.get_dataset(first_id)
                if dataset:
                    self._axes.set_title(dataset.name)
    
    def on_draw(self) -> None:
        """
        Template method for drawing the plot
        Defines the algorithm skeleton for plotting
        """
        # Clear previous plot
        self._axes.clear()
        if self._axes2:
            self._axes2.clear()
        
        # Apply grid setting (concrete step)
        self._axes.grid(self._grid_selection)
        if self._axes2:
            self._axes2.grid(False)
        
        # Setup axes (abstract step)
        self._setup_axes()
        
        # Plot data (abstract step)
        self._plot_data()
        
        # Add title (hook step)
        self._add_title()
        
        # Add legend (hook step)
        self._add_legend()
        
        # Refresh canvas (concrete step)
        self._canvas.draw()
    
    # Property getters/setters for plot settings
    @property
    def single_dataset(self) -> bool:
        return self._single_dataset
    
    @property
    def plot_selection(self) -> List[int]:
        return self._plot_selection
    
    @plot_selection.setter
    def plot_selection(self, value: List[int]) -> None:
        self._plot_selection = value
    
    @property
    def title_enabled(self) -> bool:
        return self._title_enabled
    
    @property
    def title_selection(self) -> bool:
        return self._title_selection
    
    @title_selection.setter
    def title_selection(self, value: bool) -> None:
        self._title_selection = value
    
    @property
    def grid_enabled(self) -> bool:
        return self._grid_enabled
    
    @property
    def grid_selection(self) -> bool:
        return self._grid_selection
    
    @grid_selection.setter
    def grid_selection(self, value: bool) -> None:
        self._grid_selection = value
    
    @property
    def legend_enabled(self) -> bool:
        return self._legend_enabled
    
    @property
    def legend_selection(self) -> bool:
        return self._legend_selection
    
    @legend_selection.setter
    def legend_selection(self, value: bool) -> None:
        self._legend_selection = value
    
    @property
    def dotsize_enabled(self) -> bool:
        return self._dotsize_enabled
    
    @property
    def dotsize_selection(self) -> int:
        return self._dotsize_selection
    
    @dotsize_selection.setter
    def dotsize_selection(self, value: int) -> None:
        self._dotsize_selection = value
    
    @property
    def linewidth_enabled(self) -> bool:
        return self._linewidth_enabled
    
    @property
    def linewidth_selection(self) -> int:
        return self._linewidth_selection
    
    @linewidth_selection.setter
    def linewidth_selection(self, value: int) -> None:
        self._linewidth_selection = value
    
    @property
    def scatter_enabled(self) -> bool:
        return self._scatter_enabled
    
    @property
    def scatter_selection(self) -> float:
        return self._scatter_selection
    
    @scatter_selection.setter
    def scatter_selection(self, value: float) -> None:
        self._scatter_selection = value
    
    @property
    def data_collection(self) -> Any:
        """Get data collection from parent (for backwards compatibility)"""
        if hasattr(self._parent, 'data_collection'):
            return self._parent.data_collection
        return None
    
    @property
    def ad(self) -> Dict[int, pd.DataFrame]:
        """
        Legacy property for backwards compatibility with PlotSettingsDialog
        Returns dictionary of dataset IDs to DataFrames
        """
        result = {}
        if hasattr(self._parent, 'data_collection'):
            for ds_id, dataset in self._parent.data_collection.items():
                result[ds_id] = dataset.data
                result[ds_id].index.name = dataset.name
        return result
