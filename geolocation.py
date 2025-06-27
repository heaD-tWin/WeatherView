import requests
import certifi
import os
import sys
from dotenv import load_dotenv
from logger import logger

if getattr(sys, 'frozen', False):
    env_path = os.path.join(os.path.dirname(sys.executable), ".env")
else:
    env_path = ".env"

load_dotenv()
EMAIL = os.getenv("GEOPY_USER_AGENT_EMAIL")
if not EMAIL:
    raise ValueError("GEOPY_USER_AGENT_EMAIL is not set in your .env file.")

def get_user_city():
    try:
        ip_response = requests.get("https://ipinfo.io/json", verify=certifi.where())
        location_data = ip_response.json()
        loc = location_data.get("loc")

        if loc:
            lat, lon = loc.split(",")
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en&addressdetails=1"
            headers = {"User-Agent": "weather_dashboard (EMAIL)"}
            response = requests.get(url, headers=headers, verify=certifi.where())
            response.raise_for_status()
            data = response.json()

            address = data.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village")
            return city

    except Exception as e:
        logger.error(f"Could not retrieve geolocation: {type(e).__name__} - {e}")

    return None


