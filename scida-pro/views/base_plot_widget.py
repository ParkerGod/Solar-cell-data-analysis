# -*- coding: utf-8 -*-
"""基础图表组件 - 使用模板方法模式"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple, Callable
from abc import ABC, abstractmethod

from PyQt5 import QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams

from ..models.plot_model import PlotConfig, PlotSelection, AxisConfig, LegendConfig
from ..utils import ConfigManager

# 设置matplotlib默认参数
rcParams.update({'figure.autolayout': True})


class BasePlotWidget(QtWidgets.QMainWindow, ABC):
    """
    基础图表组件类 - 模板方法模式
    
    所有图表类的基类，提供通用的初始化逻辑和绘图框架。
    子类只需实现特定的抽象方法即可。
    """
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        """
        初始化基础图表组件
        
        Args:
            parent: 父窗口
            plot_config: 图表配置
            plot_selection: 图表选择
            data: 数据字典
        """
        super().__init__(parent)
        
        # 配置管理器
        self._config_manager = ConfigManager()
        
        # 图表配置
        self._plot_config = plot_config or self._create_default_config()
        self._plot_selection = plot_selection or PlotSelection()
        self._data = data or {}
        
        # 初始化UI
        self._setup_window()
        self._create_menu()
        self._create_main_frame()
        self._init_plot_settings()
        
        # 执行绘图
        self.on_draw()
    
    def _create_default_config(self) -> PlotConfig:
        """创建默认图表配置"""
        defaults = self._config_manager.get_plot_defaults()
        colors = self._config_manager.get_colors()
        return PlotConfig(
            window_width=defaults.get('window_width', 1020),
            window_height=defaults.get('window_height', 752),
            colors=colors
        )
    
    def _setup_window(self) -> None:
        """设置窗口属性"""
        self.setWindowTitle(self.tr(self._get_window_title()))
        self.resize(self._plot_config.window_width, self._plot_config.window_height)
        
        # 居中显示
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    
    def _create_main_frame(self, two_axes: bool = False) -> None:
        """创建主框架"""
        self.main_frame = QtWidgets.QWidget()
        
        # 创建matplotlib图形和画布
        dpi = self._config_manager.get('plot_defaults.dpi', 100)
        figsize = self._config_manager.get('plot_defaults.figure_size', [10.0, 10.0])
        self.fig = Figure(figsize, dpi=dpi, facecolor='White')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # 创建坐标轴
        self.axes = self.fig.add_subplot(111, facecolor='White')
        if two_axes:
            self.axes2 = self.axes.twinx()
        
        # 创建导航工具栏
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # 添加设置按钮
        self._add_settings_button()
        
        # 布局
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        # 状态栏
        self.status_text = QtWidgets.QLabel("")
        self.statusBar().addWidget(self.status_text, 1)
    
    def _add_settings_button(self) -> None:
        """添加设置按钮到工具栏"""
        show_button = QtWidgets.QPushButton()
        show_button.clicked.connect(self.plot_settings_view)
        show_button.setIcon(QtGui.QIcon(":gear.png"))
        show_button.setToolTip(self.tr("Plot settings"))
        show_button.setStatusTip(self.tr("Plot settings"))
        
        buttonbox0 = QtWidgets.QDialogButtonBox()
        buttonbox0.addButton(show_button, QtWidgets.QDialogButtonBox.ActionRole)
        
        self.mpl_toolbar.addWidget(show_button)
    
    def _create_menu(self) -> None:
        """创建菜单"""
        self.file_menu = self.menuBar().addMenu(self.tr("File"))
        
        tip = self.tr("Quit")
        quit_action = QtWidgets.QAction(tip, self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')
        
        self.file_menu.addAction(quit_action)
    
    def _init_plot_settings(self) -> None:
        """初始化图表设置 - 子类可覆盖"""
        # 初始化数据选择
        if not self._plot_selection.selected_indices and self._data:
            self._plot_selection.selected_indices = list(range(len(self._data)))
    
    def plot_settings_view(self) -> None:
        """打开图表设置对话框"""
        from .plot_settings_dialog import PlotSettingsDialog
        settings_dialog = PlotSettingsDialog(self)
        settings_dialog.setModal(True)
        settings_dialog.show()
    
    def on_draw(self) -> None:
        """
        绘制图表 - 模板方法
        
        定义绘图的基本流程，子类实现具体步骤。
        """
        # 清除之前的绘图
        self._clear_axes()
        
        # 设置坐标轴
        self._setup_axes()
        
        # 绘制数据
        self._plot_data()
        
        # 设置图例
        self._setup_legend()
        
        # 设置网格
        self._setup_grid()
        
        # 刷新画布
        self.canvas.draw()
    
    def _clear_axes(self) -> None:
        """清除坐标轴"""
        self.axes.clear()
    
    def _setup_axes(self) -> None:
        """设置坐标轴 - 子类实现"""
        axis_config = self._get_axis_config()
        
        # 设置标签
        if axis_config.x_label:
            self.axes.set_xlabel(axis_config.x_label, fontsize=24, weight='black')
        if axis_config.y_label:
            self.axes.set_ylabel(axis_config.y_label, fontsize=24, weight='black')
        
        # 设置刻度参数
        self.axes.tick_params(pad=8)
        
        # 设置坐标轴范围
        if axis_config.xlim:
            self.axes.set_xlim(axis_config.xlim)
        if axis_config.ylim:
            self.axes.set_ylim(axis_config.ylim)
        
        # 设置坐标轴刻度类型
        if axis_config.x_scale == 'log':
            self.axes.set_xscale('log')
        if axis_config.y_scale == 'log':
            self.axes.set_yscale('log')
    
    def _setup_legend(self) -> None:
        """设置图例"""
        if self._plot_config.legend_enabled and self._plot_config.legend_selection:
            legend_config = self._get_legend_config()
            self.axes.legend(
                loc=legend_config.loc,
                scatterpoints=legend_config.scatterpoints,
                markerscale=legend_config.markerscale,
                frameon=legend_config.frameon
            )
    
    def _setup_grid(self) -> None:
        """设置网格"""
        if self._plot_config.grid_enabled:
            self.axes.grid(self._plot_config.grid_selection)
    
    def get_plot_config(self) -> PlotConfig:
        """获取图表配置"""
        return self._plot_config
    
    def set_plot_config(self, config: PlotConfig) -> None:
        """设置图表配置"""
        self._plot_config = config
        self.on_draw()
    
    def get_plot_selection(self) -> PlotSelection:
        """获取图表选择"""
        return self._plot_selection
    
    def set_plot_selection(self, selection: PlotSelection) -> None:
        """设置图表选择"""
        self._plot_selection = selection
        self.on_draw()
    
    def get_data(self) -> Dict[int, pd.DataFrame]:
        """获取数据"""
        return self._data
    
    def set_data(self, data: Dict[int, pd.DataFrame]) -> None:
        """设置数据"""
        self._data = data
        self.on_draw()
    
    # ==================== 抽象方法 - 子类必须实现 ====================
    
    @abstractmethod
    def _get_window_title(self) -> str:
        """获取窗口标题 - 子类实现"""
        pass
    
    @abstractmethod
    def _get_axis_config(self) -> AxisConfig:
        """获取坐标轴配置 - 子类实现"""
        pass
    
    @abstractmethod
    def _plot_data(self) -> None:
        """绘制数据 - 子类实现"""
        pass
    
    def _get_legend_config(self) -> LegendConfig:
        """获取图例配置 - 子类可覆盖"""
        return LegendConfig(
            loc='lower left',
            scatterpoints=1,
            markerscale=3,
            frameon=False
        )
