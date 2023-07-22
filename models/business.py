from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Text
from configuration.db import meta, engine

business = Table("business", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("name", String(150), nullable=False),
            Column("case_dropped_letter", Text, nullable=False))

meta.create_all(engine)
