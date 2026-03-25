# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import pickle
from utils import get_config, get_logger, is_number, remove_whitespace


class FilterModel:
    def __init__(self) -> None:
        self._config = get_config()
        self._logger = get_logger()
        
        self._default_filters: List[List] = self._config.default_filters
        self._user_filters: List[List] = []
        self._user_filters_plain: List[List] = []
        self._yield_loss: List[pd.DataFrame] = []
        
        self._valid_parameters = self._config.get('filters.valid_parameters', 
            ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1'])
        self._valid_operators = self._config.get('filters.valid_operators', ['<', '>'])
        self._max_filter_rows = self._config.get('filters.max_rows', 12)
    
    @property
    def default_filters(self) -> List[List]:
        return self._default_filters.copy()
    
    @property
    def user_filters(self) -> List[List]:
        return self._user_filters.copy()
    
    @property
    def user_filters_plain(self) -> List[List]:
        return self._user_filters_plain.copy()
    
    @property
    def yield_loss(self) -> List[pd.DataFrame]:
        return self._yield_loss
    
    @property
    def valid_parameters(self) -> List[str]:
        return self._valid_parameters.copy()
    
    @property
    def valid_operators(self) -> List[str]:
        return self._valid_operators.copy()
    
    @property
    def max_filter_rows(self) -> int:
        return self._max_filter_rows
    
    def parse_filter_table(self, table_data: List[List[str]]) -> List[List]:
        self._user_filters = []
        
        for row in table_data[:self._max_filter_rows]:
            if len(row) >= 3 and row[0] and row[1] and row[2]:
                param = remove_whitespace(str(row[0]))
                operator = remove_whitespace(str(row[1]))
                value = remove_whitespace(str(row[2]))
                
                if param in self._valid_parameters:
                    if operator in self._valid_operators:
                        if is_number(value):
                            self._user_filters.append([param, operator, value])
        
        return self._user_filters.copy()
    
    def convert_to_plain_format(self) -> List[List]:
        self._user_filters_plain = []
        
        for filter_item in self._user_filters:
            plain_filter = [
                str(filter_item[0]),
                str(filter_item[1])
            ]
            
            value = float(filter_item[2])
            if value % 1 == 0:
                plain_filter.append(int(value))
            else:
                plain_filter.append(value)
            
            self._user_filters_plain.append(plain_filter)
        
        return self._user_filters_plain.copy()
    
    def apply_filters(
        self,
        data: Dict[int, pd.DataFrame]
    ) -> Tuple[Dict[int, pd.DataFrame], List[pd.DataFrame]]:
        self._yield_loss = []
        
        yl_columns = [f'Filter {i+1}' for i in range(12)]
        yl_index = ['Filter', 'Loss count']
        
        for idx, df in data.items():
            yl_df = pd.DataFrame(index=yl_index, columns=yl_columns)
            yl_df.index.name = str(len(df))
            
            for i, filter_item in enumerate(self._user_filters[:12]):
                param, operator, value = filter_item
                yl_df.iloc[0, i] = f"{param}{operator}{value}"
                
                try:
                    threshold = float(value)
                    if operator == '>':
                        yl_df.iloc[1, i] = (df[param] > threshold).sum()
                        df = df[df[param] <= threshold]
                    elif operator == '<':
                        yl_df.iloc[1, i] = (df[param] < threshold).sum()
                        df = df[df[param] >= threshold]
                except Exception as e:
                    self._logger.error(f"Error applying filter: {e}")
            
            name = df.index.name
            df = df.reset_index(drop=True)
            df.index.name = name
            
            if len(df) == 0:
                df.loc[0] = [-1, -1, -1, -1, -1, -1, -1]
            
            data[idx] = df
            self._yield_loss.append(yl_df)
        
        return data, self._yield_loss
    
    def save_filters(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self._user_filters_plain, f)
            return True, ""
        except Exception as e:
            self._logger.error(f"Failed to save filters: {e}")
            return False, str(e)
    
    def load_filters(self, filepath: str) -> Tuple[bool, str]:
        try:
            with open(filepath, 'rb') as f:
                self._user_filters_plain = pickle.load(f)
            return True, ""
        except Exception as e:
            self._logger.error(f"Failed to load filters: {e}")
            return False, str(e)
    
    def reset_to_default(self) -> List[List]:
        self._user_filters = []
        self._user_filters_plain = []
        return self._default_filters.copy()
    
    def get_filter_table_data(self, use_user_filters: bool = False) -> List[List[str]]:
        if use_user_filters and self._user_filters_plain:
            return [[str(item) for item in row] for row in self._user_filters_plain]
        return [[str(item) for item in row] for row in self._default_filters]
