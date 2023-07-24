from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import env

# Generar la cadena de conexión usando las variables de entorno definidas en env.py
db_url = f"mysql+pymysql://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"

# Crear el motor de la base de datos
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
conn = SessionLocal()
meta = MetaData()


