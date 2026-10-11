from time import time

_cache = {}

CACHE_TIME = 300


def get(key):

    if key not in _cache:
        return None

    value, created = _cache[key]

    if time() - created > CACHE_TIME:
        del _cache[key]
        return None

    return value


def set(key, value):

    _cache[key] = (
        value,
        time()
    )


def clear():

    _cache.clear()