import pytest
from unittest.mock import patch, MagicMock
from scrapers import mpxnj

@patch("scrapers.mpxnj.webdriver.Chrome")
def test_get_valid_cookies_returns_dict(mock_chrome):
  # Setup mock driver and cookies
  mock_driver = MagicMock()
  mock_driver.get_cookies.return_value = [
    {'name': 'cookie1', 'value': 'value1'},
    {'name': 'cookie2', 'value': 'value2'}
  ]
  mock_chrome.return_value.__enter__.return_value = mock_driver

  cookies = mpxnj.get_valid_cookies()

  assert isinstance(cookies, dict)
  assert cookies == {'cookie1': 'value1', 'cookie2': 'value2'}
  mock_driver.get.assert_any_call("https://mpxnj.com")
  mock_driver.execute_script.assert_called_with("localStorage.setItem('age_confirm', 'true');")

@patch("scrapers.mpxnj.webdriver.Chrome")
def test_get_valid_cookies_empty(mock_chrome):
  # Setup mock driver with no cookies
  mock_driver = MagicMock()
  mock_driver.get_cookies.return_value = []
  mock_chrome.return_value.__enter__.return_value = mock_driver

  cookies = mpxnj.get_valid_cookies()

  assert cookies == {}

@patch("scrapers.mpxnj.webdriver.Chrome")
def test_get_valid_cookies_sets_localstorage_and_navigates(mock_chrome):
  mock_driver = MagicMock()
  mock_driver.get_cookies.return_value = []
  mock_chrome.return_value.__enter__.return_value = mock_driver

  mpxnj.get_valid_cookies()

  # Should call get twice and execute_script once
  assert mock_driver.get.call_count == 2
  mock_driver.execute_script.assert_called_once_with("localStorage.setItem('age_confirm', 'true');")