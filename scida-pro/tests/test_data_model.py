# -*- coding: utf-8 -*-
"""数据模型单元测试"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from models.data_model import SolarCellData, DataFilter, SummaryStats


class TestDataFilter:
    """DataFilter测试类"""
    
    def test_init_valid_operator(self) -> None:
        """测试有效操作符初始化"""
        filter_obj = DataFilter(column='Eta', operator='>', value=18.0)
        assert filter_obj.column == 'Eta'
        assert filter_obj.operator == '>'
        assert filter_obj.value == 18.0
    
    def test_init_invalid_operator(self) -> None:
        """测试无效操作符初始化"""
        with pytest.raises(ValueError):
            DataFilter(column='Eta', operator='invalid', value=18.0)
    
    def test_apply_greater_than(self) -> None:
        """测试大于过滤器"""
        df = pd.DataFrame({
            'Eta': [15.0, 18.0, 20.0, 16.0],
            'FF': [75.0, 78.0, 80.0, 76.0]
        })
        filter_obj = DataFilter(column='Eta', operator='>', value=17.0)
        result = filter_obj.apply(df)
        
        assert len(result) == 2
        assert all(result['Eta'] > 17.0)
    
    def test_apply_less_than(self) -> None:
        """测试小于过滤器"""
        df = pd.DataFrame({
            'Eta': [15.0, 18.0, 20.0, 16.0],
            'FF': [75.0, 78.0, 80.0, 76.0]
        })
        filter_obj = DataFilter(column='Eta', operator='<', value=17.0)
        result = filter_obj.apply(df)
        
        assert len(result) == 2
        assert all(result['Eta'] < 17.0)
    
    def test_count_yield_loss(self) -> None:
        """测试产损计数"""
        df = pd.DataFrame({
            'Eta': [15.0, 18.0, 20.0, 16.0]
        })
        filter_obj = DataFilter(column='Eta', operator='<', value=17.0)
        count = filter_obj.count_yield_loss(df)
        
        assert count == 2
    
    def test_to_string(self) -> None:
        """测试字符串转换"""
        filter_obj = DataFilter(column='Eta', operator='<', value=17.0)
        assert filter_obj.to_string() == "Eta<17.0"


class TestSolarCellData:
    """SolarCellData测试类"""
    
    @pytest.fixture
    def sample_data(self) -> pd.DataFrame:
        """创建示例数据"""
        return pd.DataFrame({
            'Uoc': [0.65, 0.66, 0.67, 0.68],
            'Isc': [8.5, 8.6, 8.7, 8.8],
            'RserLfDfIEC': [0.5, 0.4, 0.3, 0.2],
            'Rsh': [1000, 1100, 1200, 1300],
            'FF': [75.0, 76.0, 77.0, 78.0],
            'Eta': [18.0, 19.0, 20.0, 21.0],
            'IRev1': [0.1, 0.2, 0.3, 0.4]
        })
    
    def test_init(self, sample_data: pd.DataFrame) -> None:
        """测试初始化"""
        data = SolarCellData(sample_data, "Test Dataset")
        
        assert data.name == "Test Dataset"
        assert data.count == 4
        assert data.original_count == 4
        assert not data.is_empty()
    
    def test_get_column(self, sample_data: pd.DataFrame) -> None:
        """测试获取列"""
        data = SolarCellData(sample_data, "Test")
        eta_col = data.get_column('Eta')
        
        assert len(eta_col) == 4
        assert list(eta_col) == [18.0, 19.0, 20.0, 21.0]
    
    def test_get_column_invalid(self, sample_data: pd.DataFrame) -> None:
        """测试获取无效列"""
        data = SolarCellData(sample_data, "Test")
        
        with pytest.raises(KeyError):
            data.get_column('InvalidColumn')
    
    def test_apply_filters(self, sample_data: pd.DataFrame) -> None:
        """测试应用过滤器"""
        # 使用固定的测试数据而不是随机数据
        df = pd.DataFrame({
            'Uoc': [0.65, 0.66, 0.67, 0.68],
            'Isc': [8.5, 8.6, 8.7, 8.8],
            'RserLfDfIEC': [0.5, 0.4, 0.3, 0.2],
            'Rsh': [1000, 1100, 1200, 1300],
            'FF': [75.0, 76.0, 77.0, 78.0],
            'Eta': [18.0, 19.0, 20.0, 21.0],
            'IRev1': [0.1, 0.2, 0.3, 0.4]
        })
        data = SolarCellData(df, "Test")
        filters = [
            DataFilter(column='Eta', operator='>', value=18.5)
        ]
        
        result_df, loss_info = data.apply_filters(filters)
        
        # Eta > 18.5: 19.0, 20.0, 21.0 (3条), 产损: 18.0 (1条)
        assert len(result_df) == 3
        assert 'Filter_1' in loss_info
        # 产损计数是过滤前满足条件的数量
        assert loss_info['Filter_1']['loss_count'] == 3  # Eta > 18.5 有3条
    
    def test_calculate_summary(self, sample_data: pd.DataFrame) -> None:
        """测试计算汇总统计"""
        data = SolarCellData(sample_data, "Test")
        summary = data.calculate_summary()
        
        assert isinstance(summary, SummaryStats)
        assert not summary.median.empty
        assert not summary.average.empty
    
    def test_calculate_correlation(self, sample_data: pd.DataFrame) -> None:
        """测试计算相关性"""
        data = SolarCellData(sample_data, "Test")
        corr = data.calculate_correlation()
        
        assert corr is not None
        assert 'Eta' in corr.columns
        assert 'FF' in corr.columns
    
    def test_calculate_correlation_insufficient_data(self) -> None:
        """测试数据不足时的相关性计算"""
        df = pd.DataFrame({'Eta': [18.0]})
        data = SolarCellData(df, "Test")
        corr = data.calculate_correlation()
        
        assert corr is None
    
    def test_rename(self, sample_data: pd.DataFrame) -> None:
        """测试重命名"""
        data = SolarCellData(sample_data, "Old Name")
        data.name = "New Name"
        
        assert data.name == "New Name"
        assert data.data.index.name == "New Name"
    
    def test_copy(self, sample_data: pd.DataFrame) -> None:
        """测试复制"""
        data = SolarCellData(sample_data, "Test")
        copied = data.copy()
        
        assert copied.name == data.name
        assert copied.count == data.count
        assert copied.data is not data.data  # 确保是深拷贝
    
    def test_is_empty(self) -> None:
        """测试空数据检查"""
        empty_df = pd.DataFrame()
        data = SolarCellData(empty_df, "Empty")
        
        assert data.is_empty()


class TestSummaryStats:
    """SummaryStats测试类"""
    
    def test_to_dataframe(self) -> None:
        """测试转换为DataFrame"""
        stats = SummaryStats()
        stats.best_cell = pd.Series([0.68, 8.8], index=['Uoc', 'Isc'])
        stats.median = pd.Series([0.665, 8.65], index=['Uoc', 'Isc'])
        stats.average = pd.Series([0.665, 8.65], index=['Uoc', 'Isc'])
        stats.std_dev = pd.Series([0.01, 0.1], index=['Uoc', 'Isc'])
        
        df = stats.to_dataframe(['Uoc [V]', 'Isc [A]'])
        
        assert len(df) == 4
        assert list(df.columns) == ['Uoc [V]', 'Isc [A]']
        assert 'Best cell' in df.index
        assert 'Median' in df.index
