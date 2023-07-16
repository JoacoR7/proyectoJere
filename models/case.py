from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime, Enum, Boolean, String
from configuration.db import meta, engine

case = Table("cases", meta, 
            Column("id", Integer, primary_key=True, autoincrement=True, nullable= False),
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            Column("company_id", Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
            Column("vehicle_id", Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
            Column("accident_number", Integer, nullable=False),
            Column("created_at", DateTime, nullable=False),
            Column("finished_at", DateTime, nullable=True),
            Column("dropped", Boolean, nullable=True),
            Column("policy", String(150), nullable=True),
            Column("insured_name", String(150), nullable=True),
            Column("insured_dni", String(150), nullable=True),
            Column("insured_phone", String(150), nullable=False),
            Column("accident_date", DateTime, nullable=True),
            Column("accident_place", String(150), nullable=True),
            Column("thef_type", Enum("partial", "inner", "outside"), nullable=True))

meta.create_all(engine)