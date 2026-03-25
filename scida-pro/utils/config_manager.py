# -*- coding: utf-8 -*-
"""
Configuration Manager for SCiDA Pro
Handles loading and accessing configuration from config.yaml
"""

import os
from typing import Any, Dict, List, Optional
import yaml


class ConfigManager:
    """Singleton configuration manager class"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _config_path: str = ""
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._config:
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from config.yaml file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        self._config_path = config_path
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}")
            self._config = {}
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            self._config = {}
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports dot notation)
        Example: get('colors.primary')
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_colors(self) -> List[str]:
        """Get color list"""
        return self.get('colors.list', [
            '#4F81BD', '#C0504D', '#9BBB59', '#F79646',
            '#8064A2', '#4BACC6', '0', '0.5'
        ])
    
    def get_plot_labels(self) -> Dict[str, str]:
        """Get plot labels dictionary"""
        return self.get('plot_labels', {
            'voc_axis_label': r'$\mathrm{\mathsf{V_{OC}}}$ [V]',
            'isc_axis_label': r'$\mathrm{\mathsf{I_{SC}}}$ [A]',
        })
    
    def get_default_filters(self) -> List[List[Any]]:
        """Get default filter settings"""
        return self.get('default_filters', [
            ["IRev1", ">", 3], ["FF", "<", 70], ["Eta", "<", 16],
            ["FF", "<", 75], ["Rsh", "<", 20], ["Eta", "<", 18]
        ])
    
    def get_label_formats(self) -> Dict[int, List[str]]:
        """Get label formats dictionary"""
        return self.get('label_formats', {
            0: ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1'],
        })
    
    def get_data_columns(self) -> List[str]:
        """Get data column names"""
        return self.get('data_columns', [
            'Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1'
        ])
    
    def get_plot_selection_list(self) -> List[str]:
        """Get plot selection list"""
        return self.get('plot_selection_list', [
            'Uoc', 'Isc', 'Voc*Isc', 'FF', 'Eta', 'RserLfDfIEC', 'Rsh', 'IRev1'
        ])
    
    def get_plot_types(self) -> List[str]:
        """Get plot types"""
        return self.get('plot_types', [
            'Boxplot', 'Violinplot', 'Category scatter', 'Walk-through',
            'Rolling mean', 'Low to high', 'Histogram', 'Density',
            'Histogram + density', 'Voc-Isc', 'Eta-FF', 'Rsh-FF'
        ])
    
    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        return self.get(f'app.{key}', default)
    
    def get_plot_default(self, key: str, default: Any = None) -> Any:
        """Get plot default setting"""
        return self.get(f'plot_defaults.{key}', default)
