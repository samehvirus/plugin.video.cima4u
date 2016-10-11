import json
import time

cache_expired_in = 43200  #12 hours


def persist_to_file(file_name):

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
            return cache[param][0]

        return new_func

    return decorator
