import json
import os
from logger import logger

FAVOURITES_FILE = "favourites.json"

def save_favourite(city):
    if not isinstance(city, str):
        logger.warning(f"Attempted to save non-string favourite: {city}")
        return

    city = city.strip()
    if not city:
        logger.warning("Attempted to save empty or whitespace-only city.")
        return

    try:
        favourites = load_favourites()
        action = "added" if city not in favourites else "removed"
        
        if action == "added":
            favourites.append(city)
        else:
            favourites.remove(city)

        with open(FAVOURITES_FILE, "w") as f:
            json.dump(favourites, f)
        
        logger.info(f"Favourite city '{city}' {action} successfully.")
    except Exception as e:
        logger.error(f"Failed to save favourite '{city}': {type(e).__name__} - {e}")

def load_favourites():
    if os.path.exists(FAVOURITES_FILE):
        try:
            with open(FAVOURITES_FILE, "r") as f:
                favourites = json.load(f)
                return favourites
        except Exception as e:
            logger.error(f"Failed to load favourites: {type(e).__name__} - {e}")
            return []
    else:
        logger.info("Favourites file not found. Starting with an empty list.")
        return []

