from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.case import case as caseModel
from models.caseAccessToken import caseAccessToken as AccessModel
from schemas.case import Case, AccessToken, AccessTokenModify, CaseModify
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
    company = businessService.businessJSON(id=result[2])
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

@case.post("/expire")
async def modifyAccessToken(accessToken: AccessTokenModify):
    case = caseService.searchAccessToken(accessToken.case_access_token)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token de acceso no encontrado")
    access_token, exp = caseService.generateToken(datetime.now(), case[0], accessToken.hour_from_now*60)
    updateData = {
        "access_token": access_token,
        "due_date": exp
    }
    try:
        query = AccessModel.update().where(AccessModel.c.access_token == accessToken.case_access_token).values(**updateData)
        conn.execute(query)
        conn.commit()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return {"message": "Token actualizado exitosamente"}

@case.patch("/update/{id}")
async def modifyCase(case: CaseModify, id: int):
    caseToUpdate = caseService.searchCaseById(id)
    if not caseToUpdate:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="El caso no existe")
    updateData = {}
    if case.user_id != None:
        updateData["user_id"] = case.user_id
    if case.business_id != None:
        updateData["business_id"] = case.business_id
    if case.vehicle_id != None:
        updateData["vehicle_id"] = case.vehicle_id
    if case.accident_number != None:
        updateData["accident_number"] = case.accident_number
    if case.finished_at != None:
        updateData["finished_at"] = case.finished_at
    if case.dropped != None:
        updateData["dropped"] = case.dropped
    if case.policy != None:
        updateData["policy"] = case.policy
    if case.insured_name != None:
        updateData["insured_name"] = case.insured_name
    if case.insured_dni != None:
        updateData["insured_dni"] = case.insured_dni
    if case.insured_phone != None:
        updateData["insured_phone"] = case.insured_phone
    if case.accident_date != None:
        updateData["accident_date"] = case.accident_date
    if case.accident_place != None:
        updateData["accident_place"] = case.accident_place
    if case.thef_type != None:
        thefType = ["partial", "inner", "outside"]
        if case.thef_type not in thefType:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de robo incorrecto")
        updateData["thef_type"] = case.thef_type
    try:
        query = caseModel.update().where(caseModel.c.id == id).values(**updateData)
        conn.execute(query)
        conn.commit()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return {"message": "Caso actualizado exitosamente"}
