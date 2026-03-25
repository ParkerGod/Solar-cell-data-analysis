# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from PyQt5 import QtGui, QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams

from utils import get_config, get_logger

rcParams.update({'figure.autolayout': True})

font = {'family': 'sans-serif', 'size': 14}
matplotlib.rc('font', **font)


class CombinedMeta(type(QtWidgets.QMainWindow), ABCMeta):
    pass


class BasePlotWidget(QtWidgets.QMainWindow, metaclass=CombinedMeta):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        title: str = "Plot"
    ) -> None:
        super().__init__(parent)
        
        self._config = get_config()
        self._logger = get_logger()
        
        self.setWindowTitle(self.tr(title))
        self._setup_window_geometry()
        
        self._data = data if data is not None else {}
        self._plot_selection: List[int] = []
        self._colors = self._config.colors
        
        self._init_plot_settings()
        self._create_menu()
        self._create_main_frame()
        self._init_plot_selection()
    
    def _setup_window_geometry(self) -> None:
        self.resize(1020, 752)
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    
    def _init_plot_settings(self) -> None:
        plot_settings = self._config.plot_settings
        
        self._single_dataset: bool = False
        self._title_enabled: bool = False
        self._title_selection: bool = True
        self._grid_enabled: bool = True
        self._grid_selection: bool = True
        self._legend_enabled: bool = True
        self._legend_selection: bool = True
        self._dotsize_enabled: bool = True
        self._dotsize_selection: int = plot_settings.get('default_dot_size', 20)
        self._linewidth_enabled: bool = False
        self._linewidth_selection: int = plot_settings.get('default_line_width', 3)
        self._scatter_enabled: bool = False
        self._scatter_selection: float = plot_settings.get('default_scatter_amount', 0.5)
        
        self._font_size: int = plot_settings.get('font_size', 24)
        self._font_weight: str = plot_settings.get('font_weight', 'black')
        self._tick_pad: int = plot_settings.get('tick_pad', 8)
    
    def _init_plot_selection(self) -> None:
        self._plot_selection = list(range(len(self._data)))
    
    def _create_main_frame(self, two_axes: bool = False) -> None:
        self.main_frame = QtWidgets.QWidget()
        
        plot_settings = self._config.plot_settings
        dpi = plot_settings.get('dpi', 100)
        fig_size = plot_settings.get('figure_size', [10.0, 10.0])
        facecolor = plot_settings.get('facecolor', 'White')
        
        self.dpi = dpi
        self.fig = Figure(tuple(fig_size), dpi=self.dpi, facecolor=facecolor)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes = self.fig.add_subplot(111, facecolor=facecolor)
        
        if two_axes:
            self.axes2 = self.axes.twinx()
        
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        show_button = QtWidgets.QPushButton()
        show_button.clicked.connect(self._plot_settings_view)
        show_button.setIcon(QtGui.QIcon(":gear.png"))
        show_button.setToolTip(self.tr("Plot settings"))
        show_button.setStatusTip(self.tr("Plot settings"))
        
        buttonbox0 = QtWidgets.QDialogButtonBox()
        buttonbox0.addButton(show_button, QtWidgets.QDialogButtonBox.ActionRole)
        
        self.mpl_toolbar.addWidget(show_button)
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        self.status_text = QtWidgets.QLabel("")
        self.statusBar().addWidget(self.status_text, 1)
    
    def _create_menu(self) -> None:
        self.file_menu = self.menuBar().addMenu(self.tr("File"))
        tip = self.tr("Quit")
        quit_action = QtWidgets.QAction(tip, self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')
        self.file_menu.addAction(quit_action)
    
    def _plot_settings_view(self) -> None:
        from .dialogs import PlotSettingsDialog
        settings_dialog = PlotSettingsDialog(self)
        settings_dialog.setModal(True)
        settings_dialog.show()
    
    @property
    def data(self) -> Dict[int, pd.DataFrame]:
        return self._data
    
    @data.setter
    def data(self, value: Dict[int, pd.DataFrame]) -> None:
        self._data = value
    
    @property
    def plot_selection(self) -> List[int]:
        return self._plot_selection
    
    @plot_selection.setter
    def plot_selection(self, value: List[int]) -> None:
        self._plot_selection = value
    
    @property
    def single_dataset(self) -> bool:
        return self._single_dataset
    
    @single_dataset.setter
    def single_dataset(self, value: bool) -> None:
        self._single_dataset = value
    
    @property
    def title_enabled(self) -> bool:
        return self._title_enabled
    
    @title_enabled.setter
    def title_enabled(self, value: bool) -> None:
        self._title_enabled = value
    
    @property
    def title_selection(self) -> bool:
        return self._title_selection
    
    @title_selection.setter
    def title_selection(self, value: bool) -> None:
        self._title_selection = value
    
    @property
    def grid_enabled(self) -> bool:
        return self._grid_enabled
    
    @grid_enabled.setter
    def grid_enabled(self, value: bool) -> None:
        self._grid_enabled = value
    
    @property
    def grid_selection(self) -> bool:
        return self._grid_selection
    
    @grid_selection.setter
    def grid_selection(self, value: bool) -> None:
        self._grid_selection = value
    
    @property
    def legend_enabled(self) -> bool:
        return self._legend_enabled
    
    @legend_enabled.setter
    def legend_enabled(self, value: bool) -> None:
        self._legend_enabled = value
    
    @property
    def legend_selection(self) -> bool:
        return self._legend_selection
    
    @legend_selection.setter
    def legend_selection(self, value: bool) -> None:
        self._legend_selection = value
    
    @property
    def dotsize_enabled(self) -> bool:
        return self._dotsize_enabled
    
    @dotsize_enabled.setter
    def dotsize_enabled(self, value: bool) -> None:
        self._dotsize_enabled = value
    
    @property
    def dotsize_selection(self) -> int:
        return self._dotsize_selection
    
    @dotsize_selection.setter
    def dotsize_selection(self, value: int) -> None:
        self._dotsize_selection = value
    
    @property
    def linewidth_enabled(self) -> bool:
        return self._linewidth_enabled
    
    @linewidth_enabled.setter
    def linewidth_enabled(self, value: bool) -> None:
        self._linewidth_enabled = value
    
    @property
    def linewidth_selection(self) -> int:
        return self._linewidth_selection
    
    @linewidth_selection.setter
    def linewidth_selection(self, value: int) -> None:
        self._linewidth_selection = value
    
    @property
    def scatter_enabled(self) -> bool:
        return self._scatter_enabled
    
    @scatter_enabled.setter
    def scatter_enabled(self, value: bool) -> None:
        self._scatter_enabled = value
    
    @property
    def scatter_selection(self) -> float:
        return self._scatter_selection
    
    @scatter_selection.setter
    def scatter_selection(self, value: float) -> None:
        self._scatter_selection = value
    
    @property
    def ad(self) -> Dict[int, pd.DataFrame]:
        return self._data
    
    def get_color(self, index: int) -> str:
        return self._colors[index % len(self._colors)]
    
    def get_axis_label(self, param: str) -> str:
        return self._config.get_axis_label(param)
    
    def set_xlabel(self, label: str) -> None:
        self.axes.set_xlabel(label, fontsize=self._font_size, weight=self._font_weight)
    
    def set_ylabel(self, label: str) -> None:
        self.axes.set_ylabel(label, fontsize=self._font_size, weight=self._font_weight)
    
    def configure_ticks(self) -> None:
        self.axes.tick_params(pad=self._tick_pad)
    
    def draw_legend(self, loc: str = 'lower left', **kwargs) -> None:
        if self._legend_selection:
            self.axes.legend(loc=loc, scatterpoints=1, markerscale=3, frameon=False, **kwargs)
    
    @abstractmethod
    def on_draw(self) -> None:
        pass
