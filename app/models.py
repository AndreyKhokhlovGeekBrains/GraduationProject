# defining database app
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, ARRAY
from .db import metadata
from datetime import datetime

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32)),
    Column("email", String(128)),
    Column("password", String(255)),
    Column("age", Integer),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean),
    Column("created_at", DateTime, default=datetime.now),
)

positions = Table(
    "positions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128)),
    Column("price", Integer),
    Column("tags", ARRAY),
    Column("created_at", DateTime, default=datetime.now())
)

tokens = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False)
)
