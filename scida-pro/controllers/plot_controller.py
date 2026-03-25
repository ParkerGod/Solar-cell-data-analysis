# -*- coding: utf-8 -*-
"""图表控制器 - 管理图表创建和显示"""

from __future__ import annotations

from typing import Optional, Dict, List, Type, Any
from PyQt5 import QtWidgets

from ..views import (
    BasePlotWidget, CorrVocIscWidget, CorrEtaFFWidget, CorrRshFFWidget,
    DistLtoHWidget, DensEtaWidget, DistWTWidget, DistRMWidget, IVBoxPlotWidget
)
from ..models.plot_model import PlotType, PlotConfig, PlotSelection
from ..utils import ConfigManager, get_logger


class PlotController:
    """图表控制器类"""
    
    # 图表类型到组件类的映射
    PLOT_WIDGET_MAP: Dict[PlotType, Type[BasePlotWidget]] = {
        PlotType.VOC_ISC: CorrVocIscWidget,
        PlotType.ETA_FF: CorrEtaFFWidget,
        PlotType.RSH_FF: CorrRshFFWidget,
        PlotType.LOW_TO_HIGH: DistLtoHWidget,
        PlotType.DENSITY: DensEtaWidget,
        PlotType.WALKTHROUGH: DistWTWidget,
        PlotType.ROLLING_MEAN: DistRMWidget,
        PlotType.BOXPLOT: IVBoxPlotWidget,
    }
    
    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None
    ) -> None:
        """
        初始化图表控制器
        
        Args:
            config_manager: 配置管理器
        """
        self._logger = get_logger(__name__)
        self._config = config_manager or ConfigManager()
        
        # 存储打开的图表窗口
        self._open_plots: List[BasePlotWidget] = []
    
    def create_plot(
        self,
        plot_type: PlotType,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, Any]] = None,
        param: Optional[str] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None
    ) -> Optional[BasePlotWidget]:
        """
        创建图表
        
        Args:
            plot_type: 图表类型
            parent: 父窗口
            data: 数据字典
            param: 参数 (用于需要参数的图表类型)
            plot_config: 图表配置
            plot_selection: 图表选择
            
        Returns:
            创建的图表组件，失败返回None
        """
        widget_class = self.PLOT_WIDGET_MAP.get(plot_type)
        
        if widget_class is None:
            self._logger.error(f"未知的图表类型: {plot_type}")
            return None
        
        try:
            # 创建图表配置
            config = plot_config or self._create_default_config(plot_type)
            selection = plot_selection or PlotSelection(
                selected_indices=list(range(len(data))) if data else []
            )
            
            # 创建图表组件
            if param and plot_type in [PlotType.WALKTHROUGH, PlotType.ROLLING_MEAN, PlotType.BOXPLOT]:
                widget = widget_class(
                    parent=parent,
                    param=param,
                    plot_config=config,
                    plot_selection=selection,
                    data=data
                )
            else:
                widget = widget_class(
                    parent=parent,
                    plot_config=config,
                    plot_selection=selection,
                    data=data
                )
            
            # 添加到打开列表
            self._open_plots.append(widget)
            
            # 连接关闭信号
            widget.destroyed.connect(lambda: self._on_plot_closed(widget))
            
            return widget
            
        except Exception as e:
            self._logger.error(f"创建图表失败: {e}")
            return None
    
    def _create_default_config(self, plot_type: PlotType) -> PlotConfig:
        """创建默认图表配置"""
        defaults = self._config.get_plot_defaults()
        colors = self._config.get_colors()
        
        config = PlotConfig(
            window_width=defaults.get('window_width', 1020),
            window_height=defaults.get('window_height', 752),
            colors=colors
        )
        
        # 根据图表类型设置特定配置
        if plot_type in [PlotType.VOC_ISC, PlotType.ETA_FF, PlotType.RSH_FF]:
            config.dotsize_selection = 20
        elif plot_type == PlotType.LOW_TO_HIGH:
            config.dotsize_selection = 200
        elif plot_type == PlotType.DENSITY:
            config.dotsize_enabled = False
            config.linewidth_enabled = True
            config.linewidth_selection = 3
        elif plot_type == PlotType.BOXPLOT:
            config.grid_enabled = False
            config.legend_enabled = False
            config.dotsize_enabled = False
            config.linewidth_enabled = False
        
        return config
    
    def show_plot(self, widget: BasePlotWidget) -> None:
        """显示图表"""
        if widget:
            widget.show()
            widget.raise_()
            widget.activateWindow()
    
    def close_all_plots(self) -> None:
        """关闭所有图表"""
        for plot in self._open_plots[:]:
            plot.close()
        self._open_plots.clear()
    
    def _on_plot_closed(self, widget: BasePlotWidget) -> None:
        """图表关闭回调"""
        if widget in self._open_plots:
            self._open_plots.remove(widget)
    
    def get_open_plots(self) -> List[BasePlotWidget]:
        """获取所有打开的图表"""
        return self._open_plots.copy()
    
    def get_available_plot_types(self) -> List[PlotType]:
        """获取可用的图表类型列表"""
        return list(self.PLOT_WIDGET_MAP.keys())
    
    def get_plot_type_from_string(self, plot_type_str: str) -> Optional[PlotType]:
        """从字符串获取图表类型"""
        for pt in PlotType:
            if pt.value == plot_type_str:
                return pt
        return None
