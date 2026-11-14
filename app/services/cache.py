import json
from redis import Redis
from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

def cache_get(key: str):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def cache_set(key: str, value, ttl: int | None = None):
    redis_client.setex(key, ttl or settings.cache_ttl_seconds, json.dumps(value, default=str))

def invalidate_search_cache():
    for key in redis_client.scan_iter("search:*", count=200):
        redis_client.delete(key)
