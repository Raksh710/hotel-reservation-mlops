import logging, os
from datetime import datetime as dt

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, f"log_{dt.now().strftime("%Y-%m-%d")}.log")

logging.basicConfig(filename=LOG_FILE, 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger