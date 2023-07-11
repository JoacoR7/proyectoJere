from models.user import users
from configuration.db import conn

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