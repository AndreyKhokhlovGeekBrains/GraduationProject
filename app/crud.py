# database operations
from .models import users
from .db import database


async def create_user(user_in):
    query = users.insert().values(**user_in.dict(exclude={"created_at"}))
    last_record_id = await database.execute(query)
    return {**user_in.dict(), "id": last_record_id}


async def get_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_user(**values):
    try:
        query = users.select().where(**values)
        return await database.fetch_one(query)
    except Exception as e:
        # Handle the error, e.g., log the error or return a default value
        print(f"Error fetching user: {e}")
        return None


async def get_user_by_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: int, new_user):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
