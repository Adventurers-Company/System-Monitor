# logs.py
import logging
from datetime import datetime

logging.basicConfig(
    filename='system_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_info(msg):
    logging.info(msg)