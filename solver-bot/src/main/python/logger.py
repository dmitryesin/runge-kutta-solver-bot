import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs/bot.log")
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
