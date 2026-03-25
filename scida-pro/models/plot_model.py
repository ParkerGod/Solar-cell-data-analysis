# -*- coding: utf-8 -*-
"""图表模型 - 图表配置和选择"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


class PlotType(Enum):
    """图表类型枚举"""
    BOXPLOT = "Boxplot"
    VIOLINPLOT = "Violinplot"
    CATEGORY_SCATTER = "Category scatter"
    WALKTHROUGH = "Walk-through"
    ROLLING_MEAN = "Rolling mean"
    LOW_TO_HIGH = "Low to high"
    HISTOGRAM = "Histogram"
    DENSITY = "Density"
    HISTOGRAM_DENSITY = "Histogram + density"
    VOC_ISC = "Voc-Isc"
    ETA_FF = "Eta-FF"
    RSH_FF = "Rsh-FF"


@dataclass
class PlotSelection:
    """图表选择配置"""
    selected_indices: List[int] = field(default_factory=list)
    single_dataset: bool = False
    
    def __post_init__(self) -> None:
        """初始化后处理"""
        if not self.selected_indices:
            self.selected_indices = []


@dataclass
class PlotConfig:
    """图表配置类"""
    # 显示选项
    title_enabled: bool = False
    title_selection: bool = False
    grid_enabled: bool = True
    grid_selection: bool = True
    legend_enabled: bool = True
    legend_selection: bool = True
    
    # 散点图选项
    dotsize_enabled: bool = True
    dotsize_selection: int = 20
    scatter_enabled: bool = False
    scatter_selection: float = 0.0
    
    # 线图选项
    linewidth_enabled: bool = False
    linewidth_selection: int = 3
    
    # 窗口设置
    window_width: int = 1020
    window_height: int = 752
    
    # 颜色设置
    colors: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """初始化后处理 - 设置默认颜色"""
        if not self.colors:
            self.colors = ['#4F81BD', '#C0504D', '#9BBB59', '#F79646', '#8064A2', '#4BACC6', '0', '0.5']
    
    def get_color(self, index: int) -> str:
        """获取指定索引的颜色"""
        if not self.colors:
            return '#4F81BD'
        return self.colors[index % len(self.colors)]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title_enabled': self.title_enabled,
            'title_selection': self.title_selection,
            'grid_enabled': self.grid_enabled,
            'grid_selection': self.grid_selection,
            'legend_enabled': self.legend_enabled,
            'legend_selection': self.legend_selection,
            'dotsize_enabled': self.dotsize_enabled,
            'dotsize_selection': self.dotsize_selection,
            'scatter_enabled': self.scatter_enabled,
            'scatter_selection': self.scatter_selection,
            'linewidth_enabled': self.linewidth_enabled,
            'linewidth_selection': self.linewidth_selection,
            'window_width': self.window_width,
            'window_height': self.window_height,
            'colors': self.colors
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PlotConfig':
        """从字典创建配置"""
        return cls(**config_dict)


@dataclass
class AxisConfig:
    """坐标轴配置"""
    x_label: str = ""
    y_label: str = ""
    x_scale: str = "linear"  # linear, log, semilogx, semilogy
    y_scale: str = "linear"
    xlim: Optional[Tuple[float, float]] = None
    ylim: Optional[Tuple[float, float]] = None


@dataclass
class LegendConfig:
    """图例配置"""
    loc: str = 'lower left'
    scatterpoints: int = 1
    markerscale: int = 3
    frameon: bool = False
