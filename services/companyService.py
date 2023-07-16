from models.company import company
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#Buscar compañía por id
def searchCompanyById(id: int):
    query = company.select().where(company.c.id == id)
    result = conn.execute(query).first()
    return result

#Buscar compañía por nombre
def searchCompanyByName(name: str):
    query = company.select().where(company.c.name == name)
    result = conn.execute(query).first()
    return result

# Devuelvo un diccionario con los datos de la compañía
def companyJSON(name=None, id=None, result = None):
    if result == None:
        if id != None:
            result = searchCompanyById(id)
        elif name != None:
            result = searchCompanyByName(name)
    
    company = {
        "id": result[0],
        "name": result[1]
    }
    
    return company