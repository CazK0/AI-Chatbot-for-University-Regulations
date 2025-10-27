
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_debug(message):
    print(f"[DEBUG {datetime.now().strftime('%H:%M:%S')}] {message}")
    logger.debug(message)

def log_error(message):
    print(f"[ERROR {datetime.now().strftime('%H:%M:%S')}] {message}")
    logger.error(message)

def log_info(message):
    print(f"[INFO {datetime.now().strftime('%H:%M:%S')}] {message}")
    logger.info(message)