# -*- coding: utf-8 -*-
"""
Views package for SCiDA Pro
Contains PyQt5 UI components and plot widgets
"""

from .base_plot_widget import BasePlotWidget
from .plot_settings_dialog import PlotSettingsDialog
from .main_window import MainWindow
from .help_dialog import HelpDialog
from .correlation_plots import CorrVocIsc, CorrEtaFF, CorrRshFF
from .distribution_plots import DistLtoH, DensEta, DistWT, DistRM
from .statistical_plots import IVBoxPlot, ViolinPlot, IVHistPlot, IVHistDenPlot
from .category_plots import CategoryScatter

__all__ = [
    'BasePlotWidget',
    'PlotSettingsDialog',
    'MainWindow',
    'HelpDialog',
    'CorrVocIsc',
    'CorrEtaFF',
    'CorrRshFF',
    'DistLtoH',
    'DensEta',
    'DistWT',
    'DistRM',
    'IVBoxPlot',
    'ViolinPlot',
    'IVHistPlot',
    'IVHistDenPlot',
    'CategoryScatter'
]
