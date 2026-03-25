# -*- coding: utf-8 -*-
"""图表模型单元测试"""

import pytest
from models.plot_model import PlotConfig, PlotSelection, AxisConfig, LegendConfig, PlotType


class TestPlotConfig:
    """PlotConfig测试类"""
    
    def test_default_init(self) -> None:
        """测试默认初始化"""
        config = PlotConfig()
        
        assert config.title_enabled is False
        assert config.grid_enabled is True
        assert config.legend_enabled is True
        assert config.dotsize_selection == 20
        assert config.linewidth_selection == 3
        assert len(config.colors) > 0
    
    def test_custom_init(self) -> None:
        """测试自定义初始化"""
        config = PlotConfig(
            title_enabled=True,
            dotsize_selection=50,
            colors=['#FF0000', '#00FF00']
        )
        
        assert config.title_enabled is True
        assert config.dotsize_selection == 50
        assert config.colors == ['#FF0000', '#00FF00']
    
    def test_get_color(self) -> None:
        """测试获取颜色"""
        config = PlotConfig(colors=['#FF0000', '#00FF00', '#0000FF'])
        
        assert config.get_color(0) == '#FF0000'
        assert config.get_color(1) == '#00FF00'
        assert config.get_color(2) == '#0000FF'
        assert config.get_color(3) == '#FF0000'  # 循环
    
    def test_get_color_empty(self) -> None:
        """测试空颜色列表"""
        config = PlotConfig(colors=[])
        assert config.get_color(0) == '#4F81BD'  # 默认颜色
    
    def test_to_dict(self) -> None:
        """测试转换为字典"""
        config = PlotConfig(title_enabled=True)
        config_dict = config.to_dict()
        
        assert config_dict['title_enabled'] is True
        assert config_dict['grid_enabled'] is True
        assert 'colors' in config_dict
    
    def test_from_dict(self) -> None:
        """测试从字典创建"""
        config_dict = {
            'title_enabled': True,
            'dotsize_selection': 50,
            'colors': ['#FF0000']
        }
        config = PlotConfig.from_dict(config_dict)
        
        assert config.title_enabled is True
        assert config.dotsize_selection == 50


class TestPlotSelection:
    """PlotSelection测试类"""
    
    def test_default_init(self) -> None:
        """测试默认初始化"""
        selection = PlotSelection()
        
        assert selection.selected_indices == []
        assert selection.single_dataset is False
    
    def test_custom_init(self) -> None:
        """测试自定义初始化"""
        selection = PlotSelection(
            selected_indices=[0, 1, 2],
            single_dataset=True
        )
        
        assert selection.selected_indices == [0, 1, 2]
        assert selection.single_dataset is True


class TestAxisConfig:
    """AxisConfig测试类"""
    
    def test_default_init(self) -> None:
        """测试默认初始化"""
        config = AxisConfig()
        
        assert config.x_label == ""
        assert config.y_label == ""
        assert config.x_scale == "linear"
        assert config.y_scale == "linear"
        assert config.xlim is None
        assert config.ylim is None
    
    def test_custom_init(self) -> None:
        """测试自定义初始化"""
        config = AxisConfig(
            x_label='X Axis',
            y_label='Y Axis',
            x_scale='log',
            xlim=(0, 100)
        )
        
        assert config.x_label == 'X Axis'
        assert config.y_label == 'Y Axis'
        assert config.x_scale == 'log'
        assert config.xlim == (0, 100)


class TestLegendConfig:
    """LegendConfig测试类"""
    
    def test_default_init(self) -> None:
        """测试默认初始化"""
        config = LegendConfig()
        
        assert config.loc == 'lower left'
        assert config.scatterpoints == 1
        assert config.markerscale == 3
        assert config.frameon is False
    
    def test_custom_init(self) -> None:
        """测试自定义初始化"""
        config = LegendConfig(
            loc='upper right',
            frameon=True
        )
        
        assert config.loc == 'upper right'
        assert config.frameon is True


class TestPlotType:
    """PlotType测试类"""
    
    def test_plot_type_values(self) -> None:
        """测试图表类型值"""
        assert PlotType.BOXPLOT.value == "Boxplot"
        assert PlotType.VOC_ISC.value == "Voc-Isc"
        assert PlotType.ETA_FF.value == "Eta-FF"
        assert PlotType.RSH_FF.value == "Rsh-FF"
