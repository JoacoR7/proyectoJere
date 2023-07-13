from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from services import userService
from schemas import user


ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 180
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])


def hashPass(password: str):
    hashedPass = crypt.hash(password)
    return hashedPass

def accesToken(username: str, role: str):
    access_token = {"user": username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
                    "role": role}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

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

    user = userService.userJSON(username=username)

    return user


async def current_user(user: user.User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")

    return user


