# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict, List, Optional, Tuple
import os
import ntpath
import pandas as pd
from PyQt5 import QtWidgets

from models import DataModel
from utils import get_config, get_logger, is_valid_filename


class DataController:
    def __init__(self, data_model: Optional[DataModel] = None) -> None:
        self._model = data_model or DataModel()
        self._config = get_config()
        self._logger = get_logger()
        self._prev_dir_path: str = ""
    
    @property
    def model(self) -> DataModel:
        return self._model
    
    @property
    def data(self) -> Dict[int, pd.DataFrame]:
        return self._model.data
    
    @property
    def prev_dir_path(self) -> str:
        return self._prev_dir_path
    
    @prev_dir_path.setter
    def prev_dir_path(self, value: str) -> None:
        self._prev_dir_path = value
    
    def load_files(
        self,
        parent: Optional[QtWidgets.QWidget] = None
    ) -> Tuple[Dict[int, pd.DataFrame], List[str], List[str], List[str]]:
        file_dialog = QtWidgets.QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            parent,
            "Load files",
            self._prev_dir_path,
            "Excel Files (*.csv *.xls *.xlsx)"
        )
        
        if not file_paths:
            return {}, [], [], []
        
        self._prev_dir_path = ntpath.dirname(file_paths[0])
        
        loaded_data, empty_warnings, non_ascii_warnings, read_error_warnings = \
            self._model.load_files(file_paths)
        
        return loaded_data, empty_warnings, non_ascii_warnings, read_error_warnings
    
    def save_files(
        self,
        parent: Optional[QtWidgets.QWidget] = None
    ) -> Tuple[bool, str]:
        if not self._model.data:
            return False, "No data to save"
        
        dest_dir = QtWidgets.QFileDialog.getExistingDirectory(
            parent,
            'Open directory',
            self._prev_dir_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if not dest_dir:
            return False, "No directory selected"
        
        self._prev_dir_path = dest_dir
        yes_to_all = False
        
        for idx, df in self._model.data.items():
            filename = df.index.name + '.csv'
            save_path = os.path.join(dest_dir, filename)
            
            if os.path.isfile(save_path) and not yes_to_all:
                reply = QtWidgets.QMessageBox.question(
                    parent,
                    "Message",
                    f"Overwrite '{filename}'?",
                    QtWidgets.QMessageBox.YesToAll | QtWidgets.QMessageBox.Yes |
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
                    QtWidgets.QMessageBox.No
                )
                
                if reply == QtWidgets.QMessageBox.No:
                    new_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                        parent,
                        "Save file",
                        dest_dir,
                        "CSV File (*.csv)"
                    )
                    if not new_path:
                        continue
                    save_path = new_path
                
                if reply == QtWidgets.QMessageBox.YesToAll:
                    yes_to_all = True
                
                if reply == QtWidgets.QMessageBox.Cancel:
                    return False, "Cancelled"
            
            df.to_csv(save_path, index=False)
        
        return True, "Files saved"
    
    def combine_datasets(self) -> Tuple[bool, str]:
        if len(self._model.data) <= 1:
            return False, "Need at least 2 datasets to combine"
        
        success = self._model.combine_datasets()
        if success:
            return True, "Datasets combined"
        return False, "Failed to combine datasets"
    
    def clear_data(self) -> None:
        self._model.clear_data()
    
    def rename_dataset(self, index: int, new_name: str) -> Tuple[bool, str]:
        return self._model.rename_dataset(index, new_name)
    
    def set_label_format(self, format_index: int) -> None:
        self._model.label_format = format_index
    
    def load_custom_labels(
        self,
        parent: Optional[QtWidgets.QWidget] = None
    ) -> Tuple[bool, str]:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent,
            "Open file",
            self._prev_dir_path,
            "Label Settings File (*.csv)"
        )
        
        if not file_path:
            return False, "No file selected"
        
        if not is_valid_filename(file_path):
            return False, "Non-ASCII filename"
        
        self._prev_dir_path = ntpath.dirname(file_path)
        return self._model.load_custom_labels(file_path)
    
    def get_dataset_names(self) -> List[str]:
        return self._model.get_dataset_names()
    
    def get_dataset_count(self) -> int:
        return self._model.get_dataset_count()
    
    def has_data(self) -> bool:
        return self._model.get_dataset_count() > 0
