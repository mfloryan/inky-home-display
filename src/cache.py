import os
import io
import json

def cache(cache_key, operation):
    cache_file = os.path.join(os.path.dirname(__file__), 'cache', cache_key+".json")
    try:
        with open(cache_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        data = operation()
        try:
            cache_path = os.path.join(os.path.dirname(__file__), 'cache')
            if (not os.path.exists(cache_path)):
                os.mkdir(cache_path)
            with open(cache_file,mode='w') as f:
                json.dump(data, f)
        except Exception as e:
            print(e)
            # print("Unable to save cache",e)
        return data
