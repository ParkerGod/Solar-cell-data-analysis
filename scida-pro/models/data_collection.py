# -*- coding: utf-8 -*-
"""
Data Collection Model for SCiDA Pro
Manages a collection of IVDataModel objects
"""

from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from .iv_data_model import IVDataModel


class DataCollection:
    """
    Collection of IVDataModel objects
    Manages multiple datasets and their metadata
    """
    
    def __init__(self):
        """Initialize empty data collection"""
        self._datasets: Dict[int, IVDataModel] = {}
        self._next_id: int = 0
        self._yield_loss: Dict[int, pd.DataFrame] = {}
        self._label_format: int = 0
    
    def __len__(self) -> int:
        """Get number of datasets"""
        return len(self._datasets)
    
    def __getitem__(self, index: int) -> IVDataModel:
        """Get dataset by index"""
        return self._datasets[index]
    
    def __iter__(self) -> Iterator[IVDataModel]:
        """Iterate over datasets"""
        return iter(self._datasets.values())
    
    def items(self) -> Iterator[Tuple[int, IVDataModel]]:
        """Iterate over (id, dataset) pairs"""
        return iter(self._datasets.items())
    
    @property
    def label_format(self) -> int:
        """Get current label format"""
        return self._label_format
    
    @label_format.setter
    def label_format(self, value: int) -> None:
        """Set label format"""
        self._label_format = value
    
    @property
    def yield_loss(self) -> Dict[int, pd.DataFrame]:
        """Get yield loss data"""
        return self._yield_loss
    
    def get_dataset(self, dataset_id: int) -> Optional[IVDataModel]:
        """Get dataset by ID"""
        return self._datasets.get(dataset_id)
    
    def get_dataset_names(self) -> List[str]:
        """Get list of dataset names"""
        return [ds.name for ds in self._datasets.values()]
    
    def add_dataset(self, dataset: IVDataModel) -> int:
        """
        Add a dataset to the collection
        Returns the assigned dataset ID
        """
        dataset_id = self._next_id
        self._datasets[dataset_id] = dataset
        self._next_id += 1
        return dataset_id
    
    def remove_dataset(self, dataset_id: int) -> bool:
        """Remove a dataset from the collection"""
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            if dataset_id in self._yield_loss:
                del self._yield_loss[dataset_id]
            return True
        return False
    
    def rename_dataset(self, dataset_id: int, new_name: str) -> bool:
        """Rename a dataset"""
        if dataset_id in self._datasets:
            self._datasets[dataset_id].name = new_name
            return True
        return False
    
    def clear(self) -> None:
        """Clear all datasets"""
        self._datasets.clear()
        self._yield_loss.clear()
        self._next_id = 0
    
    def is_empty(self) -> bool:
        """Check if collection is empty"""
        return len(self._datasets) == 0
    
    def combine_all(self) -> Optional[IVDataModel]:
        """
        Combine all datasets into one
        Returns the combined dataset or None if collection is empty
        """
        if self.is_empty():
            return None
        
        # Start with first dataset
        datasets = list(self._datasets.values())
        combined = IVDataModel(name="Combined data set")
        combined.set_data(datasets[0].data.copy())
        
        # Add remaining datasets
        for ds in datasets[1:]:
            combined.combine_with(ds)
        
        return combined
    
    def get_all_statistics(self) -> pd.DataFrame:
        """Get statistics for all datasets"""
        all_stats = []
        
        for ds_id, ds in self._datasets.items():
            stats = ds.get_statistics()
            stats['Data set'] = f"{ds.name} ({len(ds.data)} cells)"
            stats = stats.set_index('Data set', append=True).swaplevel(0, 1)
            all_stats.append(stats)
        
        if all_stats:
            return pd.concat(all_stats)
        return pd.DataFrame()
    
    def get_all_correlations(self) -> pd.DataFrame:
        """Get correlation matrices for all datasets"""
        all_corr = []
        
        for ds_id, ds in self._datasets.items():
            if len(ds.data) <= 1:
                continue
                
            corr = ds.get_correlation()
            if not corr.empty:
                corr['Data set'] = f"{ds.name} ({len(ds.data)} cells)"
                corr = corr.set_index('Data set', append=True).swaplevel(0, 1)
                all_corr.append(corr)
        
        if all_corr:
            return pd.concat(all_corr)
        return pd.DataFrame()
    
    def apply_filters(self, filters: List[Tuple[str, str, float]]) -> Dict[int, List[int]]:
        """
        Apply filters to all datasets
        Returns dictionary of yield loss counts per dataset and filter
        """
        yield_loss_counts: Dict[int, List[int]] = {}
        
        ylcolumns = [f'Filter {i+1}' for i in range(12)]
        ylindex = ['Filter', 'Loss count']
        
        for ds_id, ds in self._datasets.items():
            # Initialize yield loss DataFrame for this dataset
            yl = pd.DataFrame(index=ylindex, columns=ylcolumns)
            yl.index.name = ds.original_count  # Store original count in index name
            
            loss_counts: List[int] = []
            
            for i, (column, operator, value) in enumerate(filters):
                if i >= 12:  # Limit to 12 filters as in original code
                    break
                
                # Store filter information
                yl.iloc[0, i] = f"{column}{operator}{value}"
                
                # Apply filter and count loss
                loss_count = ds.apply_filter(column, operator, value)
                yl.iloc[1, i] = loss_count
                loss_counts.append(loss_count)
            
            self._yield_loss[ds_id] = yl
            yield_loss_counts[ds_id] = loss_counts
        
        return yield_loss_counts
    
    def get_yield_loss_summary(self) -> pd.DataFrame:
        """Get summarized yield loss data"""
        all_yl = []
        
        for ds_id, ds in self._datasets.items():
            if ds_id not in self._yield_loss:
                continue
            
            yl = self._yield_loss[ds_id].copy()
            
            # Add total column
            yl['Total'] = np.nan
            if not yl.empty and len(yl) > 1:
                yl.iloc[1, 12] = yl.iloc[1, :].sum()
            
            # Add percentage row
            yl.loc['Loss %'] = np.nan
            original_count = int(yl.index.name) if yl.index.name else 0
            
            if original_count > 0:
                for j in range(len(yl.columns)):
                    if pd.notna(yl.iloc[1, j]):
                        yl.iloc[2, j] = round(100 * yl.iloc[1, j] / original_count, 2)
            
            # Drop completely empty columns
            yl = yl.dropna(axis=1, how='all')
            
            # Format for output
            yl.index.name = 'Data property'
            yl['Data set'] = f"{ds.name} ({original_count} cells)"
            yl = yl.set_index('Data set', append=True).swaplevel(0, 1)
            
            all_yl.append(yl)
        
        if all_yl:
            return pd.concat(all_yl)
        return pd.DataFrame()
