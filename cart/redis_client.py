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


def redis_add_to_cart(user_id, position_id, amount):
    if client.exists(user_id):
        key_type = client.type(user_id)
        if key_type == b'list':
            client.rpush(user_id, position_id)
        elif key_type == b'hash':
            client.hincrby(user_id, position_id, amount=amount)
            return {"status": 200}
    else:
        client.hincrby(user_id, position_id, amount=amount)

        return {"status": 200}

    return {"status": 401}


def redis_remove_from_cart(user_id, position_id, amount):
    if client.exists(user_id):
        key_type = client.type(user_id)
        if key_type == b'hash':
            current_amount = client.hget(user_id, position_id)
            if current_amount is not None:
                new_amount = int(current_amount) - amount
                if new_amount <= 0:
                    client.hdel(user_id, position_id)
                else:
                    client.hincrby(user_id, position_id, amount=-amount)

            return {"status": 200}

    return {"status": 401}


def redis_get_from_cart(user_id: int):
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


def redis_clear_cart(user_email):
    if client.exists(user_email):
        client.delete(user_email)

    return True

def redis_get_unique_item(user_id: int) -> int:
    """
        Returns the number of unique items in a user's cart stored in Redis.

        :param user_id: The ID of the user
        :return: The number of unique items in the user's cart
    """
    # Get the hash of items in the user's cart
    try:
        cart_hash = client.hgetall(user_id)

        # Convert the hash to a set to remove duplicates
        unique_items = set(cart_hash.values())

        # Return the number of unique items
        return len(unique_items)
    except Exception as e:
        print(e)

    return 0
