import logging
import os
from datetime import datetime

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Create a log file named by date
log_filename = datetime.now().strftime("logs/log_%Y-%m-%d.log")

# Configure logger
logging.basicConfig(
    filename=log_filename,
    filemode='a',
    level=logging.INFO,  # You can change to DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Shortcut to the logger object
logger = logging.getLogger("WeatherViewLogger")

