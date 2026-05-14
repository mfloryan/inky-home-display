import logging
import os

logger = logging.getLogger(__name__)


def read_token_file(filename, error_message):
    try:
        token_path = os.path.join(os.path.dirname(__file__), "..", filename)
        with open(token_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError as ex:
        logger.error("Token file `%s` not found", filename)
        raise RuntimeError(error_message) from ex
