# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import os
import ntpath
from utils import get_config, get_logger, is_valid_filename, sanitize_filename


class DataModel:
    def __init__(self) -> None:
        self._data: Dict[int, pd.DataFrame] = {}
        self._label_format: int = 0
        self._config = get_config()
        self._logger = get_logger()
        
        self._label_formats: Dict[int, List[str]] = {}
        self._init_label_formats()
    
    def _init_label_formats(self) -> None:
        formats = self._config.get('data_labels.formats', {})
        for i, (key, value) in enumerate(formats.items()):
            self._label_formats[i] = value.get('labels', [])
        
        if not self._label_formats:
            self._label_formats = {
                0: ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1'],
                1: ['Uoc0', 'Isc0', 'Rseries_multi_level', 'Rshunt_SC', 'Fill0', 'Eff0', 'Ireverse_2'],
                2: ['Uoc', 'Isc', 'RserIEC891', 'RshuntDfDr', 'FF', 'Eta', 'IRev1'],
                3: ['Uoc', 'Isc', 'Rs', 'Rsh', 'FF', 'NCell', 'Irev2'],
                4: ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
            }
    
    @property
    def data(self) -> Dict[int, pd.DataFrame]:
        return self._data
    
    @property
    def label_format(self) -> int:
        return self._label_format
    
    @label_format.setter
    def label_format(self, value: int) -> None:
        self._label_format = value
    
    @property
    def internal_labels(self) -> List[str]:
        return self._config.internal_labels
    
    def get_label_format_name(self, format_index: Optional[int] = None) -> str:
        if format_index is None:
            format_index = self._label_format
        
        format_names = {
            0: "Data label set A",
            1: "Data label set B",
            2: "Data label set C",
            3: "Data label set D",
            4: "Custom label set"
        }
        return format_names.get(format_index, "Data label set A")
    
    def load_custom_labels(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, 'rb') as f:
                first_line = f.readline()
            first_line = first_line.decode('utf-8')
            first_line = ''.join(first_line.split())
            self._label_formats[4] = first_line.split(',')
            self._label_format = 4
            return True, str(self._label_formats[4])
        except Exception as e:
            self._logger.error(f"Failed to load custom labels: {e}")
            return False, str(e)
    
    def load_files(
        self,
        filepaths: List[str]
    ) -> Tuple[Dict[int, pd.DataFrame], List[str], List[str], List[str]]:
        empty_warnings = []
        non_ascii_warnings = []
        read_error_warnings = []
        loaded_data = {}
        start_index = len(self._data)
        
        for filepath in filepaths:
            if not is_valid_filename(filepath):
                non_ascii_warnings.append(filepath)
                continue
            
            try:
                df = self._read_file(filepath)
                if df is None:
                    read_error_warnings.append(filepath)
                    continue
                
                df = self._process_dataframe(df)
                
                if df.empty:
                    empty_warnings.append(filepath)
                    continue
                
                index = start_index + len(loaded_data)
                name = self._get_dataset_name(filepath)
                df.index.name = name
                loaded_data[index] = df
                self._logger.info(f"Loaded dataset '{name}' with {len(df)} rows")
                
            except Exception as e:
                self._logger.error(f"Error loading file {filepath}: {e}")
                read_error_warnings.append(filepath)
        
        self._data.update(loaded_data)
        self._logger.info(f"Total datasets loaded: {len(loaded_data)}, Total in memory: {len(self._data)}")
        return loaded_data, empty_warnings, non_ascii_warnings, read_error_warnings
    
    def _read_file(self, filepath: str) -> Optional[pd.DataFrame]:
        _, ext = ntpath.splitext(filepath)
        
        try:
            if ext.lower() == '.csv':
                try:
                    df = pd.read_csv(filepath)[self._label_formats[self._label_format]].dropna()
                except KeyError:
                    try:
                        df = pd.read_csv(filepath, sep=';')[self._label_formats[self._label_format]].dropna()
                    except KeyError:
                        return None
            else:
                df = pd.read_excel(filepath)[self._label_formats[self._label_format]].dropna()
            
            df.columns = self._label_formats[0]
            return df
        except Exception:
            return None
    
    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.apply(pd.to_numeric)
        df = df[df > 0]
        
        if self._label_format == 1:
            if 'Eta' in df.columns:
                df['Eta'] = df['Eta'] * 100
            if 'FF' in df.columns:
                df['FF'] = df['FF'] * 100
        elif self._label_format == 3:
            if 'Eta' in df.columns:
                df['Eta'] = df['Eta'] * 100
        
        return df
    
    def _get_dataset_name(self, filepath: str) -> str:
        name = ntpath.splitext(ntpath.basename(filepath))[0]
        return sanitize_filename(name, max_length=39)
    
    def rename_dataset(self, index: int, new_name: str) -> Tuple[bool, str]:
        if index not in self._data:
            return False, "Dataset not found"
        
        sanitized = sanitize_filename(new_name, max_length=39)
        if len(sanitized) > 0:
            self._data[index].index.name = sanitized
            return True, sanitized
        return False, "Invalid name"
    
    def combine_datasets(self) -> bool:
        if len(self._data) <= 1:
            return False
        
        combined = pd.concat(list(self._data.values()), ignore_index=True)
        combined.index.name = 'Combined data set'
        
        self._data.clear()
        self._data[0] = combined
        return True
    
    def clear_data(self) -> None:
        self._data.clear()
    
    def get_dataset_count(self) -> int:
        return len(self._data)
    
    def get_dataset_names(self) -> List[str]:
        return [df.index.name for df in self._data.values()]
    
    def get_dataset(self, index: int) -> Optional[pd.DataFrame]:
        return self._data.get(index)
