# -*- coding: utf-8 -*-
"""
Unit tests for DataCollection
"""

import pytest
import pandas as pd
import numpy as np

from models import DataCollection, IVDataModel


class TestDataCollection:
    """Test cases for DataCollection"""
    
    def test_initialization(self):
        """Test basic initialization"""
        collection = DataCollection()
        assert collection.is_empty()
        assert len(collection) == 0
    
    def test_add_dataset(self):
        """Test adding datasets to collection"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        dataset = IVDataModel(name="test", data=data)
        dataset_id = collection.add_dataset(dataset)
        
        assert not collection.is_empty()
        assert len(collection) == 1
        assert collection.get_dataset(dataset_id) is dataset
    
    def test_remove_dataset(self):
        """Test removing datasets from collection"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62],
            'Isc': [8.0, 8.2],
            'RserLfDfIEC': [0.001, 0.0012],
            'Rsh': [1000.0, 1200.0],
            'FF': [75.0, 76.0],
            'Eta': [18.0, 18.5],
            'IRev1': [0.001, 0.0008]
        })
        
        dataset = IVDataModel(name="test", data=data)
        dataset_id = collection.add_dataset(dataset)
        
        # Remove existing dataset
        result = collection.remove_dataset(dataset_id)
        assert result
        assert collection.is_empty()
        assert len(collection) == 0
        
        # Remove non-existent dataset
        result = collection.remove_dataset(999)
        assert not result
    
    def test_iteration(self):
        """Test iterating over collection"""
        collection = DataCollection()
        
        # Add two datasets
        for i in range(2):
            data = pd.DataFrame({
                'Uoc': [0.6 + i*0.01, 0.62 + i*0.01],
                'Isc': [8.0 + i*0.1, 8.2 + i*0.1],
                'RserLfDfIEC': [0.001, 0.0012],
                'Rsh': [1000.0, 1200.0],
                'FF': [75.0, 76.0],
                'Eta': [18.0, 18.5],
                'IRev1': [0.001, 0.0008]
            })
            dataset = IVDataModel(name=f"dataset_{i}", data=data)
            collection.add_dataset(dataset)
        
        # Test iteration
        count = 0
        for dataset in collection:
            assert isinstance(dataset, IVDataModel)
            count += 1
        
        assert count == 2
    
    def test_combine_all(self):
        """Test combining all datasets"""
        collection = DataCollection()
        
        # Add two datasets
        for i in range(2):
            data = pd.DataFrame({
                'Uoc': [0.6, 0.62],
                'Isc': [8.0, 8.2],
                'RserLfDfIEC': [0.001, 0.0012],
                'Rsh': [1000.0, 1200.0],
                'FF': [75.0, 76.0],
                'Eta': [18.0, 18.5],
                'IRev1': [0.001, 0.0008]
            })
            dataset = IVDataModel(name=f"dataset_{i}", data=data)
            collection.add_dataset(dataset)
        
        combined = collection.combine_all()
        assert combined is not None
        assert combined.count == 4  # 2 rows per dataset * 2 datasets
    
    def test_rename_dataset(self):
        """Test renaming a dataset"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62],
            'Isc': [8.0, 8.2],
            'RserLfDfIEC': [0.001, 0.0012],
            'Rsh': [1000.0, 1200.0],
            'FF': [75.0, 76.0],
            'Eta': [18.0, 18.5],
            'IRev1': [0.001, 0.0008]
        })
        
        dataset = IVDataModel(name="original_name", data=data)
        dataset_id = collection.add_dataset(dataset)
        
        # Rename existing dataset
        result = collection.rename_dataset(dataset_id, "new_name")
        assert result
        assert collection.get_dataset(dataset_id).name == "new_name"
        
        # Rename non-existent dataset
        result = collection.rename_dataset(999, "should_fail")
        assert not result
    
    def test_get_dataset_names(self):
        """Test getting dataset names"""
        collection = DataCollection()
        
        names = ["dataset_1", "dataset_2", "dataset_3"]
        for name in names:
            data = pd.DataFrame({
                'Uoc': [0.6, 0.62],
                'Isc': [8.0, 8.2],
                'RserLfDfIEC': [0.001, 0.0012],
                'Rsh': [1000.0, 1200.0],
                'FF': [75.0, 76.0],
                'Eta': [18.0, 18.5],
                'IRev1': [0.001, 0.0008]
            })
            dataset = IVDataModel(name=name, data=data)
            collection.add_dataset(dataset)
        
        retrieved_names = collection.get_dataset_names()
        assert retrieved_names == names
    
    def test_clear(self):
        """Test clearing the collection"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62],
            'Isc': [8.0, 8.2],
            'RserLfDfIEC': [0.001, 0.0012],
            'Rsh': [1000.0, 1200.0],
            'FF': [75.0, 76.0],
            'Eta': [18.0, 18.5],
            'IRev1': [0.001, 0.0008]
        })
        
        dataset = IVDataModel(name="test", data=data)
        collection.add_dataset(dataset)
        
        collection.clear()
        assert collection.is_empty()
        assert len(collection) == 0
    
    def test_apply_filters(self):
        """Test applying filters to all datasets"""
        collection = DataCollection()
        
        # Add two datasets
        for i in range(2):
            data = pd.DataFrame({
                'Uoc': [0.6, 0.62, 0.58],
                'Isc': [8.0, 8.2, 7.8],
                'RserLfDfIEC': [0.001, 0.0012, 0.0009],
                'Rsh': [1000.0, 1200.0, 900.0],
                'FF': [75.0, 76.0, 74.0],
                'Eta': [18.0, 18.5, 17.5],
                'IRev1': [0.001, 0.0008, 0.0012]
            })
            dataset = IVDataModel(name=f"dataset_{i}", data=data)
            collection.add_dataset(dataset)
        
        # Apply filter: Eta > 18.0
        filters = [('Eta', '>', 18.0)]
        yield_loss = collection.apply_filters(filters)
        
        # Each dataset should have 1 row removed (Eta=18.5)
        for ds_id, losses in yield_loss.items():
            assert sum(losses) == 1  # One cell filtered out per dataset
    
    def test_get_all_statistics(self):
        """Test getting statistics for all datasets"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        dataset = IVDataModel(name="test", data=data)
        collection.add_dataset(dataset)
        
        stats = collection.get_all_statistics()
        assert not stats.empty
    
    def test_get_all_correlations(self):
        """Test getting correlations for all datasets"""
        collection = DataCollection()
        
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58, 0.61, 0.59],
            'Isc': [8.0, 8.2, 7.8, 8.1, 7.9],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009, 0.0011, 0.00095],
            'Rsh': [1000.0, 1200.0, 900.0, 1100.0, 950.0],
            'FF': [75.0, 76.0, 74.0, 75.5, 74.5],
            'Eta': [18.0, 18.5, 17.5, 18.2, 17.8],
            'IRev1': [0.001, 0.0008, 0.0012, 0.0009, 0.0011]
        })
        
        dataset = IVDataModel(name="test", data=data)
        collection.add_dataset(dataset)
        
        corr = collection.get_all_correlations()
        assert not corr.empty
