# utils/cache.py
from django.core.cache import cache
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def cached_response(cache_key_func, timeout=60 * 15, cache_none=True):
    def decorator(view_method):
        def wrapper(view_instance, request, *args, **kwargs):
            try:
                # Get cache key dynamically
                cache_key = (
                    cache_key_func(view_instance, request, *args, **kwargs)
                    if callable(cache_key_func)
                    else cache_key_func
                )

                # Try to get from cache
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return Response(cached_data)

                # Call the original view method
                response = view_method(view_instance, request, *args, **kwargs)

                # Only cache successful responses (status < 400)
                if response.status_code < 400:
                    data = response.data
                    # Optionally avoid caching empty lists or null
                    if cache_none or data not in [None, [], {}, ""]:
                        cache.set(cache_key, data, timeout=timeout)

                return Response(data) if response.status_code < 400 else response

            except Exception as e:
                logger.error(f"Cache decorator error: {e}", exc_info=True)
                return view_method(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator