import redis
from common.common import config

redis_config = config.load_redis_config()
redis_pool = redis.ConnectionPool(host=redis_config["host"])
client = redis.StrictRedis(connection_pool=redis_pool)
timeout = redis_config["timeout"] / 1000
base_expire = 30 * 60
bitmap_key = "fid"
lock_expired = 10


def rpush(key, value):
    client.rpush(key, value)


def lpop(key):
    return client.lpop(key)


def get_bitmap(key, offset):
    return client.getbit(key, offset)


def set_bitmap(key, offset):
    return client.setbit(key, offset, 1)


def blpop(key):
    return client.blpop(key, timeout)
