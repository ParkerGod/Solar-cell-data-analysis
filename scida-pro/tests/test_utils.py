# -*- coding: utf-8 -*-
"""
Unit tests for utility functions
"""

import pytest
import pandas as pd
import numpy as np

from utils import (
    is_number,
    remove_whitespace,
    is_valid_ascii_filename,
    sanitize_filename,
    get_file_extension,
    calculate_statistics,
    calculate_correlation,
    safe_division,
    apply_unit_conversion,
    validate_filter_condition,
    apply_filter,
    count_filtered_out
)


class TestUtils:
    """Test cases for utility functions"""
    
    def test_is_number_with_valid_numbers(self):
        """Test is_number with valid numeric values"""
        assert is_number(42)
        assert is_number(3.14)
        assert is_number("123")
        assert is_number("3.14")
        assert is_number("-42")
        assert is_number(np.pi)
    
    def test_is_number_with_invalid_numbers(self):
        """Test is_number with invalid numeric values"""
        assert not is_number("abc")
        assert not is_number("12a3")
        assert not is_number(None)
        assert not is_number([])
        assert not is_number({})
    
    def test_remove_whitespace(self):
        """Test whitespace removal"""
        assert remove_whitespace("  hello  world  ") == "helloworld"
        assert remove_whitespace("\t tab \t test \t") == "tabtest"
        assert remove_whitespace("no_spaces") == "no_spaces"
        assert remove_whitespace("") == ""
    
    def test_is_valid_ascii_filename(self):
        """Test ASCII filename validation"""
        assert is_valid_ascii_filename("test.csv")
        assert is_valid_ascii_filename("data_123.xlsx")
        assert not is_valid_ascii_filename("测试.csv")  # Chinese characters
        assert not is_valid_ascii_filename("datá.csv")  # Accented character
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Keep valid characters
        assert sanitize_filename("test_file.csv") == "test_file.csv"
        assert sanitize_filename("test file.xlsx") == "test file.xlsx"
        
        # Remove invalid characters
        assert sanitize_filename("test/file:name?") == "testfilename"
        
        # Truncate long names
        long_name = "a" * 50
        assert len(sanitize_filename(long_name)) == 40
    
    def test_get_file_extension(self):
        """Test file extension extraction"""
        assert get_file_extension("test.csv") == ".csv"
        assert get_file_extension("data.XLSX") == ".xlsx"
        assert get_file_extension("no_extension") == ""
        assert get_file_extension("path/to/file.txt") == ".txt"
    
    def test_calculate_statistics(self):
        """Test statistics calculation"""
        data = pd.DataFrame({
            'Uoc': [0.6, 0.62, 0.58, 0.61],
            'Isc': [8.0, 8.2, 7.8, 8.1],
            'RserLfDfIEC': [0.001, 0.0012, 0.0009, 0.0011],
            'Rsh': [1000.0, 1200.0, 900.0, 1100.0],
            'FF': [75.0, 76.0, 74.0, 75.5],
            'Eta': [18.0, 18.5, 17.5, 18.2],
            'IRev1': [0.001, 0.0008, 0.0012, 0.0009]
        })
        
        stats = calculate_statistics(data)
        
        assert not stats.empty
        assert list(stats.index) == ['Best cell', 'Median', 'Average', 'Std.dev.']
        
        # Best cell should be the one with maximum Eta (index 1, Eta=18.5)
        assert pytest.approx(stats.loc['Best cell', 'Eta']) == 18.5
    
    def test_calculate_correlation(self):
        """Test correlation calculation"""
        # Create correlated data
        np.random.seed(42)
        x = np.random.rand(100)
        y = 2 * x + np.random.randn(100) * 0.1  # y correlated with x
        
        data = pd.DataFrame({
            'Uoc': x,
            'Isc': y,
            'RserLfDfIEC': np.random.rand(100),
            'Rsh': np.random.rand(100),
            'FF': np.random.rand(100),
            'Eta': np.random.rand(100),
            'IRev1': np.random.rand(100)
        })
        
        corr = calculate_correlation(data)
        
        assert not corr.empty
        
        # Uoc and Isc should be correlated
        assert 'Uoc' in corr.columns
        assert 'Isc' in corr.columns
    
    def test_calculate_correlation_with_insufficient_data(self):
        """Test correlation calculation with insufficient data"""
        data = pd.DataFrame({
            'Uoc': [0.6],
            'Isc': [8.0],
            'RserLfDfIEC': [0.001],
            'Rsh': [1000.0],
            'FF': [75.0],
            'Eta': [18.0],
            'IRev1': [0.001]
        })
        
        corr = calculate_correlation(data)
        assert corr.empty  # Should return empty for single data point
    
    def test_safe_division_scalar(self):
        """Test safe division with scalars"""
        # Normal division
        assert safe_division(10, 2) == 5.0
        
        # Division by zero
        assert safe_division(10, 0) == 0.0
        
        # Custom default
        assert safe_division(10, 0, default=np.nan) is np.nan
    
    def test_safe_division_array(self):
        """Test safe division with numpy arrays"""
        numerator = np.array([10, 20, 30])
        denominator = np.array([2, 0, 5])
        
        result = safe_division(numerator, denominator)
        expected = np.array([5.0, 0.0, 6.0])
        
        np.testing.assert_array_equal(result, expected)
    
    def test_apply_unit_conversion_rser(self):
        """Test Rser unit conversion (Ohm to mOhm)"""
        data = pd.Series([0.001, 0.002, 0.003])  # Ohms
        converted = apply_unit_conversion(data, 'Rser')
        
        # 0.001 Ohm = 1 mOhm
        assert pytest.approx(converted.iloc[0]) == 1.0
    
    def test_apply_unit_conversion_rsh(self):
        """Test Rsh unit conversion (Ohm to kOhm)"""
        data = pd.Series([1000.0, 2000.0, 3000.0])  # Ohms
        converted = apply_unit_conversion(data, 'Rsh')
        
        # 1000 Ohm = 1 kOhm
        assert pytest.approx(converted.iloc[0]) == 1.0
    
    def test_apply_unit_conversion_eta(self):
        """Test Eta unit conversion (decimal to percentage)"""
        data = pd.Series([0.18, 0.19, 0.20])  # Decimal
        converted = apply_unit_conversion(data, 'Eta')
        
        # 0.18 = 18%
        assert pytest.approx(converted.iloc[0]) == 18.0
    
    def test_apply_unit_conversion_inverse(self):
        """Test inverse unit conversion"""
        data = pd.Series([1.0])  # mOhm
        converted = apply_unit_conversion(data, 'Rser', inverse=True)
        
        # 1 mOhm = 0.001 Ohm
        assert pytest.approx(converted.iloc[0]) == 0.001
    
    def test_validate_filter_condition(self):
        """Test filter condition validation"""
        # Valid conditions
        assert validate_filter_condition('Uoc', '>', '0.5')
        assert validate_filter_condition('Eta', '<', '20')
        
        # Invalid conditions
        assert not validate_filter_condition('Invalid', '>', '0.5')
        assert not validate_filter_condition('Uoc', 'invalid', '0.5')
        assert not validate_filter_condition('Uoc', '>', 'not_a_number')
    
    def test_apply_filter_greater_than(self):
        """Test applying > filter to DataFrame"""
        data = pd.DataFrame({
            'Eta': [17.0, 18.0, 19.0, 20.0, 21.0]
        })
        
        # Keep values <= 19.0 (filter out values > 19.0)
        filtered = apply_filter(data, 'Eta', '>', 19.0)
        
        # Should keep 3 values: 17.0, 18.0, 19.0
        assert len(filtered) == 3
        assert max(filtered['Eta']) == 19.0
    
    def test_apply_filter_less_than(self):
        """Test applying < filter to DataFrame"""
        data = pd.DataFrame({
            'FF': [70.0, 72.0, 74.0, 76.0, 78.0]
        })
        
        # Keep values >= 74.0 (filter out values < 74.0)
        filtered = apply_filter(data, 'FF', '<', 74.0)
        
        # Should keep 3 values: 74.0, 76.0, 78.0
        assert len(filtered) == 3
        assert min(filtered['FF']) == 74.0
    
    def test_apply_filter_invalid_column(self):
        """Test applying filter with invalid column"""
        data = pd.DataFrame({'Eta': [18.0, 19.0]})
        
        # Invalid column should return unchanged data
        filtered = apply_filter(data, 'Invalid', '>', 19.0)
        assert len(filtered) == 2
    
    def test_count_filtered_out(self):
        """Test counting filtered out rows"""
        data = pd.DataFrame({
            'Eta': [17.0, 18.0, 19.0, 20.0, 21.0]
        })
        
        # Count values > 19.0 (should be 2: 20.0 and 21.0)
        count = count_filtered_out(data, 'Eta', '>', 19.0)
        assert count == 2
        
        # Count values < 18.0 (should be 1: 17.0)
        count = count_filtered_out(data, 'Eta', '<', 18.0)
        assert count == 1
