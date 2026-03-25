# -*- coding: utf-8 -*-
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scida-pro'))


class TestValidators:
    def test_is_number_valid(self):
        from utils.validators import is_number
        
        assert is_number("123") is True
        assert is_number("123.45") is True
        assert is_number("-123") is True
        assert is_number("0") is True
        assert is_number("1e-5") is True
    
    def test_is_number_invalid(self):
        from utils.validators import is_number
        
        assert is_number("abc") is False
        assert is_number("") is False
        assert is_number(None) is False
        assert is_number("12.34.56") is False
    
    def test_remove_whitespace(self):
        from utils.validators import remove_whitespace
        
        assert remove_whitespace("a b c") == "abc"
        assert remove_whitespace("a\tb\tc") == "abc"
        assert remove_whitespace("  test  ") == "test"
        assert remove_whitespace("") == ""
    
    def test_is_valid_filename(self):
        from utils.validators import is_valid_filename
        
        assert is_valid_filename("test.csv") is True
        assert is_valid_filename("path/to/file.csv") is True
        assert is_valid_filename("") is False
    
    def test_sanitize_filename(self):
        from utils.validators import sanitize_filename
        
        assert sanitize_filename("test file.csv") == "test file.csv"
        assert sanitize_filename("test@file#.csv") == "testfile.csv"
        assert sanitize_filename("a" * 50, max_length=40) == "a" * 40


class TestDataModel:
    def test_init(self):
        from models.data_model import DataModel
        
        model = DataModel()
        assert model.data == {}
        assert model.label_format == 0
    
    def test_get_dataset_count(self):
        from models.data_model import DataModel
        
        model = DataModel()
        assert model.get_dataset_count() == 0
    
    def test_clear_data(self):
        from models.data_model import DataModel
        
        model = DataModel()
        model._data[0] = pd.DataFrame({'Uoc': [1, 2, 3]})
        assert model.get_dataset_count() == 1
        
        model.clear_data()
        assert model.get_dataset_count() == 0
    
    def test_get_dataset_names(self):
        from models.data_model import DataModel
        
        model = DataModel()
        df = pd.DataFrame({'Uoc': [1, 2, 3]})
        df.index.name = "test_data"
        model._data[0] = df
        
        names = model.get_dataset_names()
        assert names == ["test_data"]
    
    def test_combine_datasets_empty(self):
        from models.data_model import DataModel
        
        model = DataModel()
        result = model.combine_datasets()
        assert result is False
    
    def test_combine_datasets_single(self):
        from models.data_model import DataModel
        
        model = DataModel()
        df = pd.DataFrame({'Uoc': [1, 2, 3]})
        model._data[0] = df
        
        result = model.combine_datasets()
        assert result is False
    
    def test_rename_dataset(self):
        from models.data_model import DataModel
        
        model = DataModel()
        df = pd.DataFrame({'Uoc': [1, 2, 3]})
        df.index.name = "old_name"
        model._data[0] = df
        
        success, new_name = model.rename_dataset(0, "new_name")
        assert success is True
        assert new_name == "new_name"
        assert model._data[0].index.name == "new_name"


