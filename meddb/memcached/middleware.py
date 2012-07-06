from django.conf import settings
import memcache

nginx_cache = memcache.Client(getattr(settings, 'CACHE_MEMCACHE_SERVERS', ['localhost:11211']), server_max_value_length=1024*1024*4)
is_enabled = getattr(settings, 'CACHE_MEMCACHE', True)

class UpdateCacheMiddleware(object):
    """Updates the cache cache with the response of the request.

    This uses the X-Memcached-Key header from nginx to set the correct key.
    
    The middleware must be at the top of settings.MIDDLEWARE_CLASSES
    to be called last during the response phase.
    """

    def __init__(self):
        """Initialize middleware. Args:
            * cache_timeout - seconds after which the cached response expires
            * anonymous_only - only cache if the user is anonymous
        """
        self.cache_timeout = getattr(settings, 'CACHE_MEMCACHE_TIMEOUT', 3600)
        self.anonymous_only = getattr(settings, 'CACHE_MEMCACHE_ANONYMOUS_OLNY', True)

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if ((not is_enabled) or
            (request.method != 'GET') or 
            (response.status_code != 200)):
            return response
        # Logged in users don't cause caching if anonymous_only is set.
        if self.anonymous_only and request.user.is_authenticated():
            return response
        self.cache_response(request, response)
        return response

    def cache_response(self, request, response):
        """Cache this response for the web server to grab next time."""
        cache_key = request.META.get('X-Memcached-Key', None)
        if cache_key:
            nginx_cache.set(cache_key, response._get_content(), cache_timeout)
