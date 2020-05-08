# -*- coding: utf-8 -*-
"""pytest配置和fixtures"""

import pytest
import pandas as pd
import numpy as np

# 尝试导入PyQt5，如果失败则使用mock
try:
    from PyQt5 import QtWidgets, QtGui
    HAS_QT = True
except ImportError:
    HAS_QT = False
    from unittest.mock import MagicMock
    QtWidgets = MagicMock()
    QtGui = MagicMock()


@pytest.fixture
def sample_iv_data() -> pd.DataFrame:
    """创建示例IV测试数据"""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        'Uoc': np.random.normal(0.66, 0.01, n_samples),
        'Isc': np.random.normal(8.7, 0.1, n_samples),
        'RserLfDfIEC': np.random.normal(0.3, 0.05, n_samples),
        'Rsh': np.random.normal(1200, 100, n_samples),
        'FF': np.random.normal(77, 1, n_samples),
        'Eta': np.random.normal(20, 0.5, n_samples),
        'IRev1': np.random.normal(0.2, 0.05, n_samples)
    })


@pytest.fixture
def qapp():
    """创建QApplication实例用于测试"""
    if not HAS_QT:
        pytest.skip("PyQt5 not available")
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


@pytest.fixture
def series_list_model(qapp) -> 'QtGui.QStandardItemModel':
    """创建标准项模型"""
    if not HAS_QT:
        pytest.skip("PyQt5 not available")
    return QtGui.QStandardItemModel()
