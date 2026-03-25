# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

from .base_plot_widget import BasePlotWidget


class CorrVocIscPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        super().__init__(parent, data, title="Correlation")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        self.set_xlabel(self.get_axis_label('Uoc'))
        self.set_ylabel(self.get_axis_label('Isc'))
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                self.axes.scatter(
                    df['Uoc'],
                    df['Isc'],
                    c=self.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._dotsize_selection,
                    label=df.index.name
                )
        
        self.draw_legend(loc='lower left')
        self.canvas.draw()


class CorrEtaFFPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        super().__init__(parent, data, title="Correlation")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        self.set_xlabel(self.get_axis_label('FF'))
        self.set_ylabel(self.get_axis_label('Eta'))
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                self.axes.scatter(
                    df['FF'],
                    df['Eta'],
                    c=self.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._dotsize_selection,
                    label=df.index.name
                )
        
        self.draw_legend(loc='lower left')
        self.canvas.draw()


class CorrRshFFPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        super().__init__(parent, data, title="Correlation")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        self.set_xlabel(self.get_axis_label('FF'))
        self.set_ylabel(self.get_axis_label('Rsh'))
        self.axes.semilogy()
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                self.axes.scatter(
                    df['FF'],
                    df['Rsh'],
                    c=self.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._dotsize_selection,
                    label=df.index.name
                )
        
        self.draw_legend(loc='lower left')
        self.canvas.draw()


class DistLtoHPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._dotsize_selection = 200
        super().__init__(parent, data, title="Distribution")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        xmin = 1e4
        xmax = 0
        ymin = -1
        
        self.set_xlabel(self.get_axis_label('Eta'))
        self.set_ylabel(r'$\mathrm{\mathsf{Normalized\ cell\ number\ [a.u.]}}$')
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                se = pd.DataFrame(np.sort(df['Eta']))
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
                    c=self.get_color(i),
                    edgecolor=self.get_color(i),
                    marker=r'$\circ$',
                    s=self._dotsize_selection,
                    label=df.index.name
                )
        
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))
        self.axes.semilogy(10 ** np.floor(ymin))
        self.axes.set_ylim((10 ** np.floor(ymin), 2))
        
        self.draw_legend(loc='upper left')
        self.canvas.draw()


class DensEtaPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        self._linewidth_selection = 3
        super().__init__(parent, data, title="Density")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        
        xmin = 1e4
        xmax = 0
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                se = df['Eta']
                if se.min() <= xmin:
                    xmin = se.min()
                if se.max() >= xmax:
                    xmax = se.max()
                se.plot(
                    kind='kde',
                    c=self.get_color(i),
                    lw=self._linewidth_selection,
                    label=df.index.name,
                    ax=self.axes
                )
        
        self.set_xlabel(self.get_axis_label('Eta'))
        self.set_ylabel(r'$\mathrm{\mathsf{Density\ [a.u.]}}$')
        self.configure_ticks()
        
        self.axes.grid(self._grid_selection)
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))
        
        self.draw_legend(loc='upper left')
        self.canvas.draw()


class DistWTPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        param: str = 'Eta'
    ) -> None:
        self._param = param
        super().__init__(parent, data, title="Walkthrough")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        self.set_xlabel(r'$\mathrm{\mathsf{Normalized\ cell\ number\ [a.u.]}}$')
        self.set_ylabel(self.get_axis_label(self._param))
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                se = self._get_param_data(df, self._param)
                se.index = (se.index + 1) / len(se)
                self.axes.scatter(
                    se.index,
                    se,
                    c=self.get_color(i),
                    edgecolors='white',
                    linewidths=0.3,
                    s=self._dotsize_selection,
                    label=df.index.name
                )
        
        self.axes.set_xlim((0, 1))
        self.draw_legend(loc='lower left')
        self.canvas.draw()
    
    def _get_param_data(self, df: pd.DataFrame, param: str) -> pd.DataFrame:
        if param == 'Voc*Isc':
            return pd.DataFrame(df['Uoc'] * df['Isc'])
        elif param == 'RserLfDfIEC':
            return pd.DataFrame(1000 * df[param])
        elif param == 'Rsh':
            return pd.DataFrame(0.001 * df[param])
        else:
            return pd.DataFrame(df[param])


class DistRMPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        param: str = 'Eta'
    ) -> None:
        self._param = param
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        self._linewidth_selection = 3
        super().__init__(parent, data, title="Rolling mean")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        self.axes.grid(self._grid_selection)
        
        self.set_xlabel(r'$\mathrm{\mathsf{Normalized\ cell\ number\ [a.u.]}}$')
        self.set_ylabel(self.get_axis_label(self._param))
        self.configure_ticks()
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                se = self._get_param_data(df, self._param)
                se.index = (se.index + 1) / len(se)
                window = int(np.floor(len(se) * 0.1) if len(se) > 100 else 1)
                rm = se.rolling(center=True, window=window).mean()
                self.axes.plot(
                    rm.index,
                    rm,
                    c=self.get_color(i),
                    lw=self._linewidth_selection,
                    label=df.index.name
                )
        
        self.draw_legend(loc='lower left')
        self.canvas.draw()
    
    def _get_param_data(self, df: pd.DataFrame, param: str) -> pd.DataFrame:
        if param == 'Voc*Isc':
            return pd.DataFrame(df['Uoc'] * df['Isc'])
        elif param == 'RserLfDfIEC':
            return pd.DataFrame(1000 * df[param])
        elif param == 'Rsh':
            return pd.DataFrame(0.001 * df[param])
        else:
            return pd.DataFrame(df[param])


class IVBoxPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        param: str = 'Eta'
    ) -> None:
        self._param = param
        self._grid_enabled = False
        self._legend_enabled = False
        self._dotsize_enabled = False
        super().__init__(parent, data, title="Boxplot")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        
        self.set_ylabel(self.get_axis_label(self._param))
        self.configure_ticks()
        
        if len(self._plot_selection) == 0:
            self.canvas.draw()
            return
        
        data_list = []
        labels = []
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                data_list.append(self._get_param_data(df, self._param))
                labels.append(df.index.name)
        
        if data_list:
            bp = self.axes.boxplot(data_list, 0, '')
            self.axes.set_xticks([y + 1 for y in range(len(labels))])
            self.axes.set_xticklabels(labels, rotation=0)
            plt.setp(bp['boxes'], color='black', lw=2)
            plt.setp(bp['whiskers'], color='black', lw=2, ls='-')
            plt.setp(bp['caps'], color='black', lw=2)
        
        self.canvas.draw()
    
    def _get_param_data(self, df: pd.DataFrame, param: str) -> pd.Series:
        if param == 'Voc*Isc':
            return df['Uoc'] * df['Isc']
        elif param == 'RserLfDfIEC':
            return 1000 * df[param]
        elif param == 'Rsh':
            return 0.001 * df[param]
        else:
            return df[param]


class ViolinPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        param: str = 'Eta'
    ) -> None:
        self._param = param
        self._grid_enabled = False
        self._legend_enabled = False
        self._dotsize_enabled = False
        super().__init__(parent, data, title="Violinplot")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        
        self.set_ylabel(self.get_axis_label(self._param))
        self.configure_ticks()
        
        if len(self._plot_selection) == 0:
            self.canvas.draw()
            return
        
        data_list = []
        labels = []
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                data_list.append(self._get_param_data(df, self._param))
                labels.append(df.index.name)
        
        if data_list:
            self.axes.violinplot(data_list, showmeans=False, showmedians=True)
            self.axes.set_xticks([y + 1 for y in range(len(labels))])
            self.axes.set_xticklabels(labels, rotation=0)
        
        self.canvas.draw()
    
    def _get_param_data(self, df: pd.DataFrame, param: str) -> pd.Series:
        if param == 'Voc*Isc':
            return df['Uoc'] * df['Isc']
        elif param == 'RserLfDfIEC':
            return 1000 * df[param]
        elif param == 'Rsh':
            return 0.001 * df[param]
        else:
            return df[param]


class CategoryScatterPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None,
        param: str = 'Eta'
    ) -> None:
        self._param = param
        self._grid_enabled = False
        self._legend_enabled = False
        self._dotsize_enabled = True
        self._dotsize_selection = 20
        self._scatter_enabled = True
        self._scatter_selection = 0.5
        super().__init__(parent, data, title="Category scatter")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        
        self.set_ylabel(self.get_axis_label(self._param))
        self.configure_ticks()
        
        if len(self._plot_selection) == 0:
            self.canvas.draw()
            return
        
        scatter = self._scatter_selection
        xticks = []
        xticklabels = []
        
        for i in self._plot_selection:
            if i in self._data:
                df = self._data[i]
                n = len(df['Uoc'])
                xvalues = scatter * np.random.uniform(size=n) - scatter * 0.5 + i
                
                data = self._get_param_data(df, self._param)
                
                self.axes.scatter(
                    [xvalues],
                    [data.values.flatten().tolist()],
                    c=self.get_color(i),
                    edgecolors='white',
                    s=self._dotsize_selection
                )
                
                xticks.append(i)
                xticklabels.append(df.index.name)
        
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels)
        
        self.canvas.draw()
    
    def _get_param_data(self, df: pd.DataFrame, param: str) -> pd.DataFrame:
        if param == 'Voc*Isc':
            return pd.DataFrame(df['Uoc'] * df['Isc'])
        elif param == 'RserLfDfIEC':
            return pd.DataFrame(1000 * df[param])
        elif param == 'Rsh':
            return pd.DataFrame(0.001 * df[param])
        else:
            return pd.DataFrame(df[param])


class IVHistPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._single_dataset = True
        self._title_enabled = True
        self._grid_enabled = False
        self._legend_enabled = False
        self._dotsize_enabled = False
        self._plot_selection = [0]
        super().__init__(parent, data, title="Histogram")
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        
        xmin = 1e4
        xmax = 0
        
        for i in self._data:
            ser = self._data[i]['Eta']
            if ser.min() <= xmin:
                xmin = ser.min()
            if ser.max() >= xmax:
                xmax = ser.max()
        
        if self._plot_selection and self._plot_selection[0] in self._data:
            df = self._data[self._plot_selection[0]]
            se = df['Eta'].round(1)
            freq = se.value_counts()
            freq = 100 * freq / len(se)
            freq = freq.sort_index()
            self.axes.bar(
                freq.index,
                freq.values,
                0.1,
                color=self.get_color(self._plot_selection[0]),
                align='center',
                edgecolor='0'
            )
            
            if self._title_selection:
                self.axes.set_title(df.index.name)
        
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))
        self.set_xlabel(self.get_axis_label('Eta'))
        self.set_ylabel(r'$\mathrm{\mathsf{Frequency\ [\%]}}$')
        self.configure_ticks()
        self.axes.grid(False)
        
        self.canvas.draw()


class IVHistDenPlot(BasePlotWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        data: Optional[Dict[int, pd.DataFrame]] = None
    ) -> None:
        self._single_dataset = True
        self._title_enabled = True
        self._grid_enabled = False
        self._legend_enabled = False
        self._dotsize_enabled = False
        self._linewidth_enabled = True
        self._linewidth_selection = 3
        self._plot_selection = [0]
        super().__init__(parent, data, title="Histogram and density")
        self._create_main_frame(two_axes=True)
        self.on_draw()
    
    def on_draw(self) -> None:
        self.axes.clear()
        if hasattr(self, 'axes2'):
            self.axes2.clear()
        
        xmin = 1e4
        xmax = 0
        
        for i in self._data:
            ser = self._data[i]['Eta']
            if ser.min() <= xmin:
                xmin = ser.min()
            if ser.max() >= xmax:
                xmax = ser.max()
        
        if self._plot_selection and self._plot_selection[0] in self._data:
            df = self._data[self._plot_selection[0]]
            den = df['Eta']
            bn = df['Eta'].round(1)
            freq = bn.value_counts()
            freq = 100 * freq / len(bn)
            freq = freq.sort_index()
            self.axes.bar(
                freq.index,
                freq.values,
                0.1,
                color=self.get_color(self._plot_selection[0]),
                align='center',
                edgecolor='0'
            )
            
            if hasattr(self, 'axes2'):
                den.plot(kind='kde', c='white', lw=self._linewidth_selection + 3, ax=self.axes2)
                den.plot(kind='kde', c='black', lw=self._linewidth_selection + 1, ax=self.axes2)
                den.plot(kind='kde', c='r', lw=self._linewidth_selection, ax=self.axes2)
            
            if self._title_selection:
                self.axes.set_title(df.index.name)
        
        self.axes.set_xlim((np.floor(xmin), np.ceil(xmax)))
        if hasattr(self, 'axes2'):
            self.axes2.set_xlim((np.floor(xmin), np.ceil(xmax)))
        
        self.set_xlabel(self.get_axis_label('Eta'))
        self.axes.set_ylabel(r'$\mathrm{\mathsf{Frequency\ [\%]}}$')
        if hasattr(self, 'axes2'):
            self.axes2.set_ylabel(r'$\mathrm{\mathsf{Density\ [a.u.]}}$')
        self.configure_ticks()
        if hasattr(self, 'axes2'):
            self.axes2.tick_params(pad=self._tick_pad)
        self.axes.grid(False)
        if hasattr(self, 'axes2'):
            self.axes2.grid(False)
        
        self.canvas.draw()
