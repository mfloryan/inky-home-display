import os
import json
import logging

logger = logging.getLogger(__name__)


def cache(cache_key, operation):
    cache_file = os.path.join(os.path.dirname(__file__), "cache", cache_key + ".json")
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = operation()

        # Skip saving empty arrays to disk
        if data == []:
            return data

        try:
            cache_path = os.path.join(os.path.dirname(__file__), "cache")
            if not os.path.exists(cache_path):
                os.mkdir(cache_path)
            with open(cache_file, mode="w", encoding="utf-8") as f:
                json.dump(data, f)
        except (OSError, TypeError) as exception:
            logger.error("Failed to write to cache: %s", exception)
        return data
