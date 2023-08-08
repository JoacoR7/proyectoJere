from fastapi import APIRouter, HTTPException, status, Depends, Header, Request
from configuration.db import conn
from models.user import users
from schemas.user import User, UserLogin, UserUpdate
from sqlalchemy import exc
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from services import authService, userService
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from utils import customResponses

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
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya existe")
    hashedPassword = authService.hashPass(user.password)
    new_user = users.insert().values(
        name=user.name,
        username=user.username,
        password=hashedPassword,
        role=user.role
    )
    try:
        conn.execute(new_user)
        conn.commit()  # Confirmar la transacción
        return customResponses.JsonEmitter.response(status.HTTP_201_CREATED, detail="Usuario creado exitosamente")
    except exc.DataError as exception:
        conn.rollback()
        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: rol incorrecto", exception=exception)
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al registrar usuario", exception=e)
    
# Obtener listado de usuarios de la db
@user.get("", name="Obtener todos los usuarios de la bd")
async def getUsers(request: Request):
    # Verifico si el usuario que quiere realizar la operación es administrador
    await authService.verifyAdmin(request) 
    # Obtengo todos los registros de la tabla "users" de la bd
    result = conn.execute(users.select()).fetchall()
    if result:
        # Si no se encuentran usuarios, devuelve una respuesta vacía con el código de estado 204
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, content={})
    # En la lista data acumulo todos los usuarios en forma de diccionario
    data = []
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
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

# Obtener un usuario por path ".../user/id"
@user.get("/get/{id}", name="Obtener un usuario por su id")
async def getUser(id: int, request: Request):
    # Verifico si el usuario que quiere realizar la operación es administrador
    response = await authService.verifyAdmin(request)
    if response:
        return response
    # Busca un usuario por su ID
    result = userService.searchUserById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")

    # Creo un diccionario con los datos del usuario encontrado
    data = {
        "id": result[0],
        "name": result[1],
        "username": result[2],
        "disabled": result[4] != None,
        "role": result[5]
    }
    # Convierte el diccionario en formato JSON
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

# Obtengo los datos del usuario 
@user.get("/me", name="Perfil usuario")
async def me(request: Request):
    return await authService.current_user(request)

@user.patch("/disable/{id}", name="Deshabilitar usuario")
async def disableUser(id: int, request: Request):
    # Verifico si el usuario que quiere realizar la operación es administrador
    await authService.verifyAdmin(request)
    # Busca un usuario por su ID
    result = userService.searchUserById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")
    try:
        query = users.update().where(users.c.id == id).values(disabled_at=datetime.now())
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Usuario deshabilitado exitosamente"}

@user.patch("/enable/{id}", name="Habilitar usuario")
async def enableUser(id: int, request: Request):
    # Verifico si el usuario que quiere realizar la operación es administrador
    await authService.verifyAdmin(request)
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

# Login de usuario
@user.post("/login", name="Login usuario")
async def login(user: UserLogin):
    # Busco el usuario
    userDB = userService.searchUserByUserName(user.username)
    # Si no existe, devuelvo error
    if not userDB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    # Si existe, pero la contraseña es incorrecta, devuelvo error
    if not crypt.verify(user.password, userDB.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
    
    # Si existe, y la contraseña es correcta, devuelvo el token que 
    # tendrá la info del nombre de usuario, rol, id y expiración
    access_token  = authService.accesToken(userDB.username, userDB.role, userDB.id)
    return {"access_token": access_token, "token_type": "bearer"}

@user.patch("/update/{id}")
async def updateUser(id, userUpdate: UserUpdate, request: Request):
    usuario = userService.searchUserById(id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    updateData = {}
    if userUpdate.name != None:
        updateData["name"] = userUpdate.name
    if userUpdate.username != None:
        userDB = userService.searchUserByUserName(userUpdate.username)
        if userDB != None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya se encuentra en uso")
        updateData["username"] = userUpdate.username
    if userUpdate.password != None:
        newPass = authService.hashPass(userUpdate.password)
        updateData["password"] = newPass
    if userUpdate.role != None:
        await authService.verifyAdmin(request)
        if userUpdate.role != "admin" and userUpdate.role != "operator":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol incorrecto")
        updateData["role"] = userUpdate.role
    
    try:
        query = users.update().where(users.c.id == id).values(**updateData)
        conn.execute(query)
        conn.commit()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return {"message": "Usuario actualizado exitosamente"}
    
        
        

