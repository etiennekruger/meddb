from backend import logger, app, db
from redis import Redis
import time
from datetime import datetime
import json
from redis.exceptions import ConnectionError

redis = Redis()


def store(key, str_in):
    """
    Store a record in the cache.
    """
    now = int(time.time())
    expires = now + (60 * 60 * 24 * 7)
    try:
        p = redis.pipeline()
        p.set(key, str_in)
        p.expireat(key, expires)
        p.execute()
    except ConnectionError:
        # fall back to filesystem, if Redis is not available
        with open('/tmp/med-db.cache', 'w+') as f:
            try:
                cache = json.loads(f.read())
            except Exception:
                cache = {}
            cache[key] = str_in
            f.seek(0)
            f.write(json.dumps(cache))
            f.truncate()
        pass


def log(key, str_in):
    """
    Add a record to a set in the cache.
    """
    now = int(time.time())
    expires = now + (5 * 60)
    try:
        p = redis.pipeline()
        p.sadd(key, str_in)
        p.expireat(key, expires)
        p.execute()
    except ConnectionError:
        # fall back to filesystem, if Redis is not available
        with open('/tmp/med-db.cache', 'w+') as f:
            try:
                cache = json.loads(f.read())
            except Exception:
                cache = {}
            if not cache.get(key):
                cache[key] = []
            cache[key].append(str_in)
            f.seek(0)
            f.write(json.dumps(cache))
            f.truncate()
        pass


def retrieve(key):
    try:
        return redis.get(key)
    except ConnectionError:
        # fall back to filesystem, if Redis is not available
        with open('/tmp/med-db.cache', 'r') as f:
            try:
                cache = json.loads(f.read())
            except Exception:
                cache = {}
            if cache.get(key):
                return cache[key]
        pass
    return None