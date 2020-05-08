# -*- coding: utf-8 -*-
"""配置管理器单元测试"""

import pytest
import os
import tempfile
from unittest.mock import patch, mock_open

from utils.config_manager import ConfigManager


class TestConfigManager:
    """ConfigManager测试类"""
    
    def test_singleton(self) -> None:
        """测试单例模式"""
        # 重置单例
        ConfigManager._instance = None
        
        cm1 = ConfigManager()
        cm2 = ConfigManager()
        
        assert cm1 is cm2
    
    def test_default_config(self) -> None:
        """测试默认配置"""
        ConfigManager._instance = None
        
        cm = ConfigManager(config_path="nonexistent.yaml")
        
        assert 'colors' in cm._config
        assert 'plot_parameters' in cm._config
    
    def test_get_colors(self) -> None:
        """测试获取颜色"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        colors = cm.get_colors()
        
        assert isinstance(colors, list)
        assert len(colors) > 0
    
    def test_get_plot_parameters(self) -> None:
        """测试获取绘图参数"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        params = cm.get_plot_parameters()
        
        assert isinstance(params, list)
        assert 'Uoc' in params
        assert 'Eta' in params
    
    def test_get_default_filters(self) -> None:
        """测试获取默认过滤器"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        filters = cm.get_default_filters()
        
        assert isinstance(filters, list)
        assert len(filters) > 0
    
    def test_get_plot_defaults(self) -> None:
        """测试获取绘图默认设置"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        defaults = cm.get_plot_defaults()
        
        assert isinstance(defaults, dict)
        assert 'window_width' in defaults
        assert 'window_height' in defaults
    
    def test_get_with_default(self) -> None:
        """测试带默认值的获取"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        value = cm.get('nonexistent.key', 'default_value')
        
        assert value == 'default_value'
    
    def test_get_nested_key(self) -> None:
        """测试嵌套键获取"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        colors = cm.get('colors.plot_colors')
        
        assert isinstance(colors, list)
    
    def test_reload(self) -> None:
        """测试重新加载"""
        ConfigManager._instance = None
        
        cm = ConfigManager()
        original_config = cm._config.copy()
        
        cm.reload()
        
        assert cm._config is not None
