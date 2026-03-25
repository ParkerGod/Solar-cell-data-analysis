# -*- coding: utf-8 -*-
import logging
import os
from typing import Optional


_logger: Optional[logging.Logger] = None


def setup_logger(
    name: str = 'scida_pro',
    level: str = 'INFO',
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file: Optional[str] = None
) -> logging.Logger:
    global _logger
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter(log_format)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger


def get_logger(name: str = 'scida_pro') -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = setup_logger(name)
    return _logger