class TestFilterModel:
    def test_init(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        assert model.user_filters == []
        assert model.max_filter_rows > 0
    
    def test_valid_parameters(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        params = model.valid_parameters
        
        assert 'Uoc' in params
        assert 'Isc' in params
        assert 'FF' in params
        assert 'Eta' in params
    
    def test_parse_filter_table_valid(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        table_data = [
            ['Uoc', '>', '0.5'],
            ['FF', '<', '80'],
        ]
        
        result = model.parse_filter_table(table_data)
        
        assert len(result) == 2
        assert result[0] == ['Uoc', '>', '0.5']
        assert result[1] == ['FF', '<', '80']
    
    def test_parse_filter_table_invalid(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        table_data = [
            ['InvalidParam', '>', '0.5'],
            ['Uoc', '=', '0.5'],
            ['FF', '<', 'not_a_number'],
        ]
        
        result = model.parse_filter_table(table_data)
        
        assert len(result) == 0
    
    def test_convert_to_plain_format(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        model._user_filters = [
            ['Uoc', '>', '0.5'],
            ['FF', '<', '80'],
        ]
        
        result = model.convert_to_plain_format()
        
        assert len(result) == 2
        assert result[0][2] == 0.5
        assert result[1][2] == 80
    
    def test_reset_to_default(self):
        from models.filter_model import FilterModel
        
        model = FilterModel()
        model._user_filters = [['Uoc', '>', '0.5']]
        
        result = model.reset_to_default()
        
        assert model._user_filters == []
        assert len(result) > 0


class TestReportModel:
    def test_init(self):
        from models.report_model import ReportModel
        
        model = ReportModel()
        assert model.summaries == []
        assert model.correlations == []
    
    def test_generate_summaries_empty(self):
        from models.report_model import ReportModel
        
        model = ReportModel()
        result = model.generate_summaries({})
        
        assert result == []
    
    def test_generate_summaries_with_data(self):
        from models.report_model import ReportModel
        
        model = ReportModel()
        data = {
            0: pd.DataFrame({
                'Uoc': [0.6, 0.61, 0.62],
                'Isc': [8.0, 8.1, 8.2],
                'RserLfDfIEC': [1.5, 1.6, 1.7],
                'Rsh': [1000, 1100, 1200],
                'FF': [78.0, 79.0, 80.0],
                'Eta': [18.0, 18.5, 19.0],
                'IRev1': [0.5, 0.6, 0.7]
            })
        }
        data[0].index.name = "test_data"
        
        result = model.generate_summaries(data)
        
        assert len(result) == 1
    
    def test_generate_correlations_empty(self):
        from models.report_model import ReportModel
        
        model = ReportModel()
        result = model.generate_correlations({})
        
        assert result == []
    
    def test_generate_correlations_with_data(self):
        from models.report_model import ReportModel
        
        model = ReportModel()
        data = {
            0: pd.DataFrame({
                'Uoc': [0.6, 0.61, 0.62, 0.63],
                'Isc': [8.0, 8.1, 8.2, 8.3],
                'RserLfDfIEC': [1.5, 1.6, 1.7, 1.8],
                'Rsh': [1000, 1100, 1200, 1300],
                'FF': [78.0, 79.0, 80.0, 81.0],
                'Eta': [18.0, 18.5, 19.0, 19.5],
                'IRev1': [0.5, 0.6, 0.7, 0.8]
            })
        }
        data[0].index.name = "test_data"
        
        result = model.generate_correlations(data)
        
        assert len(result) == 1


class TestConfig:
    def test_get_config_singleton(self):
        from utils.config import get_config, Config
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_config_get(self):
        from utils.config import get_config
        
        config = get_config()
        
        assert config.get('app.name') == 'SCiDA Pro'
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_config_colors(self):
        from utils.config import get_config
        
        config = get_config()
        colors = config.colors
        
        assert isinstance(colors, list)
        assert len(colors) > 0
    
    def test_config_internal_labels(self):
        from utils.config import get_config
        
        config = get_config()
        labels = config.internal_labels
        
        assert 'Uoc' in labels
        assert 'Isc' in labels


class TestDataUtils:
    def test_convert_param_value_rser(self):
        from utils.data_utils import convert_param_value
        
        result = convert_param_value('RserLfDfIEC', 1.5)
        assert result == 1500
    
    def test_convert_param_value_rsh(self):
        from utils.data_utils import convert_param_value
        
        result = convert_param_value('Rsh', 1000)
        assert result == 1.0
    
    def test_convert_param_value_other(self):
        from utils.data_utils import convert_param_value
        
        result = convert_param_value('Uoc', 0.6)
        assert result == 0.6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
