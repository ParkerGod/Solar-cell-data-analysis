# -*- coding: utf-8 -*-
"""
Utils package for SCiDA Pro
Contains configuration management, logging, and helper functions
"""

from .config_manager import ConfigManager
from .logger import AppLogger, get_logger
from .helpers import (
    is_number,
    remove_whitespace,
    is_valid_ascii_filename,
    sanitize_filename,
    get_file_extension,
    calculate_statistics,
    calculate_correlation,
    safe_division,
    apply_unit_conversion,
    validate_filter_condition,
    apply_filter,
    count_filtered_out
)

__all__ = [
    'ConfigManager',
    'AppLogger',
    'get_logger',
    'is_number',
    'remove_whitespace',
    'is_valid_ascii_filename',
    'sanitize_filename',
    'get_file_extension',
    'calculate_statistics',
    'calculate_correlation',
    'safe_division',
    'apply_unit_conversion',
    'validate_filter_condition',
    'apply_filter',
    'count_filtered_out'
]
