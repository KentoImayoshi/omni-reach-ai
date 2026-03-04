from django.core.cache import cache
from django.conf import settings


def get_or_set_cache(key: str, func):
    """
    Get value from cache or execute function and store result.
    """
    data = cache.get(key)

    if data is None:
        data = func()
        cache.set(key, data, settings.CACHE_TTL)

    return data