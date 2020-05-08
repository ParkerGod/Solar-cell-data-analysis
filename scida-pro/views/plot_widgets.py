# -*- coding: utf-8 -*-
"""具体图表组件实现"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Dict, List

from .base_plot_widget import BasePlotWidget
from ..models.plot_model import PlotConfig, PlotSelection, AxisConfig, LegendConfig


class CorrVocIscWidget(BasePlotWidget):
    """Voc-Isc相关性图表"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        # 设置特定配置
        config = plot_config or PlotConfig()
        config.dotsize_selection = 20
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Correlation"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        return AxisConfig(
            x_label=cm.get_axis_label('voc'),
            y_label=cm.get_axis_label('isc')
        )
    
    def _plot_data(self) -> None:
        for i in self._plot_selection.selected_indices:
            if i in self._data:
                self.axes.scatter(
                    self._data[i]['Uoc'],
                    self._data[i]['Isc'],
                    c=self._plot_config.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._plot_config.dotsize_selection,
                    label=self._data[i].index.name
                )


class CorrEtaFFWidget(BasePlotWidget):
    """Eta-FF相关性图表"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        config = plot_config or PlotConfig()
        config.dotsize_selection = 20
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Correlation"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        return AxisConfig(
            x_label=cm.get_axis_label('ff'),
            y_label=cm.get_axis_label('eta')
        )
    
    def _plot_data(self) -> None:
        for i in self._plot_selection.selected_indices:
            if i in self._data:
                self.axes.scatter(
                    self._data[i]['FF'],
                    self._data[i]['Eta'],
                    c=self._plot_config.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._plot_config.dotsize_selection,
                    label=self._data[i].index.name
                )


class CorrRshFFWidget(BasePlotWidget):
    """Rsh-FF相关性图表"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        config = plot_config or PlotConfig()
        config.dotsize_selection = 20
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Correlation"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        return AxisConfig(
            x_label=cm.get_axis_label('ff'),
            y_label=cm.get_axis_label('rsh'),
            y_scale='log'
        )
    
    def _plot_data(self) -> None:
        for i in self._plot_selection.selected_indices:
            if i in self._data:
                self.axes.scatter(
                    self._data[i]['FF'],
                    self._data[i]['Rsh'],
                    c=self._plot_config.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._plot_config.dotsize_selection,
                    label=self._data[i].index.name
                )


class DistLtoHWidget(BasePlotWidget):
    """低至高分布图表 (Eta排序)"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        config = plot_config or PlotConfig()
        config.dotsize_selection = 200
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Distribution"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        return AxisConfig(
            x_label=cm.get_axis_label('eta'),
            y_label=cm.get_axis_label('normalized_cell'),
            y_scale='log'
        )
    
    def _get_legend_config(self) -> LegendConfig:
        return LegendConfig(
            loc='upper left',
            scatterpoints=1,
            markerscale=1,
            frameon=False
        )
    
    def _plot_data(self) -> None:
        xmin = 1e4
        xmax = 0
        ymin = -1
        
        for i in self._plot_selection.selected_indices:
            if i not in self._data:
                continue
                
            se = pd.DataFrame(np.sort(self._data[i]['Eta']))
            if se.iloc[:, 0].min() <= xmin:
                xmin = se.iloc[:, 0].min()
            if se.iloc[:, 0].max() >= xmax:
                xmax = se.iloc[:, 0].max()
            if np.log10(1 / len(se)) < ymin:
                ymin = np.log10(1 / len(se))
            
            se.index = (se.index + 1) / len(se)
            self.axes.scatter(
                se,
                se.index,
                c=self._plot_config.get_color(i),
                edgecolor=self._plot_config.get_color(i),
                marker=r'$\circ$',
                s=self._plot_config.dotsize_selection,
                label=self._data[i].index.name
            )
        
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))
        self.axes.set_ylim((10 ** np.floor(ymin), 2))


class DensEtaWidget(BasePlotWidget):
    """Eta密度图表"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        config = plot_config or PlotConfig()
        config.dotsize_enabled = False
        config.linewidth_enabled = True
        config.linewidth_selection = 3
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Density"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        return AxisConfig(
            x_label=cm.get_axis_label('eta'),
            y_label=cm.get_axis_label('density')
        )
    
    def _get_legend_config(self) -> LegendConfig:
        return LegendConfig(
            loc='upper left',
            scatterpoints=1,
            markerscale=1,
            frameon=False
        )
    
    def _plot_data(self) -> None:
        xmin = 1e4
        xmax = 0
        
        for i in self._plot_selection.selected_indices:
            if i not in self._data:
                continue
                
            se = self._data[i]['Eta']
            if se.min() <= xmin:
                xmin = se.min()
            if se.max() >= xmax:
                xmax = se.max()
            
            se.plot(
                kind='kde',
                c=self._plot_config.get_color(i),
                lw=self._plot_config.linewidth_selection,
                label=self._data[i].index.name,
                ax=self.axes
            )
        
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))


