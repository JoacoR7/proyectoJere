from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, BLOB, Boolean, String
from configuration.db import meta, engine

image = Table("case_photo", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("photo", BLOB(length=429496729), nullable=False),
            Column("case_id", Integer, nullable=False),
            Column("type", String(150), nullable=False),
            Column("validated", Boolean, nullable=False),
            Column("validation_attemps", Integer, nullable=False),
            Column("metadata", String(150), nullable=True))

meta.create_all(engine)
