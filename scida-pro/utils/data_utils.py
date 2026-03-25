# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np


def convert_param_value(
    param_name: str,
    value: Union[pd.Series, float],
    param_one_combo: Optional[str] = None
) -> Union[pd.Series, float]:
    if param_one_combo == 'Voc*Isc':
        if isinstance(value, pd.DataFrame):
            return value.iloc[:, 0]
        return value
    
    if param_name == 'RserLfDfIEC' or param_one_combo == 'RserLfDfIEC':
        if isinstance(value, (pd.Series, pd.DataFrame)):
            return 1000 * value
        return 1000 * value
    
    if param_name == 'Rsh' or param_one_combo == 'Rsh':
        if isinstance(value, (pd.Series, pd.DataFrame)):
            return 0.001 * value
        return 0.001 * value
    
    return value


def get_axis_label(param: str, axis_labels: Dict[str, str]) -> str:
    label_mapping = {
        'Uoc': 'Uoc',
        'Isc': 'Isc',
        'Voc*Isc': 'Voc_Isc',
        'FF': 'FF',
        'Eta': 'Eta',
        'RserLfDfIEC': 'RserLfDfIEC',
        'Rsh': 'Rsh',
        'IRev1': 'IRev1'
    }
    key = label_mapping.get(param, param)
    return axis_labels.get(key, param)


def calculate_statistics(data: pd.DataFrame, columns: List[str]) -> Dict[str, Dict[str, float]]:
    result = {}
    for col in columns:
        if col in data.columns:
            result[col] = {
                'max': float(data[col].max()),
                'min': float(data[col].min()),
                'mean': float(data[col].mean()),
                'median': float(data[col].median()),
                'std': float(data[col].std()) if len(data) > 1 else np.nan
            }
    return result


def apply_conversion_factor(data: pd.DataFrame, label_format: int) -> pd.DataFrame:
    if label_format == 1:
        if 'Eta' in data.columns:
            data['Eta'] = data['Eta'] * 100
        if 'FF' in data.columns:
            data['FF'] = data['FF'] * 100
    elif label_format == 3:
        if 'Eta' in data.columns:
            data['Eta'] = data['Eta'] * 100
    return data
