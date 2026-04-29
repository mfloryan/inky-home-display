import os
import pickle
import logging

logger = logging.getLogger(__name__)


def cache(cache_key, operation):
    cache_file = os.path.join(os.path.dirname(__file__), "cache", cache_key + ".pkl")
    try:
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        data = operation()

        # Skip saving empty arrays to disk
        if data == []:
            return data

        try:
            cache_path = os.path.dirname(cache_file)
            if not os.path.exists(cache_path):
                os.makedirs(cache_path, exist_ok=True)
            with open(cache_file, mode="wb") as f:
                pickle.dump(data, f)
        except Exception as exception:
            logger.error("Failed to write to cache: %s", exception)
        return data
