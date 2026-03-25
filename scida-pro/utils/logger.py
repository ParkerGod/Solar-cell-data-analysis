# -*- coding: utf-8 -*-
"""
Logger utility for SCiDA Pro
Provides logging functionality
"""

import logging
import os
from typing import Optional


class AppLogger:
    """Application logger class"""
    
    _instance: Optional['AppLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logging configuration"""
        self._logger = logging.getLogger('scida_pro')
        self._logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # Create file handler if logs directory exists
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(
                os.path.join(log_dir, 'scida_pro.log'),
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception:
            # Fail silently if we can't create log file
            pass
    
    def info(self, message: str) -> None:
        """Log info message"""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        if self._logger:
            self._logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        if self._logger:
            self._logger.debug(message)


def get_logger() -> logging.Logger:
    """Get the application logger instance"""
    return AppLogger()._logger or logging.getLogger('scida_pro')
