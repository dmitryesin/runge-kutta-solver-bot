import logging
import os

LOGS_DIR = "solver-bot/src/main/python/logs/"

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(LOGS_DIR + "bot.log", encoding='utf-8')
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
