from models.user import users
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#Buscar usuario por id
def searchUserById(id: int):
    query = users.select().where(users.c.id == id)
    result = conn.execute(query).first()
    return result

#Buscar usuario por username
def searchUserByUserName(username: str):
    query = users.select().where(users.c.username == username)
    result = conn.execute(query).first()
    print(result)
    return result

def userJSON(username=None, id=None):
    if id != None:
        result = searchUserById(id)
    elif username != None:
        result = searchUserByUserName(username)
    
    user = {
        "id": result[0],
        "name": result[1],
        "username": result[2],
        "disabled": result[4] != None,
        "role": result[5]
    }
    
    user = jsonable_encoder(user)
    return JSONResponse(content=user)