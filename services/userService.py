from models.user import users
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Header

#Buscar usuario por id
def searchUserById(id: int):
    query = users.select().where(users.c.id == id)
    result = conn.execute(query).first()
    return result

#Buscar usuario por username
def searchUserByUserName(username: str):
    query = users.select().where(users.c.username == username)
    result = conn.execute(query).first()
    return result

# Devuelvo un diccionario con los datos del usuario
def userJSON(username=None, id=None, result = None):
    if result == None:
        if id != None:
            result = searchUserById(id)
        elif username != None:
            result = searchUserByUserName(username)
    
    user = {
        "id": result[0],
        "name": result[1]
        #"username": result[2],
        #"disabled": result[4] != None,
        #"role": result[5]
    }
    return user
