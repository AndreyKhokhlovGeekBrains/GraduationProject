# database configuration
import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from app.models import metadata, engine
from app.models import database_url

# DATABASE_URL = "sqlite:///mydatabase.db"


database = databases.Database(database_url)
metadata = metadata
engine = engine

async def connect_db():
    await database.connect()


async def disconnect_db():
    await database.disconnect()
