# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from PyQt5 import QtWidgets

from models import FilterModel
from utils import get_config, get_logger


class FilterController:
    def __init__(self, filter_model: Optional[FilterModel] = None) -> None:
        self._model = filter_model or FilterModel()
        self._config = get_config()
        self._logger = get_logger()
    
    @property
    def model(self) -> FilterModel:
        return self._model
    
    @property
    def default_filters(self) -> List[List]:
        return self._model.default_filters
    
    @property
    def user_filters(self) -> List[List]:
        return self._model.user_filters
    
    @property
    def valid_parameters(self) -> List[str]:
        return self._model.valid_parameters
    
    @property
    def max_filter_rows(self) -> int:
        return self._model.max_filter_rows
    
    def parse_filter_table(self, table_data: List[List[str]]) -> List[List]:
        return self._model.parse_filter_table(table_data)
    
    def apply_filters(
        self,
        data: Dict[int, pd.DataFrame]
    ) -> Tuple[Dict[int, pd.DataFrame], List[pd.DataFrame]]:
        return self._model.apply_filters(data)
    
    def save_filters(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        prev_dir: str = ""
    ) -> Tuple[bool, str, str]:
        self._model.convert_to_plain_format()
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent,
            "Save file",
            prev_dir,
            "Description Files (*.scda)"
        )
        
        if not file_path:
            return False, "", "No file selected"
        
        success, error = self._model.save_filters(file_path)
        return success, file_path, error
    
    def load_filters(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        prev_dir: str = ""
    ) -> Tuple[bool, str, str]:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent,
            "Open file",
            prev_dir,
            "Filter Settings Files (*.scda)"
        )
        
        if not file_path:
            return False, "", "No file selected"
        
        success, error = self._model.load_filters(file_path)
        return success, file_path, error
    
    def reset_to_default(self) -> List[List]:
        return self._model.reset_to_default()
    
    def get_filter_table_data(self, use_user_filters: bool = False) -> List[List[str]]:
        return self._model.get_filter_table_data(use_user_filters)
    
    def get_yield_loss(self) -> List[pd.DataFrame]:
        return self._model.yield_loss
