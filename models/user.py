from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Enum
from configuration.db import meta, engine

users = Table("users", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("name", String(150), nullable=False),
            Column("username", String(150), nullable=False),
            Column("password", String(150), nullable=False),
            Column("disabled_at", DateTime, nullable=True),
            Column("role", Enum("operator", "admin"), nullable=False))

meta.create_all(engine)
