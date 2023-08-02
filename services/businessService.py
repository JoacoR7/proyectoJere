from models.business import business
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#Buscar compañía por id
def searchBusinessById(id: int):
    query = business.select().where(business.c.id == id)
    result = conn.execute(query).first()
    return result

#Buscar compañía por nombre
def searchBusinessByName(name: str):
    query = business.select().where(business.c.name == name)
    result = conn.execute(query).first()
    return result

# Devuelvo un diccionario con los datos de la compañía
def businessJSON(name=None, id=None, result = None):
    if result == None:
        if id != None:
            result = searchBusinessById(id)
        elif name != None:
            result = searchBusinessByName(name)
    
    business = {
        "id": result[0],
        "name": result[1],
        "caseLetter": result[2]
    }
    
    return business