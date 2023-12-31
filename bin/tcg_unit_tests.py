import unittest
from unittest.mock import patch, Mock, MagicMock
from tcg_validations import DataFrameValidator
import pandas as pd
from tcg_scraper_functions import get_todays_date, get_max_page_number, download_elements_from_webpage, get_card_data
from datetime import datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import numpy as np

class TestDataFrameValidator(unittest.TestCase):
    def setUp(self):
        """
        Set up the initial state for the test case.

        Parameters:
        self (TestCase): The current instance of the test case.

        Returns:
        None
        """
        self.df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6], 'col3': [7, 8, 9]})

    @patch('logging.info')
    def test_df_show_schema(self, mock_info):
        """
        Test the df_show_schema method of the DataFrameValidator class.

        :param mock_info: The mocked logging.info function.
        :return: None
        """
        df_validator = DataFrameValidator(self.df)
        df_validator.df_show_schema()
        self.assertTrue(mock_info.called)

class TestGetTodaysDate(unittest.TestCase):
    def setUp(self):
        """
        Set up the test case by getting today's date and formatting it.

        Parameters:
            self (TestCase): The test case object.

        Returns:
            None
        """
        self.formatted_date, self.hyphenated_formatted_date = get_todays_date()
    
    def test_get_todays_date(self):
        """
        Test case to check if the formatted date and hyphenated formatted date 
        are equal to today's date in their respective formats.
        """
        self.assertEqual(self.formatted_date, datetime.today().strftime('%Y%m%d'))
        self.assertEqual(self.hyphenated_formatted_date, datetime.today().strftime('%Y-%m-%d'))

class TestGetMaxPageNumber(unittest.TestCase):
    @patch('tcg_scraper_functions.WebDriverWait')
    @patch('tcg_scraper_functions.EC.presence_of_all_elements_located')
    @patch('logging.info')
    @patch('logging.error')
    def test_get_max_page_number(self, mock_error_logging, mock_info_logging, mock_presence, mock_wait):
        mock_driver = Mock()
        mock_wait.return_value.until.return_value = [Mock(text='5')]
        mock_presence.return_value = "xpath"

        result = get_max_page_number(mock_driver)

        mock_wait.assert_called_with(mock_driver, 12)
        mock_wait.return_value.until.assert_called_with("xpath")
        self.assertEqual(result, list(range(1, 6)))

    @patch('tcg_scraper_functions.WebDriverWait')
    @patch('logging.error')
    @patch('logging.info')
    def test_get_max_page_number_exception(self, mock_info_logging, mock_error_logging, mock_wait):
        mock_driver = Mock()
        mock_wait.return_value.until.side_effect = AttributeError('test exception')

        with self.assertRaises(AttributeError):  # assert the exception is raised
            get_max_page_number(mock_driver)

        self.assertEqual(mock_error_logging.call_count, 3)  # assert the error is logged three times

class TestDownloadElementsFromWebpage(unittest.TestCase):
    @patch('tcg_scraper_functions.WebDriverWait')
    @patch('tcg_scraper_functions.EC.presence_of_all_elements_located')
    @patch('logging.info')
    @patch('logging.error')
    def test_download_elements_from_webpage(self, mock_error_logging, mock_info_logging, mock_presence, mock_wait):
        mock_url = Mock()
        mock_driver = Mock()
        mock_elements = mock_wait.return_value.until.return_value = [Mock(text='web elements')]
        mock_presence.return_value = "css_selector"

        result = download_elements_from_webpage(mock_driver, mock_url)

        mock_wait.assert_called_with(mock_driver, 12)
        mock_wait.return_value.until.assert_called_with("css_selector")
        self.assertEqual(result, mock_elements)
        
    @patch('tcg_scraper_functions.WebDriverWait')
    @patch('logging.info')
    @patch('logging.error')
    def test_download_elements_from_webpage_exception(self, mock_error_logging, mock_info_logging, mock_wait):
        mock_url = Mock()
        mock_driver = Mock()
        mock_wait.return_value.until.side_effect = TimeoutException('test exception')

        with self.assertRaises(TimeoutException):  # assert the exception is raised
            download_elements_from_webpage(mock_driver, mock_url)
        self.assertEqual(mock_error_logging.call_count, 3)  # assert the error is called three times

