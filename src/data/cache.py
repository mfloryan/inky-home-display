import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__datetime__": True, "as_str": obj.isoformat()}
        return super().default(obj)


def datetime_decoder(dct):
    if dct.get("__datetime__"):
        return datetime.fromisoformat(dct["as_str"])
    return dct


def cache(cache_key, operation):
    cache_file = os.path.join(os.path.dirname(__file__), "cache", cache_key + ".json")
    try:
        with open(cache_file, "r") as f:
            return json.load(f, object_hook=datetime_decoder)
    except (FileNotFoundError, EOFError, json.JSONDecodeError):
        data = operation()

        # Skip saving empty arrays to disk
        if data == []:
            return data

        try:
            cache_path = os.path.dirname(cache_file)
            if not os.path.exists(cache_path):
                os.makedirs(cache_path, exist_ok=True)
            with open(cache_file, mode="w") as f:
                json.dump(data, f, cls=DateTimeEncoder)
        except Exception as exception:
            logger.error("Failed to write to cache: %s", exception)
        return data
