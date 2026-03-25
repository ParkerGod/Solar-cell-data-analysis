# -*- coding: utf-8 -*-
"""数据控制器 - 管理数据加载、过滤和处理"""

from __future__ import annotations

import os
import ntpath
from typing import Dict, List, Optional, Tuple, Any, Callable
from pathlib import Path

import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtGui

from ..models.data_model import SolarCellData, DataFilter, SummaryStats
from ..utils import ConfigManager, get_logger


class DataController(QtCore.QObject):
    """数据控制器类"""
    
    # 信号定义
    data_loaded = QtCore.pyqtSignal(int, str)  # 数据加载信号 (索引, 名称)
    data_filtered = QtCore.pyqtSignal()  # 数据过滤信号
    data_combined = QtCore.pyqtSignal()  # 数据合并信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误信号
    
    def __init__(
        self,
        series_list_model: QtGui.QStandardItemModel,
        config_manager: Optional[ConfigManager] = None
    ) -> None:
        """
        初始化数据控制器
        
        Args:
            series_list_model: 数据集列表模型
            config_manager: 配置管理器
        """
        super().__init__()
        
        self._logger = get_logger(__name__)
        self._config = config_manager or ConfigManager()
        
        # 数据存储
        self._data: Dict[int, SolarCellData] = {}
        self._series_list_model = series_list_model
        
        # 过滤器
        self._default_filters: List[DataFilter] = []
        self._user_filters: List[DataFilter] = []
        
        # 产损数据
        self._yield_loss_data: Dict[int, pd.DataFrame] = {}
        
        # 初始化默认过滤器
        self._init_default_filters()
    
    def _init_default_filters(self) -> None:
        """初始化默认过滤器"""
        default_filters_config = self._config.get_default_filters()
        for filter_config in default_filters_config:
            if len(filter_config) >= 3:
                self._default_filters.append(
                    DataFilter(
                        column=str(filter_config[0]),
                        operator=str(filter_config[1]),
                        value=float(filter_config[2])
                    )
                )
    
    @property
    def data(self) -> Dict[int, SolarCellData]:
        """获取所有数据"""
        return self._data
    
    @property
    def data_count(self) -> int:
        """获取数据集数量"""
        return len(self._data)
    
    def get_data(self, index: int) -> Optional[SolarCellData]:
        """获取指定索引的数据"""
        return self._data.get(index)
    
    def get_dataframes(self) -> Dict[int, pd.DataFrame]:
        """获取所有DataFrame字典"""
        return {i: data.data for i, data in self._data.items()}
    
    def load_files(
        self,
        file_paths: List[str],
        label_format: int = 0
    ) -> Tuple[bool, List[str]]:
        """
        加载数据文件
        
        Args:
            file_paths: 文件路径列表
            label_format: 标签格式索引
            
        Returns:
            (是否成功, 警告信息列表)
        """
        warnings: List[str] = []
        
        # 获取标签格式
        label_formats = self._config.get_label_formats()
        format_keys = list(label_formats.keys())
        
        if label_format >= len(format_keys):
            label_format = 0
        
        # 使用选定的格式读取，但列名会被重命名为标准格式(format_a)
        source_format = label_formats.get(format_keys[label_format], [])
        standard_columns = label_formats.get('format_a', SolarCellData.STANDARD_COLUMNS)
        
        for file_path in file_paths:
            # 检查文件名是否为ASCII
            try:
                file_path.encode('ascii')
            except UnicodeEncodeError:
                warnings.append("non_ascii_filename")
                continue
            
            # 加载数据 - 使用源格式列名读取
            data = self._load_single_file(file_path, source_format)
            
            if data is None:
                warnings.append("read_error")
                continue
            
            # 重命名列为标准名称
            try:
                data.data.columns = standard_columns
            except (KeyError, ValueError) as e:
                self._logger.error(f"列名重命名失败: {e}")
                continue
            
            # 转换为数值
            data.data = data.data.apply(pd.to_numeric)
            data.data = data.data[data.data > 0]
            
            # 检查数据是否为空
            if data.is_empty():
                warnings.append("empty_data")
                continue
            
            # 应用格式特定的转换
            self._apply_format_conversion(data, label_format)
            
            # 添加到数据字典
            index = len(self._data)
            self._data[index] = data
            
            # 添加到列表模型
            self._add_to_list_model(data.name)
            
            self.data_loaded.emit(index, data.name)
        
        return len(self._data) > 0, warnings
    
    def _load_single_file(
        self,
        file_path: str,
        columns: List[str]
    ) -> Optional[SolarCellData]:
        """加载单个文件"""
        _, ext = ntpath.splitext(file_path)
        name = ntpath.splitext(ntpath.basename(file_path))[0][:39]
        
        try:
            if ext.lower() == '.csv':
                try:
                    df = pd.read_csv(file_path)[columns].dropna()
                except KeyError:
                    df = pd.read_csv(file_path, sep=';')[columns].dropna()
                return SolarCellData(df, name)
            else:
                xl_file = pd.read_excel(file_path)
                df = xl_file[columns].dropna()
                return SolarCellData(df, name)
        except Exception as e:
            self._logger.error(f"加载文件失败 {file_path}: {e}")
            return None
    
    def _apply_format_conversion(self, data: SolarCellData, label_format: int) -> None:
        """应用格式特定的转换"""
        if label_format == 1:
            # 格式B: Eta和FF需要乘以100
            if 'Eta' in data.data.columns:
                data.data.loc[:, 'Eta'] *= 100
            if 'FF' in data.data.columns:
                data.data.loc[:, 'FF'] *= 100
        elif label_format == 3:
            # 格式D: Eta需要乘以100
            if 'Eta' in data.data.columns:
                data.data.loc[:, 'Eta'] *= 100
    
    def _add_to_list_model(self, name: str) -> None:
        """添加项目到列表模型"""
        item = QtGui.QStandardItem(name)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        self._series_list_model.appendRow(item)
    
    def combine_datasets(self) -> bool:
        """合并所有数据集"""
        if len(self._data) <= 1:
            return False
        
        # 清除相关数据
        self._yield_loss_data.clear()
        self._series_list_model.clear()
        self._series_list_model.setHorizontalHeaderLabels(['Data series'])
        
        # 合并数据
        combined_data = self._data[0].data
        for i in range(1, len(self._data)):
            combined_data = pd.concat([combined_data, self._data[i].data], ignore_index=True)
        
        # 创建新的合并数据集
        self._data.clear()
        self._data[0] = SolarCellData(combined_data, 'Combined data set')
        
        # 更新列表
        self._add_to_list_model('Combined data set')
        
        self.data_combined.emit()
        return True
    
    def apply_filters(self, filters: Optional[List[DataFilter]] = None) -> Dict[int, Any]:
        """
        应用过滤器
        
        Args:
            filters: 过滤器列表，None则使用默认过滤器
            
        Returns:
            产损信息字典
        """
        filters_to_apply = filters or self._default_filters
        yield_loss_results = {}
        
        for index, data in self._data.items():
            if index not in self._yield_loss_data:
                # 创建产损DataFrame
                yl_columns = [f'Filter {i+1}' for i in range(12)]
                yl_df = pd.DataFrame(index=['Filter', 'Loss count'], columns=yl_columns)
                yl_df.index.name = data.original_count
                self._yield_loss_data[index] = yl_df
            
            # 应用过滤器
            _, loss_info = data.apply_filters(filters_to_apply)
            yield_loss_results[index] = loss_info
            
            # 更新产损DataFrame
            for i, (key, info) in enumerate(loss_info.items()):
                if i < 12:
                    self._yield_loss_data[index].iloc[0, i] = info['filter']
                    self._yield_loss_data[index].iloc[1, i] = info['loss_count']
        
        # 更新列表模型
        self._series_list_model.clear()
        self._series_list_model.setHorizontalHeaderLabels(['Data series'])
        for index, data in self._data.items():
            item = QtGui.QStandardItem(data.name)
            self._series_list_model.appendRow(item)
        
        self.data_filtered.emit()
        return yield_loss_results
    
    def save_data(self, dest_dir: str) -> List[str]:
        """
        保存数据到目录
        
        Args:
            dest_dir: 目标目录
            
        Returns:
            保存的文件路径列表
        """
        saved_files: List[str] = []
        
        for index, data in self._data.items():
            filename = f"{data.name}.csv"
            
            if os.name == 'nt':
                filepath = os.path.join(dest_dir, filename)
            else:
                filepath = os.path.join(dest_dir, filename)
            
            data.to_csv(filepath)
            saved_files.append(filepath)
        
        return saved_files
    
    def clear(self) -> None:
        """清除所有数据"""
        self._data.clear()
        self._yield_loss_data.clear()
        self._series_list_model.clear()
    
    def rename_dataset(self, index: int, new_name: str) -> bool:
        """
        重命名数据集
        
        Args:
            index: 数据集索引
            new_name: 新名称
            
        Returns:
            是否成功
        """
        if index not in self._data:
            return False
        
        # 验证名称
        keep_chars = (' ', '.', '_')
        valid_name = "".join(c for c in new_name if c.isalnum() or c in keep_chars).rstrip()
        
        if not valid_name:
            return False
        
        self._data[index].name = valid_name
        return True
