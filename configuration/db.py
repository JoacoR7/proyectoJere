from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+pymysql://root:root@localhost:3306/project")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
conn = SessionLocal()
meta = MetaData()


#TODO: investigar sobre enum en mysql (para roles)

