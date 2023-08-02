from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.case import case as caseModel
from models.caseAccessToken import caseAccessToken as AccessModel
from schemas.case import Case, AccessToken
from sqlalchemy import exc
from services import businessService, caseService, userService, vehicleService
from datetime import datetime

case = APIRouter()

"""
Funciones:
C: createCase
R: readCase
"""

# Crear caso
@case.post("/create")
async def createCase(case: Case):
    # Realizo la query para crear el caso con los valores correspondientes
    createdAt = datetime.now()
    newCase = caseModel.insert().values(
        user_id=case.user_id,
        business_id=case.business_id,
        vehicle_id=case.vehicle_id,
        accident_number = case.accident_number,
        created_at=createdAt,
        finished_at=case.finished_at,
        dropped=case.dropped,
        policy=case.policy,
        insured_name=case.insured_name,
        insured_dni=case.insured_dni,
        insured_phone=case.insured_phone,
        accident_date=case.accident_date,
        accident_place=case.accident_place,
        thef_type=case.thef_type

    )
    try:
        result = conn.execute(newCase)
        caseService.createAccessToken(createdAt, result.lastrowid)
        conn.commit()  # Confirmar la transacción
        return {"message": "Caso creado exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear el caso: {str(e)}"}

# Obtengo la información del caso según su id (y si existe)
@case.get("/{id}")
async def readCase(id: int):
    # Busca un caso por su ID
    result = caseService.searchCaseById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="El caso no existe")
    # Creo un diccionario con los datos del usuario, compañía y vehículo correspondiente
    user = userService.userJSON(id=result[1])
    company = businessService.companyJSON(id=result[2])
    vehicle = vehicleService.vehicleJSON(id=result[3])
    data = {
        "id": result[0],
        "user": user,
        "business": company,
        "vehicle": vehicle,
        "accident_number": result[4],
        "created_at": result[5],
        "finished_at": result[6],
        "dropped": result[7],
        "policy": result[8],
        "insured_name": result[9],
        "insured_dni": result[10],
        "insured_phone": result[11],
        "accident_date": result[12],
        "accident_place": result[13],
        "theft_type": result[14]
    }
    # Convierte el diccionario en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

# Borrar caso
@case.delete("/{id}", name="Borrar caso")
async def deleteCase(id: int):
    result = caseService.searchCaseById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="Caso no encontrado")
    try:
        query = caseModel.delete().where(caseModel.c.id == id)
        result = conn.execute(query)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error al eliminar el caso")
    conn.commit()
    return {"message": "Caso eliminado exitosamente"}


@case.put("/dropCase/{id}", name="Tirar caso")
async def changeCompanyName(id: int):
    result = caseService.searchCaseById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")
    try:
        query = caseModel.update().where(caseModel.c.id == id).values(dropped=True)
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Caso abandonado exitosamente"} 

@case.post("/validate")
async def validateToken(caseAccess: AccessToken):
    case, response = caseService.verifyAccessToken(caseAccess.case_access_token)
    if case == None:
        return response
    """query = AccessModel.select().where(AccessModel.c.access_token == caseAccess.case_access_token)
    result = conn.execute(query).first()"""
    if str(case.get("caseId")) != caseAccess.case_id:
        content = {"is_valid": False, "detail": "Token válido, pero id de caso no coincide"}
        status_code=status.HTTP_200_OK
        response = JSONResponse(content=content, status_code=status_code)
    else:
        content = {"is_valid": True, "detail": "Token válido"}
        status_code=status.HTTP_200_OK
        response = JSONResponse(content=content, status_code=status_code)
    return response