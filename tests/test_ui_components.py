import pytest
from unittest.mock import MagicMock, patch, ANY
import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ui_components

# --- Test Fixtures ---

@pytest.fixture
def mock_ui():
    """Provides a mock UI dictionary for testing UI component functions."""
    root = tk.Tk()
    ui = {
        "root": root, "search_entry": MagicMock(), "status_label": MagicMock(),
        "search_button": MagicMock(), "city_label": MagicMock(), "temp_label": MagicMock(),
        "condition_label": MagicMock(), "humidity_label": MagicMock(), "wind_label": MagicMock(),
        "time_label": MagicMock(), "icon_label": MagicMock(), "forecast_cards_container": MagicMock(),
        "chart_frame": MagicMock(), "save_button": MagicMock(), "unit_toggle_button": MagicMock(),
    }
    ui["search_entry"].get.return_value = "London"
    yield ui
    root.destroy()

@pytest.fixture
def mock_unit_var():
    """Provides a mock Tkinter StringVar for the unit."""
    var = MagicMock()
    var.get.return_value = "metric"
    return var

# --- Tests for handle_search ---

@patch('ui_components.get_weather_by_city')
@patch('ui_components.get_forecast_by_city')
@patch('ui_components.get_detailed_forecast_by_city')
@patch('ui_components.set_dynamic_background')
@patch('ui_components.load_weather_icon')
@patch('ui_components.create_forecast_figure')
@patch('ui_components.embed_chart')
@patch('ui_components.update_fav_button')
@patch('ui_components.reset_auto_refresh')
def test_handle_search_success(
    mock_reset_refresh, mock_update_fav, mock_embed, mock_create_fig,
    mock_load_icon, mock_set_bg, mock_get_detailed, mock_get_forecast,
    mock_get_weather, mock_ui, mock_unit_var
):
    """
    Tests the successful path of handle_search, where all API calls return valid data.
    """
    mock_get_weather.return_value = {
        "city": "London", "temperature": 15, "condition": "Clouds",
        "humidity": 80, "wind_speed": 5, "day": "Tuesday",
        "date": "2025-07-01", "time": "12:00", "icon": "04d"
    }
    mock_get_forecast.return_value = []
    mock_get_detailed.return_value = []
    mock_load_icon.return_value = "fake_photo_image"
    mock_set_bg.return_value = ("#B0C4DE", "#3A4A5A", "#E8EEF4")

    ui_components.handle_search(mock_ui, mock_unit_var)

    mock_ui["status_label"].config.assert_any_call(text="Loading...", foreground="black")
    mock_get_weather.assert_called_once_with("London", "metric")
    mock_ui["city_label"].config.assert_called_with(text="London", foreground="black")
    mock_ui["temp_label"].config.assert_called_with(text="Temperature: 15°C")
    assert mock_set_bg.call_count == 2
    mock_load_icon.assert_called_once_with("04d", size=(150, 150))
    mock_ui["icon_label"].config.assert_called_with(image="fake_photo_image")
    mock_update_fav.assert_called_once()
    mock_reset_refresh.assert_called_once()

@patch('ui_components.get_weather_by_city')
@patch('ui_components.update_fav_button')
@patch('ui_components.reset_auto_refresh')
def test_handle_search_location_not_found(
    mock_reset_refresh, mock_update_fav, mock_get_weather, mock_ui, mock_unit_var
):
    """
    Tests the failure path where the weather API returns a 'Location not found' error.
    """
    mock_get_weather.return_value = {"error": "Location not found"}

    ui_components.handle_search(mock_ui, mock_unit_var)

    mock_ui["city_label"].config.assert_called_with(text="City: Not found", foreground="red")
    mock_ui["temp_label"].config.assert_called_with(text="Temperature: —")
    mock_ui["condition_label"].config.assert_called_with(text="Condition: —")
    mock_ui["status_label"].config.assert_called_with(text="Bad Location", foreground="red")
    mock_update_fav.assert_called_once()
    mock_reset_refresh.assert_called_once()

# --- Tests for load_weather_icon ---

@patch('ui_components.os.path.exists', return_value=True)
@patch('ui_components.Image.open')
@patch('ui_components.ImageTk.PhotoImage')
@patch('ui_components.resource_path', side_effect=lambda x: x)
def test_load_weather_icon_success(mock_resource_path, mock_photo_image, mock_image_open, mock_exists):
    """
    Tests that a weather icon is loaded correctly when the file exists.
    """
    result = ui_components.load_weather_icon("01d")
    mock_exists.assert_called_once_with(os.path.join("weather_icons", "01d.png"))
    mock_image_open.assert_called_once()
    mock_photo_image.assert_called_once()
    assert result is not None

@patch('ui_components.os.path.exists', return_value=False)
@patch('ui_components.Image.open')
@patch('ui_components.ImageTk.PhotoImage')
@patch('ui_components.resource_path', side_effect=lambda x: x)
def test_load_weather_icon_fallback_to_default(mock_resource_path, mock_photo_image, mock_image_open, mock_exists):
    """
    Tests that the default icon is loaded when the specific icon file does not exist.
    """
    ui_components.load_weather_icon("non_existent_icon")
    mock_image_open.assert_called_once_with(os.path.join("weather_icons", "default.png"))
    mock_photo_image.assert_called_once()
