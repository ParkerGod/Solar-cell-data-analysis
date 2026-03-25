# -*- coding: utf-8 -*-
"""
Unit tests for IVDataModel
"""

import pytest
import pandas as pd
import numpy as np

from models import IVDataModel
from utils import ConfigManager


class TestIVDataModel:
    """Test cases for IVDataModel"""
    
    def test_initialization(self):
        """Test basic initialization"""
        model = IVDataModel(name="test")
        assert model.name == "test"
        assert model.is_empty()
        assert model.count == 0
        assert model.original_count == 0
    
    def test_set_data_with_valid_dataframe(self):
        """Test setting data with valid DataFrame"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        assert not model.is_empty()
        assert model.count == 3
        assert model.original_count == 3
    
    def test_set_data_with_missing_columns(self):
        """Test setting data with missing columns should result in empty model"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62],
            'Isc': [8.0, 8.2]
            # Missing other columns
        })
        
        model = IVDataModel(name="test", data=data)
        assert model.is_empty()  # Should be empty due to NaN values
    
    def test_set_data_with_negative_values(self):
        """Test that negative values are filtered out"""
        data = pd.DataFrame({
            'Uoc': [0.6, -0.62, 0.58],  # One negative value
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        assert model.count == 2  # One row filtered due to negative value
    
    def test_apply_filter_greater_than(self):
        """Test applying > filter"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        initial_count = model.count
        
        # Filter out Eta > 18.0 (should remove one row)
        removed = model.apply_filter('Eta', '>', 18.0)
        assert removed == 1
        assert model.count == initial_count - 1
    
    def test_apply_filter_less_than(self):
        """Test applying < filter"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        initial_count = model.count
        
        # Filter out FF < 75.0 (should remove one row)
        removed = model.apply_filter('FF', '<', 75.0)
        assert removed == 1
        assert model.count == initial_count - 1
    
    def test_combine_with(self):
        """Test combining two datasets"""
        data1 = pd.DataFrame({
            'Uoc': [0.6, 0.62],
            'Isc': [8.0, 8.2],
            'RserLfDfIEC': [0.001, 0.0012],
            'Rsh': [1000.0, 1200.0],
            'FF': [75.0, 76.0],
            'Eta': [18.0, 18.5],
            'IRev1': [0.001, 0.0008]
        })
        
        data2 = pd.DataFrame({
            'Uoc': [0.58, 0.61],
            'Isc': [7.8, 8.1],
            'RserLfDfIEC': [0.0009, 0.0011],
            'Rsh': [900.0, 1100.0],
            'FF': [74.0, 75.5],
            'Eta': [17.5, 18.2],
            'IRev1': [0.0012, 0.0009]
        })
        
        model1 = IVDataModel(name="model1", data=data1)
        model2 = IVDataModel(name="model2", data=data2)
        
        model1.combine_with(model2)
        assert model1.count == 4
    
    def test_get_statistics(self):
        """Test statistics calculation"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        stats = model.get_statistics()
        
        assert not stats.empty
        assert 'Best cell' in stats.index
        assert 'Median' in stats.index
        assert 'Average' in stats.index
        assert 'Std.dev.' in stats.index
    
    def test_get_column(self):
        """Test getting column data"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58],
            'Isc': [8.0, 8.2, 7.8],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009],
            'Rsh': [1000.0, 1200.0, 900.0],
            'FF': [75.0, 76.0, 74.0],
            'Eta': [18.0, 18.5, 17.5],
            'IRev1': [0.001, 0.0008, 0.0012]
        })
        
        model = IVDataModel(name="test", data=data)
        
        # Test standard column
        uoc = model.get_column('Uoc')
        assert len(uoc) == 3
        assert pytest.approx(uoc.iloc[0]) == 0.6
        
        # Test calculated column Voc*Isc
        voc_isc = model.get_column('Voc*Isc')
        assert len(voc_isc) == 3
        
        # Test unit conversion for Rser (to mOhm)
        rser = model.get_column('RserLfDfIEC')
        assert pytest.approx(rser.iloc[0]) == 1.0  # 0.001 Ohm = 1 mOhm
        
        # Test unit conversion for Rsh (to kOhm)
        rsh = model.get_column('Rsh')
        assert pytest.approx(rsh.iloc[0]) == 1.0  # 1000 Ohm = 1 kOhm
