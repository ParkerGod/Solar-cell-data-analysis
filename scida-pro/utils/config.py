# -*- coding: utf-8 -*-
import yaml
import os
from typing import Any, Dict, List, Optional
from pathlib import Path


class Config:
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls, config_path: Optional[str] = None) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        
        config_path = os.path.abspath(config_path)
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'app': {
                'name': 'SCiDA Pro',
                'version': '1.0.0',
                'default_style': 'Fusion',
                'window_width': 1024,
                'window_height': 576,
                'font_size': 12
            },
            'colors': {
                'palette': ['#4F81BD', '#C0504D', '#9BBB59', '#F79646', '#8064A2', '#4BACC6', 'black', 'gray'],
                'window_background': [200, 201, 209],
                'base_background': [255, 255, 255],
                'highlight': [255, 79, 0]
            },
            'data_labels': {
                'formats': {
                    'format_a': {
                        'name': 'Data label set A',
                        'labels': ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
                    }
                },
                'default_format': 0,
                'internal_labels': ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
            },
            'filters': {
                'default': [
                    ['IRev1', '>', 3],
                    ['FF', '<', 70],
                    ['Eta', '<', 16],
                    ['FF', '<', 75],
                    ['Rsh', '<', 20],
                    ['Eta', '<', 18]
                ],
                'max_rows': 12,
                'valid_operators': ['<', '>'],
                'valid_parameters': ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
            },
            'plots': {
                'default_dot_size': 20,
                'default_line_width': 3,
                'default_scatter_amount': 0.5,
                'font_size': 24,
                'font_weight': 'black',
                'tick_pad': 8,
                'figure_size': [10.0, 10.0],
                'dpi': 100,
                'facecolor': 'White'
            },
            'axis_labels': {
                'Uoc': r'$\mathrm{\mathsf{V_{OC}\ [V]}}$',
                'Isc': r'$\mathrm{\mathsf{I_{SC}\ [A]}}$',
                'Voc_Isc': r'$\mathrm{\mathsf{V_{OC}\ *\ I_{SC}\ [V*A]}}$',
                'FF': r'$\mathrm{\mathsf{FF\ [\%]}}$',
                'Eta': r'$\mathrm{\mathsf{Eta\ [\%]}}$',
                'RserLfDfIEC': r'$\mathrm{\mathsf{R_{SERIES}\ [mOhm \cdot cm^{2}]}}$',
                'Rsh': r'$\mathrm{\mathsf{R_{SHUNT}\ [kOhm]}}$',
                'IRev1': r'$\mathrm{\mathsf{I_{REV}\ [A]}}$'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'scida_pro.log'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def app_name(self) -> str:
        return self.get('app.name', 'SCiDA Pro')
    
    @property
    def colors(self) -> List[str]:
        return self.get('colors.palette', ['#4F81BD', '#C0504D', '#9BBB59', '#F79646', '#8064A2', '#4BACC6'])
    
    @property
    def default_filters(self) -> List[List]:
        return self.get('filters.default', [])
    
    @property
    def label_formats(self) -> Dict[int, List[str]]:
        formats = self.get('data_labels.formats', {})
        result = {}
        for i, (key, value) in enumerate(formats.items()):
            result[i] = value.get('labels', [])
        return result
    
    @property
    def internal_labels(self) -> List[str]:
        return self.get('data_labels.internal_labels', ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1'])
    
    @property
    def plot_settings(self) -> Dict[str, Any]:
        return self.get('plots', {})
    
    @property
    def axis_labels(self) -> Dict[str, str]:
        return self.get('axis_labels', {})
    
    def get_axis_label(self, param: str) -> str:
        return self.axis_labels.get(param, param)


_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
