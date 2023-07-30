import unittest
from unittest.mock import patch, Mock
from tcg_validations import DataFrameValidator
import pandas as pd
from tcg_scraper_functions import get_todays_date
from datetime import datetime

class TestDataFrameValidator(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6], 'col3': [7, 8, 9]})

    @patch('logging.info')
    def test_df_show_schema(self, mock_info):
        df_validator = DataFrameValidator(self.df)
        df_validator.df_show_schema()
        self.assertTrue(mock_info.called)

class TestGetTodaysDate(unittest.TestCase):
    def setUp(self):
        self.formatted_date, self.hyphenated_formatted_date = get_todays_date()
    
    def test_get_todays_date(self):
        self.assertEqual(self.formatted_date, datetime.today().strftime('%Y%m%d'))
        self.assertEqual(self.hyphenated_formatted_date, datetime.today().strftime('%Y-%m-%d'))