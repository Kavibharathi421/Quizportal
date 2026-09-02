import json
from flask import current_app
try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:
    Redis=None
    class RedisError(Exception):pass
_clients={}
def client():
    if Redis is None:raise RedisError("redis package is not installed")
    url=current_app.config["REDIS_URL"]
    if url not in _clients:_clients[url]=Redis.from_url(url,decode_responses=True,socket_connect_timeout=2,socket_timeout=2,health_check_interval=30)
    return _clients[url]
def available():
    try:return bool(client().ping())
    except RedisError:return False
def set_json(key,value,ttl):
    try:client().setex(key,ttl,json.dumps(value));return True
    except RedisError:return False
def get_json(key):
    try:
        value=client().get(key);return json.loads(value) if value else None
    except (RedisError,ValueError):return None
def acquire_lock(key,ttl=30):
    try:return bool(client().set(key,"1",nx=True,ex=ttl))
    except RedisError:return True
def release_lock(key):
    try:client().delete(key)
    except RedisError:pass
