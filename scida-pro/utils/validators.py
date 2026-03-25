# -*- coding: utf-8 -*-
import re
from typing import Optional


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def remove_whitespace(s: str) -> str:
    if not isinstance(s, str):
        return ''
    result = s.replace(' ', '')
    result = result.replace('\t', '')
    return result


def is_valid_filename(filename: str) -> bool:
    if not filename:
        return False
    try:
        filename.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def sanitize_filename(name: str, max_length: int = 40) -> str:
    keepcharacters = (' ', '.', '_')
    sanitized = ''.join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
    return sanitized[:max_length]


def validate_filter_value(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def validate_filter_operator(op: str) -> bool:
    return op in ['<', '>']
