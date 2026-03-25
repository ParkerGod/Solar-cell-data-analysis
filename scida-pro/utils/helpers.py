# -*- coding: utf-8 -*-
"""
Helper functions for SCiDA Pro
Common utility functions used across the application
"""

import os
import re
from typing import Any, List, Optional, Union
import numpy as np
import pandas as pd


def is_number(s: Any) -> bool:
    """Check if input can be converted to a float"""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def remove_whitespace(s: str) -> str:
    """Remove all whitespace and tab characters from string"""
    return s.replace(" ", "").replace("\t", "")


def is_valid_ascii_filename(filename: str) -> bool:
    """Check if filename contains only ASCII characters"""
    try:
        filename.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def sanitize_filename(filename: str, max_length: int = 40) -> str:
    """
    Sanitize filename to remove invalid characters and limit length
    Only keep alphanumeric characters, spaces, dots, and underscores
    """
    keepcharacters = (' ', '.', '_')
    valid_filename = "".join(
        c for c in filename if c.isalnum() or c in keepcharacters
    ).rstrip()
    return valid_filename[:max_length]


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def calculate_statistics(data: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Calculate statistics for given data columns
    Returns: best cell (max efficiency), median, average, std.dev.
    """
    if columns is None:
        columns = ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
    
    stats_index = ['Best cell', 'Median', 'Average', 'Std.dev.']
    stats = pd.DataFrame(index=stats_index, columns=columns)
    
    # Get best cell (row with maximum Eta)
    if 'Eta' in data.columns and len(data) > 0:
        best_idx = data['Eta'].idxmax()
        stats.loc['Best cell'] = data.loc[best_idx, columns].values
    
    # Calculate other statistics
    stats.loc['Median'] = data[columns].median().values
    stats.loc['Average'] = data[columns].mean().values
    
    # Standard deviation for selected columns (Voc, Isc, FF, Eta)
    std_dev = pd.Series([np.nan] * len(columns), index=columns)
    std_columns = ['Uoc', 'Isc', 'FF', 'Eta']
    for col in std_columns:
        if col in data.columns:
            std_dev[col] = data[col].std()
    stats.loc['Std.dev.'] = std_dev.values
    
    return stats


def calculate_correlation(data: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Calculate correlation matrix for given data
    Mask out correlation for Rser, Rsh, and IRev1
    """
    if columns is None:
        columns = ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
    
    if len(data) <= 1:
        return pd.DataFrame()
    
    corr_matrix = data[columns].corr().round(2)
    
    # Mask out Rser, Rsh, and IRev1 correlations (as in original code)
    if len(columns) >= 7:
        corr_matrix.iloc[:, 2:4] = np.nan
        corr_matrix.iloc[2:4, :] = np.nan
        corr_matrix.iloc[6, :] = np.nan
        corr_matrix.iloc[:, 6] = np.nan
    
    # Drop empty rows and columns
    corr_matrix = corr_matrix.dropna(how='all').T.dropna(how='all')
    
    return corr_matrix


def safe_division(numerator: Union[float, np.ndarray], 
                   denominator: Union[float, np.ndarray], 
                   default: float = 0.0) -> Union[float, np.ndarray]:
    """Safe division that handles division by zero"""
    if isinstance(denominator, np.ndarray):
        mask = denominator != 0
        result = np.full_like(numerator, default, dtype=np.float64)
        result[mask] = numerator[mask] / denominator[mask]
        return result
    else:
        if denominator == 0:
            return default
        return numerator / denominator


def apply_unit_conversion(data: pd.Series, 
                          conversion_type: str, 
                          inverse: bool = False) -> pd.Series:
    """
    Apply unit conversions to data series
    conversion_type: 
        - 'Rser': convert Ohm to mOhm (*1000)
        - 'Rsh': convert Ohm to kOhm (/1000)
        - 'Eta': convert decimal to percentage (*100)
        - 'FF': convert decimal to percentage (*100)
    """
    if conversion_type == 'Rser':
        factor = 1000.0 if not inverse else 0.001
        return data * factor
    elif conversion_type == 'Rsh':
        factor = 0.001 if not inverse else 1000.0
        return data * factor
    elif conversion_type in ['Eta', 'FF']:
        factor = 100.0 if not inverse else 0.01
        return data * factor
    else:
        return data


def validate_filter_condition(column: str, operator: str, value: str) -> bool:
    """Validate filter condition"""
    valid_columns = ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
    valid_operators = ['<', '>']
    
    return (column in valid_columns and 
            operator in valid_operators and 
            is_number(value))


def apply_filter(data: pd.DataFrame, 
                 column: str, 
                 operator: str, 
                 value: float) -> pd.DataFrame:
    """
    Apply a single filter to data
    Returns filtered data (keeps data where condition is FALSE, i.e., removes outliers)
    """
    if column not in data.columns:
        return data
    
    if operator == '>':
        # Keep data where value <= threshold (remove values > threshold)
        return data[data[column] <= value]
    elif operator == '<':
        # Keep data where value >= threshold (remove values < threshold)
        return data[data[column] >= value]
    else:
        return data


def count_filtered_out(data: pd.DataFrame, 
                       column: str, 
                       operator: str, 
                       value: float) -> int:
    """Count number of rows that would be filtered out"""
    if column not in data.columns:
        return 0
    
    if operator == '>':
        return int((data[column] > value).sum())
    elif operator == '<':
        return int((data[column] < value).sum())
    else:
        return 0
