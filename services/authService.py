from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from services import userService
from schemas import user
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from utils import customResponses


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 120
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])
security = HTTPBearer()

# Encripto la contraseña
def hashPass(password: str):
    hashedPass = crypt.hash(password)
    return hashedPass

# Al loguearse de forma exitosa, creo un token donde guardo el nombre de usuario,
# la fecha de expiración, el rol y el id
def accesToken(username: str, role: str, id: int):
    access_token = {"user": username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
                    "role": role, 
                    "id": id}

    return jwt.encode(access_token, SECRET, algorithm=ALGORITHM)

# Verifico que el token otorgado sea correcto o válido (que no haya expirado)
async def auth_user(request: Request):
    try:
        _, token = request.headers.get("Authorization").split()
    except AttributeError:
        response = customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail = "Token vacío")
        return None, response
    
    response = customResponses.JsonEmitter.response(status.HTTP_401_UNAUTHORIZED, detail = "Credenciales de autenticación inválidas")

    try:
        user = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if user is None:
            return None, response

    except JWTError:
        return None, response

    return user, None

async def current_user(request):
    id = request.state.user.get("id")
    userDB = userService.searchUserById(id)
    if userDB[4] != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    content = {
        "name": userDB[1],
        "username": userDB[2],
        "role": userDB[5]
    }
    response = customResponses.JsonEmitter.response(status.HTTP_200_OK, content=content)
    return response

async def verifyAdmin(request):
    role = request.state.user.get("role")
    if role != "admin":
        return customResponses.JsonEmitter.response(status.HTTP_401_UNAUTHORIZED, detail="No cuentas con los permisos para ejecutar esta acción")

async def isEnabled(request):
    user = userService.searchUserById(request.state.user.get("id"))
    if user[4] != None:
        return customResponses.JsonEmitter.response(status.HTTP_401_UNAUTHORIZED, detail="Usuario deshabilitado")
        

    






