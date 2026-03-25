# -*- coding: utf-8 -*-
"""
IVMainPlot 重构版本 - 向后兼容包装器

此模块提供与原始IVMainPlot.py相同的API，但内部使用新的MVC架构实现。
保持向后兼容性，确保现有代码可以继续工作。
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from PyQt5 import QtGui, QtWidgets

# 从新的MVC架构导入
from views import (
    CorrVocIscWidget as _CorrVocIscWidget,
    CorrEtaFFWidget as _CorrEtaFFWidget,
    CorrRshFFWidget as _CorrRshFFWidget,
    DistLtoHWidget as _DistLtoHWidget,
    DensEtaWidget as _DensEtaWidget,
    DistWTWidget as _DistWTWidget,
    DistRMWidget as _DistRMWidget,
    IVBoxPlotWidget as _IVBoxPlotWidget,
    PlotSettingsDialog as _PlotSettingsDialog
)
from models.plot_model import PlotConfig, PlotSelection
from utils import ConfigManager

# 保持与原始代码相同的颜色配置
cl = ['#4F81BD', '#C0504D', '#9BBB59', '#F79646', '#8064A2', '#4BACC6', '0', '0.5']

# 保持与原始代码相同的轴标签
irev_axis_label = r'$\mathrm{\mathsf{I_{REV}\ [A]}}$'
rser_axis_label = r'$\mathrm{\mathsf{R_{SERIES}\ [mOhm \cdot cm^{2}]}}$'
rshunt_axis_label = r'$\mathrm{\mathsf{R_{SHUNT}\ [kOhm]}}$'
eta_axis_label = r'$\mathrm{\mathsf{Eta\ [\%]}}$'
voc_axis_label = r'$\mathrm{\mathsf{V_{OC}\ [V]}}$'
isc_axis_label = r'$\mathrm{\mathsf{I_{SC}\ [A]}}$'
ff_axis_label = r'$\mathrm{\mathsf{FF\ [\%]}}$'
vocisc_axis_label = r'$\mathrm{\mathsf{V_{OC}\ *\ I_{SC}\ [V*A]}}$'
plot_selection_list = ['Uoc', 'Isc', 'Voc*Isc', 'FF', 'Eta', 'RserLfDfIEC', 'Rsh', 'IRev1']
plot_label_list = [voc_axis_label, isc_axis_label, vocisc_axis_label, ff_axis_label, 
                   eta_axis_label, rser_axis_label, rshunt_axis_label, irev_axis_label]


class IVMainPlot:
    """
    IVMainPlot基类 - 向后兼容包装器
    
    保持与原始代码相同的API，内部委托给新的BasePlotWidget。
    """
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """初始化 (向后兼容)"""
        self.parent = parent
        self.ad: Dict[int, pd.DataFrame] = {}
        self.plot_selection: List[int] = []
        
        # 图表设置 (与原始代码兼容)
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 20
        self.linewidth_enabled = False
        self.scatter_enabled = False
        self.scatter_selection = 0.0
        self.linewidth_selection = 3
        
        # 内部widget引用
        self._widget: Optional[Any] = None
    
    def on_draw(self) -> None:
        """绘制图表 (子类实现)"""
        if self._widget:
            self._widget.on_draw()
    
    def create_main_frame(self, two_axes: bool = False) -> None:
        """创建主框架 (向后兼容，实际在widget中实现)"""
        pass
    
    def create_menu(self) -> None:
        """创建菜单 (向后兼容，实际在widget中实现)"""
        pass
    
    def plot_settings_view(self) -> None:
        """打开图表设置对话框"""
        if self._widget:
            self._widget.plot_settings_view()


class CorrVocIsc(_CorrVocIscWidget):
    """Voc-Isc相关性图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        # 从父窗口获取数据
        data = getattr(parent, 'ad', {}) if parent else {}
        
        # 创建选择配置
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        # 调用父类初始化
        super().__init__(
            parent=parent,
            plot_config=PlotConfig(
                dotsize_selection=20,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        # 保持向后兼容的属性
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 20
        self.linewidth_enabled = False
        self.scatter_enabled = False


class CorrEtaFF(_CorrEtaFFWidget):
    """Eta-FF相关性图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        super().__init__(
            parent=parent,
            plot_config=PlotConfig(
                dotsize_selection=20,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 20
        self.linewidth_enabled = False
        self.scatter_enabled = False


class CorrRshFF(_CorrRshFFWidget):
    """Rsh-FF相关性图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        super().__init__(
            parent=parent,
            plot_config=PlotConfig(
                dotsize_selection=20,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 20
        self.linewidth_enabled = False
        self.scatter_enabled = False


class DistLtoH(_DistLtoHWidget):
    """低至高分布图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        super().__init__(
            parent=parent,
            plot_config=PlotConfig(
                dotsize_selection=200,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 200
        self.linewidth_enabled = False
        self.scatter_enabled = False


class DensEta(_DensEtaWidget):
    """Eta密度图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        super().__init__(
            parent=parent,
            plot_config=PlotConfig(
                dotsize_enabled=False,
                linewidth_enabled=True,
                linewidth_selection=3,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = False
        self.linewidth_enabled = True
        self.linewidth_selection = 3
        self.scatter_enabled = False


class DistWT(_DistWTWidget):
    """遍历图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget], param_one_combo: str) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        param = str(param_one_combo) if str(param_one_combo) in plot_selection_list else 'Eta'
        
        super().__init__(
            parent=parent,
            param=param,
            plot_config=PlotConfig(
                dotsize_selection=20,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.param_one_combo = param
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = True
        self.dotsize_selection = 20
        self.linewidth_enabled = False
        self.scatter_enabled = False


class DistRM(_DistRMWidget):
    """滚动均值图表 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget], param_one_combo: str) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        param = str(param_one_combo) if str(param_one_combo) in plot_selection_list else 'Eta'
        
        super().__init__(
            parent=parent,
            param=param,
            plot_config=PlotConfig(
                dotsize_enabled=False,
                linewidth_enabled=True,
                linewidth_selection=3,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.param_one_combo = param
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = True
        self.grid_selection = True
        self.legend_enabled = True
        self.legend_selection = True
        self.dotsize_enabled = False
        self.linewidth_enabled = True
        self.linewidth_selection = 3
        self.scatter_enabled = False


class IVBoxPlot(_IVBoxPlotWidget):
    """箱线图 - 向后兼容包装器"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget], param_one_combo: str) -> None:
        data = getattr(parent, 'ad', {}) if parent else {}
        plot_selection = PlotSelection(
            selected_indices=list(range(len(data))),
            single_dataset=False
        )
        
        param = str(param_one_combo) if str(param_one_combo) in plot_selection_list else 'Eta'
        
        super().__init__(
            parent=parent,
            param=param,
            plot_config=PlotConfig(
                grid_enabled=False,
                legend_enabled=False,
                dotsize_enabled=False,
                linewidth_enabled=False,
                colors=cl
            ),
            plot_selection=plot_selection,
            data=data
        )
        
        self.ad = data
        self.plot_selection = list(range(len(data)))
        self.param_one_combo = param
        self.single_dataset = False
        self.title_enabled = False
        self.grid_enabled = False
        self.legend_enabled = False
        self.dotsize_enabled = False
        self.linewidth_enabled = False
        self.scatter_enabled = False


# 保持PlotSettingsDialog的兼容性
PlotSettingsDialog = _PlotSettingsDialog


# 为了完全兼容，添加这些类的别名
IVMainPlotWidget = IVMainPlot
