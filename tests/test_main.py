import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

# --- Tests for main application functions ---

def test_on_select_favourite_triggers_search_and_update():
    """
    Tests that selecting a favourite city correctly updates the UI and triggers a search.
    """
    mock_ui = {
        "favourites_dropdown": MagicMock(),
        "search_entry": MagicMock()
    }
    mock_ui["favourites_dropdown"].get.return_value = "London"
    unit_var = MagicMock()

    with patch("main.handle_search") as mock_handle_search, \
         patch("main.update_fav_button") as mock_update_fav_button:
        main.on_select_favourite(mock_ui, unit_var)
        mock_ui["search_entry"].delete.assert_called_once_with(0, tk.END)
        mock_ui["search_entry"].insert.assert_called_once_with(0, "London")
        mock_handle_search.assert_called_once_with(mock_ui, unit_var)
        mock_update_fav_button.assert_called_once_with(mock_ui)

def test_on_close_calls_destroy_and_logs():
    mock_root = MagicMock()
    with patch("main.logger") as mock_logger:
        main.on_close(mock_root)
        mock_logger.info.assert_called_once_with("Application closed by user.")
        mock_root.destroy.assert_called_once()

