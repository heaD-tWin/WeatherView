import json
import os

FAVOURITES_FILE = "favourites.json"

def save_favourite(city):
    if not isinstance(city, str):
        return

    city = city.strip()
    if not city:
        return

    favourites = load_favourites()
    if city not in favourites:
        favourites.append(city)
        with open(FAVOURITES_FILE, "w") as f:
            json.dump(favourites, f)
    else:
        favourites.remove(city)
        with open(FAVOURITES_FILE, "w") as f:
            json.dump(favourites, f)


def load_favourites():
    if os.path.exists(FAVOURITES_FILE):
        with open(FAVOURITES_FILE, "r") as f:
            return json.load(f)
    return []

