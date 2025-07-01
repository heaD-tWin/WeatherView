import pytest
from unittest.mock import MagicMock, patch, ANY
import tkinter as tk

# Add project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to be tested
import utils
import themes
import geolocation

# --- Tests for utils.py ---

@pytest.fixture
def mock_ui():
    """Provides a mock UI object for utils tests."""
    ui = {
        "search_entry": MagicMock(),
        "favourites_dropdown": MagicMock(),
        "save_button": MagicMock()
    }
    ui["search_entry"].get.return_value = "London"
    return ui

def test_on_save_favourite_new_city(mock_ui):
    """Tests that a new city is saved and the UI is updated."""
    with patch("utils.load_favourites", return_value=[]), \
         patch("utils.save_favourite") as mock_save, \
         patch("utils.update_fav_button") as mock_update:
        
        # Action
        utils.on_save_favourite(mock_ui)
        
        # Assertions
        mock_save.assert_called_once_with("London")
        # Corrected Assertion: Check for the dictionary item assignment
        mock_ui["favourites_dropdown"].__setitem__.assert_called_once_with('values', ['London'])
        mock_update.assert_called_once_with(mock_ui)

def test_update_fav_button_city_is_favourite(mock_ui):
    """Tests that the button shows 'Remove' when the city is a favourite."""
    with patch("utils.load_favourites", return_value=["London"]):
        utils.update_fav_button(mock_ui)
        mock_ui["save_button"].config.assert_called_with(
            text="Remove from Favourites",
            # Use ANY from unittest.mock
            command=ANY
        )
        mock_ui["favourites_dropdown"].set.assert_called_with("London")

def test_on_remove_favourite(mock_ui):
    """Tests that a city is removed and the UI is updated."""
    with patch("utils.load_favourites", return_value=["London"]), \
         patch("utils.save_favourite") as mock_save, \
         patch("utils.update_fav_button") as mock_update:
        
        # Action
        utils.on_remove_favourite(mock_ui)

        # Assertions
        mock_save.assert_called_once_with("London")
        # Corrected Assertion: Check for the dictionary item assignment
        mock_ui["favourites_dropdown"].__setitem__.assert_called_once_with('values', [])
        mock_update.assert_called_once_with(mock_ui)

# --- Tests for themes.py ---

@pytest.mark.parametrize("condition", [
    "clear", "few clouds", "shower rain", "thunderstorms", 
    "light snow", "mist", "drizzle", "unknown condition"
])
def test_set_dynamic_background(condition):
    """Tests that the correct background color category is chosen."""
    mock_root = MagicMock()
    style = MagicMock()
    with patch('themes.ttk.Style', return_value=style):
        # Action
        bg, dark, light = themes.set_dynamic_background(mock_root, condition)
    
    # Assertions
    # Verify that valid colors are returned and the root is configured
    assert isinstance(bg, str) and bg.startswith("#")
    assert isinstance(dark, str) and dark.startswith("#")
    assert isinstance(light, str) and light.startswith("#")
    mock_root.configure.assert_called_with(bg=bg)

# --- Tests for graph_forecast.py ---

def test_create_forecast_figure():
    """Tests that a matplotlib figure is created with the correct data."""
    # Import locally to avoid collection errors
    import graph_forecast
    
    forecast_data = [
        {"datetime": "2025-07-01 12:00:00", "temperature": 20},
        {"datetime": "2025-07-01 15:00:00", "temperature": 22}
    ]
    fig = graph_forecast.create_forecast_figure(forecast_data, "Test City", "#FFFFFF", "#000000", "#EEEEEE", "metric")
    
    ax = fig.axes[0]
    # Use a simple 'C' to avoid any potential encoding issues
    assert "5-Day Temperature Forecast for Test City (C)" in ax.get_title()
    assert len(ax.lines[0].get_ydata()) == 2
    assert ax.lines[0].get_ydata()[1] == 22

# --- Tests for geolocation.py ---

@patch('geolocation.requests.get')
def test_get_user_city_success(mock_get):
    """Tests successful retrieval of a user's city from IP and geolocation APIs."""
    mock_ip_response = MagicMock()
    mock_ip_response.json.return_value = {"loc": "51.50,-0.12"}
    
    mock_geo_response = MagicMock()
    mock_geo_response.json.return_value = {"address": {"city": "London"}}
    
    mock_get.side_effect = [mock_ip_response, mock_geo_response]
    
    city = geolocation.get_user_city()
    
    assert city == "London"
    assert mock_get.call_count == 2

@patch('geolocation.requests.get', side_effect=Exception("Network Error"))
@patch('geolocation.logger')
def test_get_user_city_failure(mock_logger, mock_get):
    """Tests that None is returned and an error is logged on failure."""
    city = geolocation.get_user_city()
    
    assert city is None
    mock_logger.error.assert_called_once()
