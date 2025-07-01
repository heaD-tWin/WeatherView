import pytest
from unittest.mock import patch, MagicMock

# Add project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to be tested
import weather_api

# --- Test Fixtures ---

@pytest.fixture
def mock_requests_get():
    """Fixture to patch 'requests.get' and provide a mock response object."""
    with patch('weather_api.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        yield mock_response

# --- Tests for get_weather_by_city ---

def test_get_weather_by_city_success(mock_requests_get):
    """
    Tests successful parsing of a valid weather API response.
    """
    # Set the status code for a successful response
    mock_requests_get.status_code = 200
    mock_requests_get.json.return_value = {
        "cod": 200, "name": "London", "dt": 1672531200,
        "main": {"temp": 15.55, "humidity": 80},
        "wind": {"speed": 5.12},
        "weather": [{"description": "broken clouds", "icon": "04d"}]
    }
    
    result = weather_api.get_weather_by_city("London", "metric")
    
    assert result["city"] == "London"
    assert result["temperature"] == 15.6
    assert result["condition"] == "broken clouds"
    assert result["humidity"] == 80
    assert result["wind_speed"] == 5.1
    assert "error" not in result

def test_get_weather_by_city_not_found(mock_requests_get):
    """
    Tests handling of a 'location not found' error from the API.
    """
    mock_requests_get.status_code = 404
    mock_requests_get.json.return_value = {"cod": "404", "message": "city not found"}
    
    result = weather_api.get_weather_by_city("InvalidCity", "metric")
    
    assert "error" in result
    assert result["error"] == "Location not found."

@patch('weather_api.requests.get', side_effect=Exception("Network Error"))
def test_get_weather_by_city_request_fails(mock_get):
    """
    Tests handling of a network failure during the API request.
    """
    result = weather_api.get_weather_by_city("London", "metric")
    
    assert "error" in result
    assert result["error"] == "Request failed."

# --- Tests for get_forecast_by_city ---

def test_get_forecast_by_city_success(mock_requests_get):
    """
    Tests successful parsing of a valid 5-day forecast API response.
    """
    mock_requests_get.status_code = 200
    mock_requests_get.json.return_value = {
        "cod": "200", "city": {"timezone": 0},
        "list": [
            {"dt_txt": "2025-07-01 12:00:00", "main": {"temp": 20}, "weather": [{"description": "clear", "icon": "01d"}]},
            {"dt_txt": "2025-07-01 15:00:00", "main": {"temp": 22}, "weather": [{"description": "clear", "icon": "01d"}]}
        ]
    }
    
    result = weather_api.get_forecast_by_city("London", "metric")
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["date"] == "2025-07-01"
    assert result[0]["temperature"] == 20

# --- Tests for get_detailed_forecast_by_city ---

def test_get_detailed_forecast_by_city_success(mock_requests_get):
    """
    Tests successful parsing of a detailed forecast for the graph.
    """
    mock_requests_get.status_code = 200
    mock_requests_get.json.return_value = {
        "cod": "200",
        "list": [
            {"dt_txt": "2025-07-01 12:00:00", "main": {"temp": 20}, "weather": [{"description": "clear", "icon": "01d"}]},
            {"dt_txt": "2025-07-01 15:00:00", "main": {"temp": 22}, "weather": [{"description": "clear", "icon": "01d"}]}
        ]
    }
    
    result = weather_api.get_detailed_forecast_by_city("London", "metric")
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[1]["datetime"] == "2025-07-01 15:00:00"
    assert result[1]["temperature"] == 22

# --- Tests for extract_daily_min_max ---

def test_extract_daily_min_max():
    """
    Tests the logic of the helper function that extracts min/max temperatures.
    """
    forecast_list = [
        {"dt_txt": "2025-07-01 12:00:00", "main": {"temp": 15}},
        {"dt_txt": "2025-07-01 18:00:00", "main": {"temp": 20}},
        {"dt_txt": "2025-07-02 12:00:00", "main": {"temp": 18}},
        {"dt_txt": "2025-07-02 18:00:00", "main": {"temp": 25}}
    ]
    
    result = weather_api.extract_daily_min_max(forecast_list)
    
    assert result["2025-07-01"]["min"] == 15
    assert result["2025-07-01"]["max"] == 20
    assert result["2025-07-02"]["min"] == 18
    assert result["2025-07-02"]["max"] == 25
