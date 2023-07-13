from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from configuration.db import meta, engine

company = Table("companies", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("name", String(150), nullable=False))

meta.create_all(engine)
