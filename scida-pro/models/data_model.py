# -*- coding: utf-8 -*-
"""数据模型 - 太阳能电池数据结构和处理"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class FilterOperator(Enum):
    """过滤器操作符"""
    GREATER = ">"
    LESS = "<"
    EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


@dataclass
class DataFilter:
    """数据过滤器"""
    column: str
    operator: str
    value: float
    
    def __post_init__(self) -> None:
        """验证操作符"""
        valid_operators = ['>', '<', '==', '>=', '<=']
        if self.operator not in valid_operators:
            raise ValueError(f"无效的操作符: {self.operator}")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用过滤器到数据"""
        if self.operator == '>':
            return data[data[self.column] > self.value]
        elif self.operator == '<':
            return data[data[self.column] < self.value]
        elif self.operator == '==':
            return data[data[self.column] == self.value]
        elif self.operator == '>=':
            return data[data[self.column] >= self.value]
        elif self.operator == '<=':
            return data[data[self.column] <= self.value]
        return data
    
    def count_yield_loss(self, data: pd.DataFrame) -> int:
        """计算产损数量"""
        if self.operator == '>':
            return (data[self.column] > self.value).sum()
        elif self.operator == '<':
            return (data[self.column] < self.value).sum()
        elif self.operator == '==':
            return (data[self.column] == self.value).sum()
        elif self.operator == '>=':
            return (data[self.column] >= self.value).sum()
        elif self.operator == '<=':
            return (data[self.column] <= self.value).sum()
        return 0
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"{self.column}{self.operator}{self.value}"


@dataclass
class SummaryStats:
    """汇总统计信息"""
    best_cell: pd.Series = field(default_factory=pd.Series)
    median: pd.Series = field(default_factory=pd.Series)
    average: pd.Series = field(default_factory=pd.Series)
    std_dev: pd.Series = field(default_factory=pd.Series)
    
    def to_dataframe(self, columns: List[str]) -> pd.DataFrame:
        """转换为DataFrame"""
        data = {
            'Best cell': self.best_cell,
            'Median': self.median,
            'Average': self.average,
            'Std.dev.': self.std_dev
        }
        df = pd.DataFrame(data).T
        df.columns = columns
        return df


class SolarCellData:
    """太阳能电池数据类"""
    
    # 标准列名
    STANDARD_COLUMNS = ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
    
    def __init__(self, data: pd.DataFrame, name: str = "") -> None:
        """
        初始化太阳能电池数据
        
        Args:
            data: 原始数据DataFrame
            name: 数据集名称
        """
        self._data = data.copy()
        self._name = name
        self._original_count = len(data)
        self._filters_applied: List[DataFilter] = []
        
        # 设置索引名称
        if name:
            self._data.index.name = name
    
    @property
    def data(self) -> pd.DataFrame:
        """获取数据"""
        return self._data
    
    @property
    def name(self) -> str:
        """获取数据集名称"""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """设置数据集名称"""
        self._name = value
        self._data.index.name = value
    
    @property
    def count(self) -> int:
        """获取数据条数"""
        return len(self._data)
 
    @property
    def original_count(self) -> int:
        """获取原始数据条数"""
        return self._original_count
    
    @property
    def columns(self) -> List[str]:
        """获取列名列表"""
        return list(self._data.columns)
    
    def get_column(self, column: str) -> pd.Series:
        """获取指定列数据"""
        if column not in self._data.columns:
            raise KeyError(f"列 {column} 不存在")
        return self._data[column]
    
    def apply_filters(self, filters: List[DataFilter]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        应用过滤器
        
        Args:
            filters: 过滤器列表
            
        Returns:
            (过滤后的数据, 产损信息字典)
        """
        filtered_data = self._data.copy()
        yield_loss_info = {}
        
        for i, filter_obj in enumerate(filters):
            loss_count = filter_obj.count_yield_loss(filtered_data)
            yield_loss_info[f'Filter_{i+1}'] = {
                'filter': filter_obj.to_string(),
                'loss_count': int(loss_count)
            }
            filtered_data = filter_obj.apply(filtered_data)
        
        self._data = filtered_data
        self._filters_applied = filters
        
        return filtered_data, yield_loss_info
    
    def calculate_summary(self) -> SummaryStats:
        """计算汇总统计信息"""
        stats = SummaryStats()
        
        if self._data.empty:
            return stats
        
        # Best cell (效率最高的行)
        if 'Eta' in self._data.columns:
            best_idx = self._data['Eta'].idxmax()
            stats.best_cell = self._data.loc[best_idx]
        
        # 中位数
        stats.median = self._data.median()
        
        # 平均值
        stats.average = self._data.mean()
        
        # 标准差 (只对特定列计算)
        params_with_std = ['Uoc', 'Isc', 'FF', 'Eta']
        for col in params_with_std:
            if col in self._data.columns:
                stats.std_dev[col] = self._data[col].std()
        
        return stats
    
    def calculate_correlation(self) -> Optional[pd.DataFrame]:
        """计算相关性矩阵"""
        if len(self._data) <= 1:
            return None
        
        corr = self._data.corr().round(2)
        
        # 某些列不计算相关性
        exclude_cols = ['RserLfDfIEC', 'Rsh', 'IRev1']
        for col in exclude_cols:
            if col in corr.columns:
                corr.loc[:, col] = np.nan
                corr.loc[col, :] = np.nan
        
        # 删除全为NaN的行和列
        corr = corr.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
        return corr
    
    def to_csv(self, filepath: str) -> None:
        """导出为CSV文件"""
        self._data.to_csv(filepath, index=False)
    
    @classmethod
    def from_csv(cls, filepath: str, columns: List[str], name: str = "") -> Optional[SolarCellData]:
        """从CSV文件加载数据"""
        try:
            df = pd.read_csv(filepath)[columns].dropna()
            return cls(df, name)
        except (KeyError, FileNotFoundError):
            return None
    
    @classmethod
    def from_excel(cls, filepath: str, columns: List[str], name: str = "") -> Optional[SolarCellData]:
        """从Excel文件加载数据"""
        try:
            xl_file = pd.read_excel(filepath)
            df = xl_file[columns].dropna()
            return cls(df, name)
        except (KeyError, FileNotFoundError):
            return None
    
    def is_empty(self) -> bool:
        """检查数据是否为空"""
        return self._data.empty
    
    def copy(self) -> SolarCellData:
        """创建数据副本"""
        new_data = SolarCellData(self._data.copy(), self._name)
        new_data._original_count = self._original_count
        return new_data
