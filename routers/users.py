from fastapi import APIRouter, HTTPException, status, Depends, Header
from configuration.db import conn
from models.user import users
from schemas.user import User
from sqlalchemy import exc
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from services import authService, userService
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime

user = APIRouter()
crypt = CryptContext(schemes=["bcrypt"])

"""
Funciones:
C: createUser
R: getUsers (obtengo todos los usuarios) - getUser (obtengo un usuario por su id)
U: disableUser - enableUser
D: deleteUser
"""

# Registrar usuario
@user.post("/register", name="Registrar nuevo usuario")
async def createUser(user: User):
    findUser = userService.searchUserByUserName(user.username)
    if findUser:
        return {"message": "El nombre de usuario ya existe"}
    hashedPassword = authService.hashPass(user.password)
    new_user = users.insert().values(
        name=user.name,
        username=user.username,
        password=hashedPassword,
        disabled_at=None,
        role=user.role
    )
    try:
        result = conn.execute(new_user)
        conn.commit()  # Confirmar la transacción
        print(result.lastrowid)
        return {"message": "Usuario creado exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear el usuario: {str(e)}"}

# Obtener listado de usuarios de la db
@user.get("", name="Obtener todos los usuarios de la bd")
async def getUsers(): 
    # Obtengo todos los registros de la tabla "users" de la bd
    result = conn.execute(users.select()).fetchall()
    if not result:
        # Si no se encuentran usuarios, devuelve una respuesta vacía con el código de estado 204
        return JSONResponse(content=[], status_code=204)
    data = []
    # En la lista data acumulo todos los usuarios en forma de diccionario
    for user in result:
        newUser = {
            "id": user[0],
            "name": user[1],
            "username": user[2],
            "disabled": user[4] != None,
            "role": user[5]
        }
        data.append(newUser)
    # Convierte la lista de diccionarios en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

# Obtener un usuario por path ".../user/id"
@user.get("/{id}", name="Obtener un usuario por su id")
async def getUser(id: int):
    # Busca un usuario por su ID
    result = userService.searchUserById(id)
    if not result:
        raise HTTPException(status_code=204)
    # Creo un diccionario con los datos del usuario encontrado
    data = {
        "id": result[0],
        "name": result[1],
        "username": result[2],
        "disabled": result[4] != None,
        "role": result[5]
    }
    # Convierte el diccionario en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

# Obtengo los datos del usuario 
@user.post("/me", name="Perfil usuario")
async def me(token: str = Header(None)):
    return await authService.auth_user(token)

@user.put("/disable/{id}", name="Deshabilitar usuario")
async def disableUser(id: int):
    # Busca un usuario por su ID
    result = userService.searchUserById(id)
    if not result:
        # Si no se encuentra ningún usuario, se lanza una excepción HTTP con el código de estado 204
        return {"message": "Usuario no encontrado"}
    try:
        query = users.update().where(users.c.id == id).values(disabled_at=datetime.now())
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Usuario deshabilitado exitosamente"}

@user.put("/enable/{id}", name="Habilitar usuario")
async def enableUser(id: int):
    result = userService.searchUserById(id)
    if not result:
        return {"message": "Usuario no encontrado"}
    try:
        query = users.update().where(users.c.id == id).values(disabled_at=None)
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Usuario habilitado exitosamente"}

# Borrar usuario
@user.delete("/{id}", name="Borrar usuario")
async def deleteUser(id: int):
    result = userService.searchUserById(id)
    if not result:
        return {"message": "Usuario no encontrado"}
    try:
        query = users.delete().where(users.c.id == id)
        result = conn.execute(query)
    except:
        raise HTTPException(status_code=404)
    conn.commit()
    return {"message": "Usuario eliminado exitosamente"}

# Login de usuario
@user.post("/login", name="Login usuario")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Busco el usuario
    user = userService.searchUserByUserName(form.username)
    # Si no existe, devuelvo error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    # Si existe, pero la contraseña es incorrecta, devuelvo error
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    # Si existe, y la contraseña es correcta, devuelvo el token que 
    # tendrá la info del nombre de usuario, rol, id y expiración
    return authService.accesToken(user.username, user.role, user.id)




