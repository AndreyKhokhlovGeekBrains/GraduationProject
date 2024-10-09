# database operations

from .models import User, Car, Token
from .db import database


async def create_user(user_in):
    query = users.insert().values(**user_in.dict(exclude={"created_at"}))
    last_record_id = await database.execute(query)
    return {**user_in.dict(), "id": last_record_id}


async def get_users(skip: int = 0, limit: int = 10):
    query = User.select().offset(skip).limit(limit)
    return await database.fetch_all(query)


async def get_user_by_login_data(email: str, password: str):
    query = User.select().where(users.c.email == email).where(users.c.password == password)
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    query = User.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: int, new_user):
    query = User.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


async def delete_user(user_id: int):
    query = User.delete().where(users.c.id == user_id)
    await database.execute(query)
    
async def create_position(position_in):
    query = Car.insert().values(**position_in.dict(exclude={"created_at"}))
    await database.execute(query)

async def get_positions(skip: int = 0, limit: int = 10):
    query = positions.select().offset(skip).limit(limit)
    return await Car.fetch_all(query)

async def get_position_by_id(position_id: int):
    query = Car.select().where(positions.c.id == position_id)
    return await database.fetch_one(query)

async def add_token_to_blacklist(token_in):
    query = Token.insert().values(**token_in.dict())
    await database.execute(query)

async def get_token(token):
    query = Token.select().where(positions.c.token == token)
    await  database.fetch_one(query)
