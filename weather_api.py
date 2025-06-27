import requests
import os
import sys
from logger import logger
from dotenv import load_dotenv
import datetime
from collections import defaultdict


if getattr(sys, 'frozen', False):
    env_path = os.path.join(os.path.dirname(sys.executable), ".env")
else:
    env_path = ".env"

load_dotenv()
API_KEY = API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    logger.error("OPENWEATHER_API_KEY is not set in your .env file")
    raise ValueError("OPENWEATHER_API_KEY is not set in your .env file")

def get_weather_by_city(city, unit_var):
    unit = unit_var
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("cod") != 200:
            logger.error("Could not find location in get_weather_by_city")
            return {"error": "Location not found."}

        timestamp = data.get("dt")
        if timestamp:
            dt_obj = datetime.datetime.fromtimestamp(timestamp)
            day = dt_obj.strftime("%A")
            date = dt_obj.strftime("%Y-%m-%d")
            time = dt_obj.strftime("%I:%M %p")
        else:
            day = date = time = "N/A"

        return {
            "city": data["name"],
            "temperature": round(data["main"]["temp"], 1),
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "icon": data["weather"][0]["icon"],
            "day": day,
            "date": date,
            "time": time
        }
    except Exception as e:
        logger.error("API request failed in get_weather_by_city")
        return {"error": "Request failed."}


def get_forecast_by_city(city, unit_var):
    unit = unit_var
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "list" not in data:
            logger.error(data.get("message", "Unknown error."))
            return {"error": data.get("message", "Unknown error.")}

        forecast_list = data["list"]
        min_max_by_date = extract_daily_min_max(forecast_list)

        daily_entries = {}
        for entry in forecast_list:
            dt_utc = datetime.datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
            local_dt = dt_utc + datetime.timedelta(seconds=data["city"]["timezone"])
            date_str = local_dt.strftime("%Y-%m-%d")
            time_diff = abs((local_dt - local_dt.replace(hour=12, minute=0, second=0)).total_seconds())

            if date_str not in daily_entries or time_diff < daily_entries[date_str][0]:
                daily_entries[date_str] = (time_diff, entry)

        today_utc = datetime.datetime.now(datetime.timezone.utc).date()

        daily_forecasts = []
        for date, (_, entry) in daily_entries.items():
            forecast_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if forecast_date < today_utc:
                continue

            if date not in min_max_by_date:
                continue

            daily_forecasts.append({
                "date": date,
                "temperature": round(entry["main"]["temp"], 1),
                "min_temp": min_max_by_date[date]["min"],
                "max_temp": min_max_by_date[date]["max"],
                "condition": entry["weather"][0]["description"],
                "icon": entry["weather"][0]["icon"]
            })

        return daily_forecasts

    except Exception as e:
        logger.error(f"Exception in get_forecast_by_city: {e}")
        return {"error": str(e)}

def get_detailed_forecast_by_city(city, unit_var):
    unit = unit_var
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "list" not in data:
            logger.error(data.get("message", "Unknown error."))
            return {"error": data.get("message", "Unknown error.")} 

        forecast_points = []

        for entry in data["list"]:
            forecast_points.append({
                "datetime": entry["dt_txt"],
                "temperature": entry["main"]["temp"],
                "condition": entry["weather"][0]["description"],
                "icon": entry["weather"][0]["icon"]
            })

        return forecast_points

    except Exception as e:
        logger.error(str(e))
        return {"error": str(e)}


def extract_daily_min_max(forecast_list):

    daily_temps = defaultdict(list)

    for entry in forecast_list:
        date = entry["dt_txt"].split(" ")[0]
        temp = entry["main"]["temp"]
        daily_temps[date].append(temp)

    daily_min_max = {}
    for date, temps in daily_temps.items():
        daily_min_max[date] = {
            "min": round(min(temps), 1),
            "max": round(max(temps), 1)
        }

    return daily_min_max


