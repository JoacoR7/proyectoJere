from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from services import userService
from schemas import user
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 180
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

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

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

# Verifico que el token otorgado sea correcto o válido (que no haya expirado)
async def auth_user(token: str = Depends(oauth2)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("user")
        if username is None:
            raise exception

    except JWTError:
        raise exception
    
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token vacío")

    return JSONResponse(content=jsonable_encoder(userService.userJSON(username=username)))


async def current_user(user: user.User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")

    return user


