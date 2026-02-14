"""
Caching utilities with automatic key prefixing and cache invalidation.
Implements the Caching system design principle.
"""
import functools
import hashlib
import logging

from django.core.cache import cache

logger = logging.getLogger("befa.cache")

CACHE_TTL = {
    "short": 60,           # 1 min — volatile data
    "medium": 60 * 15,     # 15 min — default
    "long": 60 * 60,       # 1 hour — stable data
    "day": 60 * 60 * 24,   # 24 hours — rarely changes
}


def cache_key(*parts):
    """Generate a namespaced cache key."""
    return "befa:" + ":".join(str(p) for p in parts)


def cached_view(key_func, timeout=CACHE_TTL["medium"]):
    """
    Decorator for DRF views. Caches successful GET responses.
    key_func: callable(view_instance, request) -> str
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(view_instance, request, *args, **kwargs):
            if request.method != "GET":
                return method(view_instance, request, *args, **kwargs)
            try:
                key = key_func(view_instance, request)
                cached_data = cache.get(key)
                if cached_data is not None:
                    logger.debug("Cache HIT: %s", key)
                    from rest_framework.response import Response
                    return Response(cached_data)
                logger.debug("Cache MISS: %s", key)
                response = method(view_instance, request, *args, **kwargs)
                if response.status_code < 400:
                    cache.set(key, response.data, timeout=timeout)
                return response
            except Exception:
                logger.exception("Cache error, falling through")
                return method(view_instance, request, *args, **kwargs)
        return wrapper
    return decorator


def invalidate(*keys):
    """Delete one or more cache keys."""
    for key in keys:
        cache.delete(key)
        logger.debug("Cache INVALIDATED: %s", key)


def invalidate_pattern(prefix):
    """
    Invalidate all known keys starting with prefix.
    Note: LocMemCache doesn't support pattern delete, so we track known keys.
    For Redis in prod, use cache.delete_pattern().
    """
    try:
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{prefix}*")
        else:
            # Fallback: delete known keys
            known = cache.get("befa:known_keys", set())
            to_delete = {k for k in known if k.startswith(prefix)}
            for k in to_delete:
                cache.delete(k)
            cache.set("befa:known_keys", known - to_delete)
    except Exception:
        logger.exception("Pattern invalidation failed")
