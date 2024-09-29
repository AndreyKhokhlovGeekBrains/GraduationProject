import redis
import schedule
import time


"""
Создаем Redis клиент, хост - localhost,
порт  - 6379, это стандартный порт для Redis, мы указали его в docker-compose,
db - это номер базы данных, мы можем указать любой
"""

client = redis.Redis(host='localhost', port=6379, db=0)


def redis_backup():
    """
    Создаем бэкап
    """
    schedule.every(1).day.at("02:00").do(client.bgsave())

    while True:
        schedule.run_pending()
        time.sleep(1)


def redis_add_to_cart(user_id, position_id):
    if client.exists(user_id):
        key_type = client.type(user_id)
        if key_type == b'list':
            client.rpush(user_id, position_id)
        elif key_type == b'hash':
            client.hincrby(user_id, position_id, 1)
    else:
        client.hincrby(user_id, position_id, 1)
    return {"status": 200}



def redis_get_from_cart(user_id):
    values = None
    if client.exists(user_id):
        key_type = client.type(user_id)
        if key_type == b'list':
            values = client.lrange(user_id, 0, -1)
        elif key_type == b'hash':
            values = client.hgetall(user_id)
            # Decode the bytes objects to strings
            values = {key.decode('utf-8'): value.decode('utf-8') for key, value in values.items()}
    else:
        values = None  # Define the values variable in the else block
    return values


def redis_clear_cart(user_id):
    if client.exists(user_id):
        client.delete(user_id)
    return True
