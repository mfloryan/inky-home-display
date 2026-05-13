import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=8)
def load_token(filename, service_name):
    try:
        file_path = os.path.join(os.path.dirname(__file__), filename)
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as ex:
        logger.error("Token file `%s` not found", filename)
        raise RuntimeError(f"Unable to load {service_name} token") from ex
