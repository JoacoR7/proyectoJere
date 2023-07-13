from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from configuration.db import meta, engine

vehicle = Table("vehicles", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("brand", String(150), nullable=False),
            Column("model", String(150), nullable=False),
            Column("licence_plate", String(150), nullable=False))

meta.create_all(engine)
