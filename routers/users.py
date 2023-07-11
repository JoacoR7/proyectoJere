from fastapi import APIRouter, HTTPException, status, Depends, Header
from configuration.db import conn
from models.user import users
from schemas.user import User
from sqlalchemy import exc
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from services import authService, userService
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

user = APIRouter()
crypt = CryptContext(schemes=["bcrypt"])

#Obtener listado de usuarios de la db
@user.get("/users")
async def getUsers(): 
    result = conn.execute(users.select()).fetchall()
    if not result:
        return JSONResponse(content=[], status_code=204)
    data = []
    for user in result:
        newUser = {
            "id": user[0],
            "name": user[1],
            "username": user[2],
            "role": user[5]
        }
        data.append(newUser)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

#Obtener un usuario por path ".../user/id"
@user.get("/users/{id}")
async def getUserById(id: int):
    result = userService.searchUserById(id)
    if not result:
        raise HTTPException(status_code=204)
    data = {
        "id": result[0],
        "name": result[1],
        "username": result[2],
        "role": result[5]
    }
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

#Borrar usuario
@user.delete("/users/{id}")
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

#Registrar usuario

@user.post("/register")
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


#Login de usuario ".../login"
#form: x-www-form-urlencoded en postman
#username: xxx
#password: xxx
@user.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = userService.searchUserByUserName(form.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    return authService.accesToken(user.username)

oauth2_scheme = HTTPBearer()

@user.get("/users/me")
async def me(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    user_data = authService.auth_user(credentials.credentials)
    return user_data