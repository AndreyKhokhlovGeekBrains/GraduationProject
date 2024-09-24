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


def add_to_cart(user_id, position_id):
    client.set(user_id, position_id)


def get_from_cart(user_id):
    if client.exists(user_id):
        values = client.smembers(user_id)

        return [value.decode('utf-8') for value in values]

    else:
        return None
