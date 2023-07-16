from models.case import case
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Buscar compañía por id
def searchCaseById(id: int):
    query = case.select().where(case.c.id == id)
    result = conn.execute(query).first()
    return result
