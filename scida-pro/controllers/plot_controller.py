# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict, List, Optional, Tuple
import pandas as pd
from PyQt5 import QtWidgets

from models import DataModel
from views import (
    CorrVocIscPlot,
    CorrEtaFFPlot,
    CorrRshFFPlot,
    DistLtoHPlot,
    DensEtaPlot,
    DistWTPlot,
    DistRMPlot,
    IVBoxPlot,
    IVHistPlot,
    IVHistDenPlot,
    ViolinPlot,
    CategoryScatterPlot
)
from utils import get_config, get_logger


class PlotController:
    def __init__(self) -> None:
        self._config = get_config()
        self._logger = get_logger()
        self._current_plot_window: Optional[QtWidgets.QMainWindow] = None
        
        self._plot_selection_list = [
            'Uoc', 'Isc', 'Voc*Isc', 'FF', 'Eta',
            'RserLfDfIEC', 'Rsh', 'IRev1'
        ]
        
        self._plot_type_list = [
            'Boxplot', 'Violinplot', 'Category scatter',
            'Walk-through', 'Rolling mean', 'Low to high',
            'Histogram', 'Density', 'Histogram + density',
            'Voc-Isc', 'Eta-FF', 'Rsh-FF'
        ]
    
    @property
    def plot_selection_list(self) -> List[str]:
        return self._plot_selection_list.copy()
    
    @property
    def plot_type_list(self) -> List[str]:
        return self._plot_type_list.copy()
    
    @property
    def current_plot_window(self) -> Optional[QtWidgets.QMainWindow]:
        return self._current_plot_window
    
    def close_current_plot(self) -> None:
        if self._current_plot_window and self._current_plot_window.isWindow():
            self._current_plot_window.close()
    
    def create_plot(
        self,
        parent: QtWidgets.QWidget,
        data: Dict[int, pd.DataFrame],
        plot_type_index: int,
        param: str
    ) -> Optional[QtWidgets.QMainWindow]:
        self.close_current_plot()
        
        plot_classes = {
            0: lambda: IVBoxPlot(parent, data, param),
            1: lambda: ViolinPlot(parent, data, param),
            2: lambda: CategoryScatterPlot(parent, data, param),
            3: lambda: DistWTPlot(parent, data, param),
            4: lambda: DistRMPlot(parent, data, param),
            5: lambda: DistLtoHPlot(parent, data),
            6: lambda: IVHistPlot(parent, data),
            7: lambda: DensEtaPlot(parent, data),
            8: lambda: IVHistDenPlot(parent, data),
            9: lambda: CorrVocIscPlot(parent, data),
            10: lambda: CorrEtaFFPlot(parent, data),
            11: lambda: CorrRshFFPlot(parent, data),
        }
        
        if plot_type_index in plot_classes:
            self._current_plot_window = plot_classes[plot_type_index]()
            return self._current_plot_window
        
        return None
    
    def get_param_index(self, param: str) -> int:
        try:
            return self._plot_selection_list.index(param)
        except ValueError:
            return 4
    
    def should_enable_param_combo(self, plot_type_index: int) -> Tuple[bool, int]:
        if plot_type_index < 3:
            return True, -1
        elif 3 <= plot_type_index < 7:
            return False, 4
        else:
            return False, -1
