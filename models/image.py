from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, BLOB, Boolean
from configuration.db import meta, engine

image = Table("case_photo", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("photo", BLOB, nullable=False),
            Column("case_id", Integer, nullable=False),
            Column("validated", Boolean, nullable=False),
            Column("validation_attemps", Integer, nullable=False))

meta.create_all(engine)
