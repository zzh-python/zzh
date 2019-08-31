# -*- coding: utf-8 -*-

import redis

#保存到redis
def save_to_redis(mess):
    redis_cli1 =redis.StrictRedis(
        host='192.168.1.3',
        port=6379,
        db=1,
        password='zzhabc123'
    )
    redis_cli2 =redis.StrictRedis(
        host='192.168.1.3',
        port=6379,
        db=2,
        password='zzhabc123'
    )
    redis_cli1.lpush('fly',mess)
    # self.redis_cli2.lpush('pay', list
