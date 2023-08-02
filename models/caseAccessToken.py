from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from configuration.db import meta, engine

caseAccessToken = Table("case_access_token", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("access_token", String(150), nullable=False),
            Column("due_date", DateTime, nullable=False))

meta.create_all(engine)
