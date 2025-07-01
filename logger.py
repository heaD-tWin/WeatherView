import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

log_filename = datetime.now().strftime("logs/log_%Y-%m-%d.log")

logging.basicConfig(
    filename=log_filename,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("WeatherViewLogger")

