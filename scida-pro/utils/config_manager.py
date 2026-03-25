# -*- coding: utf-8 -*-
"""配置管理器 - 统一管理应用程序配置"""

import os
import yaml
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器类 - 单例模式"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls, config_path: Optional[str] = None) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        """加载配置文件"""
        if config_path is None:
            # 默认配置文件路径
            current_dir = Path(__file__).parent
            config_path = current_dir / 'config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            self._config = self._get_default_config()
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件解析错误: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'colors': {
                'plot_colors': ['#4F81BD', '#C0504D', '#9BBB59', '#F79646', '#8064A2', '#4BACC6', '0', '0.5']
            },
            'axis_labels': {
                'voc': r'$\mathrm{\mathsf{V_{OC}\ [V]}}$',
                'isc': r'$\mathrm{\mathsf{I_{SC}\ [A]}}$',
                'ff': r'$\mathrm{\mathsf{FF\ [\%]}}$',
                'eta': r'$\mathrm{\mathsf{Eta\ [\%]}}$',
            },
            'plot_parameters': ['Uoc', 'Isc', 'FF', 'Eta', 'RserLfDfIEC', 'Rsh', 'IRev1'],
            'default_filters': [
                ['IRev1', '>', 3],
                ['FF', '<', 70],
                ['Eta', '<', 16],
            ],
            'plot_defaults': {
                'window_width': 1020,
                'window_height': 752,
                'dpi': 100,
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_colors(self) -> List[str]:
        """获取绘图颜色列表"""
        return self.get('colors.plot_colors', ['#4F81BD', '#C0504D', '#9BBB59'])
    
    def get_axis_label(self, key: str) -> str:
        """获取轴标签"""
        return self.get(f'axis_labels.{key}', key)
    
    def get_plot_parameters(self) -> List[str]:
        """获取可绘制的参数列表"""
        return self.get('plot_parameters', [])
    
    def get_default_filters(self) -> List[List]:
        """获取默认过滤器"""
        return self.get('default_filters', [])
    
    def get_label_formats(self) -> Dict[str, List[str]]:
        """获取数据标签格式"""
        return self.get('label_formats', {})
    
    def get_summary_config(self) -> Dict[str, Any]:
        """获取汇总表格配置"""
        return self.get('summary', {})
    
    def get_plot_defaults(self) -> Dict[str, Any]:
        """获取图表默认设置"""
        return self.get('plot_defaults', {})
    
    def reload(self, config_path: Optional[str] = None) -> None:
        """重新加载配置"""
        self._load_config(config_path)
