import redis
from config.consul import read_config_by_key

_redis_config = read_config_by_key('redis')
_prefix = _redis_config['prefix']

_redis = redis.Redis(host=_redis_config['host'], port=_redis_config['port'],
                     password=_redis_config['password'], db=_redis_config['db'],)


def setex(key: str, val: str, ex: float | None):
    '''ex表示过期秒数'''
    key = _prefix+key
    _redis.set(key, val, ex=ex)


def ttl(key: str) -> int:
    '''获取过期时间'''
    key = _prefix+key
    return _redis.ttl(key)
