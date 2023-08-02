from models.case import case
from models.caseAccessToken import caseAccessToken as caseAccessModel
from configuration.db import conn
from datetime import timedelta
from jose import jwt, JWTError
from sqlalchemy import exc
from fastapi import status
from fastapi.responses import JSONResponse

ALGORITHM = "HS256"
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

# Buscar compañía por id
def searchCaseById(id: int):
    query = case.select().where(case.c.id == id)
    result = conn.execute(query).first()
    return result

def createAccessToken(creationDate, caseId):
    
    exp = creationDate + timedelta(minutes=1440)
    access_token = {"caseId": caseId,
                    "exp": exp}
    access_token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    query = caseAccessModel.insert().values(
        access_token = access_token,
        due_date = exp 
    )
    try:
        conn.execute(query)
        conn.commit()  # Confirmar la transacción
        return 
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear el token: {str(e)}"}
    
def verifyAccessToken(accessToken):
    content = {"is_valid": False, "detail": "Token vencido"}
    status_code=status.HTTP_200_OK
    response = JSONResponse(content=content, status_code=status_code)

    try:
        case = jwt.decode(accessToken, SECRET, algorithms=[ALGORITHM])
        if case is None:
            return None, response

    except JWTError:
        return None, response
    
    return case, None