class DistWTWidget(BasePlotWidget):
    """遍历图表 (Walk-through)"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        param: str = "Eta",
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._param = param
        config = plot_config or PlotConfig()
        config.dotsize_selection = 20
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Walkthrough"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        
        # 参数到轴标签的映射
        param_label_map = {
            'Uoc': cm.get_axis_label('voc'),
            'Isc': cm.get_axis_label('isc'),
            'Voc*Isc': cm.get_axis_label('vocisc'),
            'FF': cm.get_axis_label('ff'),
            'Eta': cm.get_axis_label('eta'),
            'RserLfDfIEC': cm.get_axis_label('rser'),
            'Rsh': cm.get_axis_label('rsh'),
            'IRev1': cm.get_axis_label('irev')
        }
        
        return AxisConfig(
            x_label=cm.get_axis_label('normalized_cell'),
            y_label=param_label_map.get(self._param, self._param)
        )
    
    def _get_legend_config(self) -> LegendConfig:
        return LegendConfig(
            loc='lower left',
            scatterpoints=1,
            markerscale=3,
            frameon=True
        )
    
    def _plot_data(self) -> None:
        for i in self._plot_selection.selected_indices:
            if i not in self._data:
                continue
            
            # 根据参数获取数据
            if self._param == 'Voc*Isc':
                se = pd.DataFrame(self._data[i]['Uoc'] * self._data[i]['Isc'])
            elif self._param == 'RserLfDfIEC':
                se = pd.DataFrame(1000 * self._data[i][self._param])
            elif self._param == 'Rsh':
                se = pd.DataFrame(0.001 * self._data[i][self._param])
            else:
                se = pd.DataFrame(self._data[i][self._param])
            
            se.index = (se.index + 1) / len(se)
            self.axes.scatter(
                se.index,
                se,
                c=self._plot_config.get_color(i),
                edgecolors='white',
                linewidths=0.3,
                s=self._plot_config.dotsize_selection,
                label=self._data[i].index.name
            )
        
        self.axes.set_xlim((0, 1))


class DistRMWidget(BasePlotWidget):
    """滚动均值图表 (Rolling Mean)"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        param: str = "Eta",
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._param = param
        config = plot_config or PlotConfig()
        config.dotsize_enabled = False
        config.linewidth_enabled = True
        config.linewidth_selection = 3
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Rolling mean"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        
        param_label_map = {
            'Uoc': cm.get_axis_label('voc'),
            'Isc': cm.get_axis_label('isc'),
            'Voc*Isc': cm.get_axis_label('vocisc'),
            'FF': cm.get_axis_label('ff'),
            'Eta': cm.get_axis_label('eta'),
            'RserLfDfIEC': cm.get_axis_label('rser'),
            'Rsh': cm.get_axis_label('rsh'),
            'IRev1': cm.get_axis_label('irev')
        }
        
        return AxisConfig(
            x_label=cm.get_axis_label('normalized_cell'),
            y_label=param_label_map.get(self._param, self._param)
        )
    
    def _get_legend_config(self) -> LegendConfig:
        return LegendConfig(
            loc='lower left',
            scatterpoints=1,
            markerscale=3,
            frameon=True
        )
    
    def _plot_data(self) -> None:
        for i in self._plot_selection.selected_indices:
            if i not in self._data:
                continue
            
            # 根据参数获取数据
            if self._param == 'Voc*Isc':
                se = pd.DataFrame(self._data[i]['Uoc'] * self._data[i]['Isc'])
            elif self._param == 'RserLfDfIEC':
                se = pd.DataFrame(1000 * self._data[i][self._param])
            elif self._param == 'Rsh':
                se = pd.DataFrame(0.001 * self._data[i][self._param])
            else:
                se = pd.DataFrame(self._data[i][self._param])
            
            se.index = (se.index + 1) / len(se)
            window = int(np.floor(len(se) * 0.1)) if len(se) > 100 else 1
            rm = se.rolling(center=True, window=window).mean()
            
            self.axes.plot(
                rm.index,
                rm,
                c=self._plot_config.get_color(i),
                lw=self._plot_config.linewidth_selection,
                label=self._data[i].index.name
            )


class IVBoxPlotWidget(BasePlotWidget):
    """箱线图"""
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        param: str = "Eta",
        plot_config: Optional[PlotConfig] = None,
        plot_selection: Optional[PlotSelection] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._param = param
        config = plot_config or PlotConfig()
        config.grid_enabled = False
        config.legend_enabled = False
        config.dotsize_enabled = False
        config.linewidth_enabled = False
        super().__init__(parent, config, plot_selection, data)
    
    def _get_window_title(self) -> str:
        return "Boxplot"
    
    def _get_axis_config(self) -> AxisConfig:
        from ..utils import ConfigManager
        cm = ConfigManager()
        
        param_label_map = {
            'Uoc': cm.get_axis_label('voc'),
            'Isc': cm.get_axis_label('isc'),
            'Voc*Isc': cm.get_axis_label('vocisc'),
            'FF': cm.get_axis_label('ff'),
            'Eta': cm.get_axis_label('eta'),
            'RserLfDfIEC': cm.get_axis_label('rser'),
            'Rsh': cm.get_axis_label('rsh'),
            'IRev1': cm.get_axis_label('irev')
        }
        
        return AxisConfig(
            y_label=param_label_map.get(self._param, self._param)
        )
    
    def _plot_data(self) -> None:
        data_to_plot = []
        labels = []
        
        for i in self._plot_selection.selected_indices:
            if i not in self._data:
                continue
            
            if self._param == 'Voc*Isc':
                values = self._data[i]['Uoc'] * self._data[i]['Isc']
            elif self._param == 'RserLfDfIEC':
                values = 1000 * self._data[i][self._param]
            elif self._param == 'Rsh':
                values = 0.001 * self._data[i][self._param]
            else:
                values = self._data[i][self._param]
            
            data_to_plot.append(values)
            labels.append(self._data[i].index.name)
        
        if data_to_plot:
            bp = self.axes.boxplot(
                data_to_plot,
                labels=labels,
                patch_artist=True
            )
            
            # 设置箱体颜色
            for patch, color in zip(bp['boxes'], self._plot_config.colors):
                patch.set_facecolor(color)


# 导入QtWidgets用于类型提示
from PyQt5 import QtWidgets
