# defining database app
# models.py

from sqlalchemy import Table, Column, Integer, String, Boolean, Date, DateTime, JSON, func
from .db import metadata
from datetime import datetime

User = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32)),
    Column("email", String(128), nullable=False),
    Column("password", String(255), nullable=False),
    Column("birthdate", Date),
    Column("phone", String(20)),
    Column("agreement", Boolean, default=False),
    Column("created_at", DateTime, server_default=func.now()),
)

Cloth = Table(
    "Cloths",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128), nullable=False),
    Column("price", Integer, nullable=False),
    Column("tags", JSON, nullable=False),
    Column("created_at", DateTime, server_default=func.now())
)

Token = Table(
    "tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, nullable=False, unique=False)
)
