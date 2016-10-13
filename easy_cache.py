import json
import time
import os

def persist_to_file(file_name, cache_expired_in):
    def decorator(original_func):

        try:
            cache = json.load(open(file_name, 'r'))
        except (IOError, ValueError, TypeError):
            cache = {}

        def new_func(param):
            if param in cache:
                if time.time() - cache[param][1] < cache_expired_in:
                    return cache[param][0]
            cache[param] = [original_func(param), time.time()]
            json.dump(cache, open(file_name, 'w'))
            size = os.path.getsize(file_name)
            if size > 7.5e+7:  #limit cache file to 75 mega
                open(file_name, 'w').close()
            return cache[param][0]

        return new_func
    return decorator
