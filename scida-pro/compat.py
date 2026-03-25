# -*- coding: utf-8 -*-
"""
Backward compatibility module.
This module provides backward compatibility for the old import paths.
"""

from views import MainWindow as IVMainGui
from views import (
    BasePlotWidget,
    CorrVocIscPlot as CorrVocIsc,
    CorrEtaFFPlot as CorrEtaFF,
    CorrRshFFPlot as CorrRshFF,
    DistLtoHPlot as DistLtoH,
    DensEtaPlot as DensEta,
    DistWTPlot as DistWT,
    DistRMPlot as DistRM,
    IVBoxPlot,
    IVHistPlot,
    IVHistDenPlot,
    ViolinPlot,
    CategoryScatterPlot as CategoryScatter,
    HelpDialog,
    PlotSettingsDialog
)
from models import DataModel, FilterModel, ReportModel
from controllers import DataController, FilterController, PlotController, ReportController
from utils import (
    get_config,
    get_logger,
    is_number,
    remove_whitespace,
    is_valid_filename
)

__all__ = [
    'IVMainGui',
    'BasePlotWidget',
    'CorrVocIsc',
    'CorrEtaFF',
    'CorrRshFF',
    'DistLtoH',
    'DensEta',
    'DistWT',
    'DistRM',
    'IVBoxPlot',
    'IVHistPlot',
    'IVHistDenPlot',
    'ViolinPlot',
    'CategoryScatter',
    'HelpDialog',
    'PlotSettingsDialog',
    'DataModel',
    'FilterModel',
    'ReportModel',
    'DataController',
    'FilterController',
    'PlotController',
    'ReportController',
    'get_config',
    'get_logger',
    'is_number',
    'remove_whitespace',
    'is_valid_filename'
]
