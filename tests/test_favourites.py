import pytest
import json
from unittest.mock import patch, mock_open

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import favourites

# --- Tests for load_favourites ---

def test_load_favourites_file_not_found():
    """
    Tests that load_favourites returns an empty list if the file doesn't exist.
    """
    with patch("os.path.exists", return_value=False), \
         patch("favourites.logger") as mock_logger:
        result = favourites.load_favourites()
        assert result == []
        mock_logger.info.assert_called_once_with("Favourites file not found. Starting with an empty list.")

def test_load_favourites_success():
    """
    Tests that load_favourites correctly loads a list of cities from a JSON file.
    """
    mock_data = json.dumps(["London", "Paris"])
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_data)):
        result = favourites.load_favourites()
        assert result == ["London", "Paris"]

def test_load_favourites_json_error():
    """
    Tests that load_favourites returns an empty list if the file contains invalid JSON.
    """
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="invalid json")), \
         patch("favourites.logger") as mock_logger:
        result = favourites.load_favourites()
        assert result == []
        assert mock_logger.error.called

# --- Tests for save_favourite ---

def test_save_favourite_add_new_city():
    """
    Tests that a new city is added to the favourites list.
    """
    with patch("favourites.load_favourites", return_value=[]), \
         patch("builtins.open", mock_open()) as mock_file, \
         patch("json.dump") as mock_json_dump:
        favourites.save_favourite("Tokyo")
        mock_json_dump.assert_called_once_with(["Tokyo"], mock_file())

def test_save_favourite_remove_existing_city():
    """
    Tests that an existing city is removed from the favourites list.
    """
    with patch("favourites.load_favourites", return_value=["Tokyo"]), \
         patch("builtins.open", mock_open()) as mock_file, \
         patch("json.dump") as mock_json_dump:
        favourites.save_favourite("Tokyo")
        mock_json_dump.assert_called_once_with([], mock_file())

def test_save_favourite_empty_city_string():
    """
    Tests that an empty string is not saved.
    """
    with patch("favourites.logger") as mock_logger, \
         patch("favourites.load_favourites") as mock_load:
        favourites.save_favourite("   ")
        mock_logger.warning.assert_called_once_with("Attempted to save empty or whitespace-only city.")
        mock_load.assert_not_called()

def test_save_favourite_non_string_input():
    """
    Tests that non-string input is not saved.
    """
    with patch("favourites.logger") as mock_logger, \
         patch("favourites.load_favourites") as mock_load:
        favourites.save_favourite(123)
        mock_logger.warning.assert_called_once_with("Attempted to save non-string favourite: 123")
        mock_load.assert_not_called()
