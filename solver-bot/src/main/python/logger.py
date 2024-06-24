import logging
import os

PY_DIR = "solver-bot/src/main/python/"

if not os.path.exists(PY_DIR + "logs"):
    os.makedirs(PY_DIR + "logs")

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(PY_DIR + "logs/bot.log")
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
