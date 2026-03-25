# -*- coding: utf-8 -*-
"""
IV Data Model for SCiDA Pro
Represents solar cell IV measurement data
"""

import os
import ntpath
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from utils import (
    ConfigManager,
    sanitize_filename,
    is_valid_ascii_filename,
    get_file_extension
)


class IVDataModel:
    """
    Data model for IV measurement data
    Manages loading, storing, and processing of solar cell measurement data
    """
    
    # Column names for internal data storage
    _columns = ['Uoc', 'Isc', 'RserLfDfIEC', 'Rsh', 'FF', 'Eta', 'IRev1']
    
    def __init__(self, name: str = "", data: Optional[pd.DataFrame] = None):
        """
        Initialize IV Data Model
        Args:
            name: Name of the dataset
            data: Optional DataFrame containing the measurement data
        """
        self._name = name
        self._data = pd.DataFrame(columns=self._columns)
        self._original_count = 0
        
        if data is not None:
            self.set_data(data)
    
    @property
    def name(self) -> str:
        """Get dataset name"""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set dataset name"""
        self._name = sanitize_filename(value)
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the underlying DataFrame"""
        return self._data
    
    @property
    def original_count(self) -> int:
        """Get original cell count before filtering"""
        return self._original_count
    
    @property
    def count(self) -> int:
        """Get current cell count"""
        return len(self._data)
    
    def set_data(self, data: pd.DataFrame, 
                 reset_original_count: bool = True) -> None:
        """
        Set data from DataFrame
        Ensures data contains only numeric values and no NaNs
        """
        # Ensure we have the correct columns
        result = pd.DataFrame(columns=self._columns)
        
        for col in self._columns:
            if col in data.columns:
                result[col] = pd.to_numeric(data[col], errors='coerce')
            else:
                result[col] = np.nan
        
        # Drop rows with any NaN values
        result = result.dropna()
        
        # Only keep positive values (as per original code)
        result = result[result > 0].dropna()
        
        self._data = result.reset_index(drop=True)
        
        if reset_original_count:
            self._original_count = len(self._data)
    
    def is_empty(self) -> bool:
        """Check if dataset is empty"""
        return len(self._data) == 0
    
    def apply_label_format_conversion(self, label_format: int) -> None:
        """
        Apply unit conversions based on label format
        Some data sources use different unit scales
        """
        if label_format == 1:
            # Convert from decimal to percentage for Eta and FF
            if 'Eta' in self._data.columns:
                self._data.loc[:, 'Eta'] *= 100
            if 'FF' in self._data.columns:
                self._data.loc[:, 'FF'] *= 100
        elif label_format == 3:
            # Convert from decimal to percentage for Eta
            if 'Eta' in self._data.columns:
                self._data.loc[:, 'Eta'] *= 100
    
    def apply_filter(self, column: str, operator: str, value: float) -> int:
        """
        Apply a filter to the data
        Returns number of cells removed
        """
        before_count = len(self._data)
        
        if column not in self._data.columns:
            return 0
        
        if operator == '>':
            # Keep cells where value <= threshold
            self._data = self._data[self._data[column] <= value]
        elif operator == '<':
            # Keep cells where value >= threshold
            self._data = self._data[self._data[column] >= value]
        
        self._data = self._data.reset_index(drop=True)
        return before_count - len(self._data)
    
    def combine_with(self, other: 'IVDataModel') -> None:
        """Combine this dataset with another dataset"""
        if other.is_empty():
            return
        
        combined = pd.concat([self._data, other.data], ignore_index=True)
        self._data = combined
        self._original_count = len(self._data)
    
    def get_statistics(self) -> pd.DataFrame:
        """Calculate statistics for this dataset"""
        from utils import calculate_statistics
        stats = calculate_statistics(self._data)
        stats.index.name = 'Data property'
        return stats
    
    def get_correlation(self) -> pd.DataFrame:
        """Calculate correlation matrix for this dataset"""
        from utils import calculate_correlation
        corr = calculate_correlation(self._data)
        corr.index.name = 'Data property'
        return corr
    
    def get_column(self, column: str) -> pd.Series:
        """Get a single column of data"""
        if column == 'Voc*Isc':
            return self._data['Uoc'] * self._data['Isc']
        elif column == 'RserLfDfIEC':
            return self._data['RserLfDfIEC'] * 1000  # Convert to mOhm
        elif column == 'Rsh':
            return self._data['Rsh'] * 0.001  # Convert to kOhm
        elif column in self._data.columns:
            return self._data[column]
        else:
            raise ValueError(f"Unknown column: {column}")
    
    @classmethod
    def from_file(cls, filename: str, 
                  label_formats: Dict[int, List[str]], 
                  selected_format: int = 0) -> Tuple[Optional['IVDataModel'], str]:
        """
        Load data from a file (CSV or Excel)
        Returns (IVDataModel or None, status message)
        """
        status = ""
        
        # Check for non-ASCII filenames
        if not is_valid_ascii_filename(filename):
            return None, "non_ascii"
        
        file_ext = get_file_extension(filename)
        
        try:
            # Read file based on extension
            if file_ext == '.csv':
                try:
                    df = pd.read_csv(filename)
                except Exception:
                    # Try with semicolon separator
                    df = pd.read_csv(filename, sep=';')
            elif file_ext in ['.xls', '.xlsx']:
                xl_file = pd.ExcelFile(filename)
                df = xl_file.parse(xl_file.sheet_names[0])
            else:
                return None, "read_error"
            
            # Get the appropriate labels for this format
            format_labels = label_formats.get(selected_format, label_formats[0])
            
            # Try to extract data using current label format
            # Rename columns to standard names
            rename_map = {}
            for std_col, fmt_col in zip(cls._columns, format_labels):
                if fmt_col in df.columns:
                    rename_map[fmt_col] = std_col
            
            if not rename_map:
                return None, "read_error"
            
            df = df.rename(columns=rename_map)
            
            # Extract name from filename
            base_name = ntpath.splitext(ntpath.basename(filename))[0]
            name = sanitize_filename(base_name, 40)
            
            dataset = cls(name)
            dataset.set_data(df)
            
            # Apply unit conversions based on format
            dataset.apply_label_format_conversion(selected_format)
            
            return dataset, "success"
            
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
            return None, "read_error"
    
    def to_csv(self, filename: str) -> bool:
        """Save data to CSV file"""
        try:
            self._data.to_csv(filename, index=False)
            return True
        except Exception:
            return False
