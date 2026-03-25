# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Tuple
import os
import subprocess
import platform
import pandas as pd
from PyQt5 import QtWidgets

from models import DataModel, ReportModel
from utils import get_config, get_logger, is_valid_filename


class ReportController:
    def __init__(
        self,
        data_model: Optional[DataModel] = None,
        report_model: Optional[ReportModel] = None
    ) -> None:
        self._data_model = data_model or DataModel()
        self._report_model = report_model or ReportModel()
        self._config = get_config()
        self._logger = get_logger()
        self._report_path: str = ""
        self._prev_dir_path: str = ""
    
    @property
    def report_path(self) -> str:
        return self._report_path
    
    @report_path.setter
    def report_path(self, value: str) -> None:
        self._report_path = value
    
    @property
    def prev_dir_path(self) -> str:
        return self._prev_dir_path
    
    @prev_dir_path.setter
    def prev_dir_path(self, value: str) -> None:
        self._prev_dir_path = value
    
    def generate_report(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        yield_loss: Optional[List[pd.DataFrame]] = None
    ) -> Tuple[bool, str]:
        if not self._data_model.data:
            return False, "No data to report"
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent,
            "Save file",
            self._prev_dir_path,
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return False, "No file selected"
        
        if not is_valid_filename(file_path):
            return False, "Non-ASCII filename"
        
        self._report_path = file_path
        self._prev_dir_path = os.path.dirname(file_path)
        
        summaries = self._report_model.generate_summaries(self._data_model.data)
        correlations = self._report_model.generate_correlations(self._data_model.data)
        
        yield_loss_output = None
        if yield_loss:
            yield_loss_output = self._report_model.generate_yield_loss_output(
                yield_loss,
                self._data_model.data
            )
        
        success, error = self._report_model.export_to_excel(
            file_path,
            summaries=summaries,
            yield_loss=yield_loss_output,
            correlations=correlations
        )
        
        return success, error if not success else "Report generated"
    
    def open_report(self) -> Tuple[bool, str]:
        if not self._report_path or not os.path.exists(self._report_path):
            return False, "No report file found"
        
        try:
            if platform.system() == 'Windows':
                os.startfile(self._report_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', self._report_path])
            else:
                subprocess.run(['xdg-open', self._report_path])
            return True, "Report opened"
        except Exception as e:
            self._logger.error(f"Failed to open report: {e}")
            return False, str(e)
