# -*- coding: utf-8 -*-
"""报告控制器 - 管理报告生成和导出"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple
import os

import pandas as pd
import numpy as np
from PyQt5 import QtCore

from ..models.data_model import SolarCellData, SummaryStats
from ..utils import ConfigManager, get_logger


class ReportController(QtCore.QObject):
    """报告控制器类"""
    
    # 信号定义
    report_generated = QtCore.pyqtSignal(str)  # 报告生成信号 (文件路径)
    report_error = QtCore.pyqtSignal(str)  # 报告错误信号
    
    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None
    ) -> None:
        """
        初始化报告控制器
        
        Args:
            config_manager: 配置管理器
        """
        super().__init__()
        
        self._logger = get_logger(__name__)
        self._config = config_manager or ConfigManager()
        
        # 汇总配置
        summary_config = self._config.get_summary_config()
        self._summary_index = summary_config.get('index', ['Best cell', 'Median', 'Average', 'Std.dev.'])
        self._summary_columns = summary_config.get('columns', [
            'Voc [V]', 'Isc [A]', 'Rser [mOhm*cm2]', 'Rshunt [kOhm]', 'FF [%]', 'Eta [%]', 'Irev [A]'
        ])
        self._rounding = summary_config.get('rounding', [3, 2, 2, 2, 1, 2, 2])
    
    def generate_excel_report(
        self,
        data: Dict[int, SolarCellData],
        yield_loss_data: Dict[int, pd.DataFrame],
        output_path: str
    ) -> bool:
        """
        生成Excel报告
        
        Args:
            data: 数据字典
            yield_loss_data: 产损数据字典
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            # 检查文件名
            output_path.encode('ascii')
        except UnicodeEncodeError:
            self.report_error.emit("non_ascii_filename")
            return False
        
        try:
            # 生成汇总表
            summary_tables = self._generate_summary_tables(data)
            
            # 生成产损表
            yield_loss_tables = self._generate_yield_loss_tables(data, yield_loss_data)
            
            # 生成相关性表
            correlation_tables = self._generate_correlation_tables(data)
            
            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                if summary_tables:
                    output1 = pd.concat(summary_tables)
                    output1.to_excel(writer, sheet_name='Summary')
                
                if yield_loss_tables:
                    output2 = pd.concat(yield_loss_tables)
                    output2.to_excel(writer, sheet_name='Yield loss')
                
                if correlation_tables:
                    output3 = pd.concat(correlation_tables)
                    output3.to_excel(writer, sheet_name='Correlation')
            
            self.report_generated.emit(output_path)
            return True
            
        except Exception as e:
            self._logger.error(f"生成报告失败: {e}")
            self.report_error.emit(str(e))
            return False
    
    def _generate_summary_tables(
        self,
        data: Dict[int, SolarCellData]
    ) -> List[pd.DataFrame]:
        """生成汇总表"""
        tables = []
        
        for index, cell_data in data.items():
            stats = cell_data.calculate_summary()
            
            # 创建DataFrame
            df = pd.DataFrame(index=self._summary_index, columns=self._summary_columns)
            df.index.name = 'Data property'
            df['Data set'] = f"{cell_data.name} ({cell_data.count} cells)"
            df = df.set_index('Data set', append=True).swaplevel(0, 1)
            
            # 填充数据
            for i2, value in enumerate(cell_data.data.max()):
                df.iloc[0, i2] = cell_data.data.iloc[cell_data.data.idxmax()[5]][i2] if 'Eta' in cell_data.data.columns else value
                df.iloc[1, i2] = cell_data.data.median()[i2]
                df.iloc[2, i2] = cell_data.data.mean()[i2]
                
                # 标准差只对特定列计算
                param_list = [0, 1, 4, 5]
                if i2 in param_list:
                    df.iloc[3, i2] = cell_data.data.std()[i2]
                else:
                    df.iloc[3, i2] = np.nan
            
            # 单位转换
            df.iloc[:, 2] = df.iloc[:, 2] * 1000  # Rser
            df.iloc[:, 3] = df.iloc[:, 3] / 1000  # Rshunt
            
            # 四舍五入
            for i3, decimals in enumerate(self._rounding):
                df.iloc[:, i3] = np.round(df.iloc[:, i3].astype(np.double), decimals=decimals)
            
            tables.append(df)
        
        return tables
    
    def _generate_yield_loss_tables(
        self,
        data: Dict[int, SolarCellData],
        yield_loss_data: Dict[int, pd.DataFrame]
    ) -> List[pd.DataFrame]:
        """生成产损表"""
        tables = []
        
        for index, yl_df in yield_loss_data.items():
            if index not in data:
                continue
            
            cell_data = data[index]
            yl_copy = yl_df.copy()
            
            # 添加总计列
            yl_copy['Total'] = np.nan
            yl_copy.iloc[1, 12] = yl_copy.iloc[1, :].sum()
            
            # 添加百分比行
            yl_copy.loc['Loss %'] = np.nan
            
            for j in range(len(yl_copy.columns)):
                if not pd.isna(yl_copy.iloc[1, j]):
                    yl_copy.iloc[2, j] = np.round(
                        100 * yl_copy.iloc[1, j] / cell_data.original_count,
                        decimals=2
                    )
            
            # 删除空列
            yl_copy = yl_copy.dropna(axis=1, how='all')
            
            # 设置索引
            yl_copy.index.name = 'Data property'
            yl_copy['Data set'] = f"{cell_data.name} ({cell_data.original_count} cells)"
            yl_copy = yl_copy.set_index('Data set', append=True).swaplevel(0, 1)
            
            tables.append(yl_copy)
        
        return tables
    
    def _generate_correlation_tables(
        self,
        data: Dict[int, SolarCellData]
    ) -> List[pd.DataFrame]:
        """生成相关性表"""
        tables = []
        
        for index, cell_data in data.items():
            corr = cell_data.calculate_correlation()
            
            if corr is None:
                continue
            
            corr.index.name = 'Data property'
            corr['Data set'] = f"{cell_data.name} ({cell_data.count} cells)"
            corr = corr.set_index('Data set', append=True).swaplevel(0, 1)
            
            tables.append(corr)
        
        return tables
    
    def export_to_csv(
        self,
        data: SolarCellData,
        output_path: str
    ) -> bool:
        """
        导出数据到CSV
        
        Args:
            data: 太阳能电池数据
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            data.to_csv(output_path)
            return True
        except Exception as e:
            self._logger.error(f"导出CSV失败: {e}")
            return False
