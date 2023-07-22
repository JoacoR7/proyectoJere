from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.case import case as caseModel
from schemas.case import Case
from sqlalchemy import exc
from services import businessService, caseService, userService, vehicleService

case = APIRouter()

"""
Funciones:
C: createCase
R: readCase
"""

# Crear caso
@case.post("/create")
async def createCase(case: Case, userId: int, businessId: int, vehicleId: int, token: str = Header(None)):
    # Realizo la query para crear el caso con los valores correspondientes
    newCase = caseModel.insert().values(
        user_id=userId,
        business_id=businessId,
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