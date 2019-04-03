# developer: 张聪
# email: 18511123018@163.com

import redis


def get_redis_obj():
    return redis.StrictRedis(host='redis', port=6379, db=15, decode_responses=True)
