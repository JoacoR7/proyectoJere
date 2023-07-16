from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.case import case as caseModel
from schemas.case import Case
from sqlalchemy import exc
from services import caseService, userService, companyService, vehicleService

case = APIRouter()

"""
Funciones:
C: createCase
R: readCase
"""

# Crear caso
@case.post("/create")
async def createCase(case: Case, userId: int, companyId: int, vehicleId: int, token: str = Header(None)):
    # Realizo la query para crear el caso con los valores correspondientes
    newCase = caseModel.insert().values(
        user_id=userId,
        company_id=companyId,
        vehicle_id=vehicleId,
        accident_number = case.accident_number,
        created_at=case.created_at,
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
        conn.execute(newCase)
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
    company = companyService.companyJSON(id=result[2])
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
