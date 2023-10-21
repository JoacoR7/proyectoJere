from fastapi import APIRouter, status, Request
from configuration.db import conn
from models.case import case as caseModel
from models.caseAccessToken import caseAccessToken as AccessModel
from models.image import image
from schemas.case import Case, AccessToken, AccessTokenModify, CaseModify, CaseId
from sqlalchemy import exc, desc
from services import caseService, vehicleService
from datetime import datetime, timedelta
from utils import customResponses

case = APIRouter()

"""
Funciones:
C: createCase
R: readCase
"""

# Crear caso
@case.post("/create")
async def createCase(case: Case, request: Request):
    # Realizo la query para crear el caso con los valores correspondientes
    userId = request.state.user.get("id")
    createdAt = datetime.now()
    vehicleId, response = vehicleService.createVehicle(case.vehicle)
    if not vehicleId:
        return response
    newCase = caseModel.insert().values(
        user_id=userId,
        business_id=case.business_id,
        vehicle_id=vehicleId,
        accident_number = case.accident_number,
        created_at=createdAt,
        finished_at=case.finished_at,
        dropped=case.dropped,
        policy=case.policy,
        insured_name=case.insured_name,
        insured_dni=case.insured_dni,
        insured_phone=case.insured_phone,
        insured_address=case.insured_address,
        accident_date=case.accident_date,
        accident_place=case.accident_place,
        thef_type=case.thef_type,
        car_use = case.car_use,
        driver_name = case.driver_name,
        driver_occupation = case.driver_occupation
    )
    try:
        result = conn.execute(newCase)
        accessToken = caseService.createAccessToken(createdAt, result.lastrowid)
        # Confirmar la transacción
        data = {"detail": "Caso creado exitosamente",
                "case_id": result.lastrowid,
                "case_access_token": accessToken}
        conn.commit()
        return customResponses.JsonEmitter.response(status.HTTP_201_CREATED, content=data)
    except exc.SQLAlchemyError as exception:
        conn.rollback()  # Revertir la transacción en caso de error
        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}", exception=exception)
    
# Obtengo la información del caso según su id (y si existe)
@case.get("/get/{id}")
async def readCase(id: int):
    # Busca un caso por su ID
    result = caseService.searchCaseById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="El caso no existe")
    # Creo un diccionario con los datos del usuario, compañía y vehículo correspondiente
    data = caseService.caseJSON(result[0], result[1], result[2], result[3],
                                result[4], result[5], result[6], result[7],
                                result[8], result[9], result[10], result[11],
                                result[12], result[13], result[14], result[15],
                                result[16], result[17], result[18], True)
    # Convierte el diccionario en formato JSON
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

@case.get("/all")
async def getCases(request: Request):
    role = request.state.user.get("role")
    if role == "admin":
        query = caseModel.select().order_by(desc(caseModel.c.created_at))
    else:
        id = request.state.user.get("id")
        query = caseModel.select().where(caseModel.c.user_id == id).order_by(desc(caseModel.c.created_at))
    results = conn.execute(query).fetchall()
    cases = []
    for result in results:
        case = caseService.caseJSON(result[0], result[1], result[2], result[3],
                                    result[4], result[5], result[6], result[7],
                                    result[8], result[9], result[10], result[11],
                                    result[12], result[13], result[14], result[15],
                                    result[16], result[17], result[18], False)
        cases.append(case)
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=cases)

# Borrar caso
@case.delete("/{id}", name="Borrar caso")
async def deleteCase(id: int):
    result = caseService.searchCaseById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")
    try:
        conn.execute(image.delete().where(image.c.case_id == id))
        query = caseModel.delete().where(caseModel.c.id == id)
        result = conn.execute(query)
    except:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al eliminar el caso")  
    conn.commit()
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Caso eliminado exitosamente")


@case.put("/dropCase", name="Tirar caso")
async def dropCase(case: CaseId): #, request: Request):
    """role = request.state.user.get("role")
    if role == "operator":
        userId = request.state.user.get("id")"""
    id = case.case_id
    result = caseService.searchCaseById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")
    try:
        query = caseModel.update().where(caseModel.c.id == id).values(dropped=1)
        result = conn.execute(query)
    except:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al abandonar caso")
    conn.commit()
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Caso abandonado exitosamente")

@case.post("/validate")
async def validateToken(caseAccess: AccessToken):
    case = caseService.verifyAccessToken(caseAccess.case_access_token)
    if case == None:
        return customResponses.JsonEmitter.response(status.HTTP_200_OK, content={"is_valid": False, "detail": "Token vencido"})
    
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content={"is_valid": True, "detail": "Token válido"})


@case.post("/expire")
async def modifyAccessToken(accessToken: AccessTokenModify):
    case = caseService.searchAccessToken(accessToken.case_access_token)
    if not case:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Token de acceso no encontrado")
    exp = datetime.now() + timedelta(minutes=accessToken.hour_from_now*60)
    updateData = {
        "due_date": exp
    }
    
    try:
        query = AccessModel.update().where(AccessModel.c.access_token == accessToken.case_access_token).values(**updateData)
        conn.execute(query)
        conn.commit()
    except:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="No se pudo expirar el caso")
    data = {"detail": "Token actualizado exitosamente",
            "expiration_date": exp.strftime("%B %d, %Y %I:%M %p")}
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

@case.patch("/update/{id}")
async def modifyCase(case: CaseModify, id: int):
    caseToUpdate = caseService.searchCaseById(id)
    if not caseToUpdate:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="El caso no existe")
    updateData = {}
    if case.user_id != None:
        updateData["user_id"] = case.user_id
    if case.business_id != None:
        updateData["business_id"] = case.business_id
    if case.vehicle != None:
        vehicleId, response = vehicleService.createVehicle(case.vehicle)
        if response:
            return customResponses.JsonEmitter.response(status=status.HTTP_400_BAD_REQUEST, detail=response)
        updateData["vehicle"] = vehicleId
    if case.accident_number != None:
        updateData["accident_number"] = case.accident_number
    if case.finished_at != None:
        updateData["finished_at"] = case.finished_at
    if case.dropped != None:
        if case.dropped != 1 and case.dropped != 0:
            return customResponses.JsonEmitter.response(status=status.HTTP_400_BAD_REQUEST, detail="El valor del atributo 'Dropped' debe ser 0 ó 1")
        updateData["dropped"] = case.dropped
    if case.policy != None:
        updateData["policy"] = case.policy
    if case.insured_name != None:
        updateData["insured_name"] = case.insured_name
    if case.insured_dni != None:
        updateData["insured_dni"] = case.insured_dni
    if case.insured_phone != None:
        updateData["insured_phone"] = case.insured_phone
    if case.insured_address != None:
        updateData["insured_address"] = case.insured_address
    if case.accident_date != None:
        updateData["accident_date"] = case.accident_date
    if case.accident_place != None:
        updateData["accident_place"] = case.accident_place
    if case.thef_type != None:
        updateData["thef_type"] = case.thef_type
    if case.car_use != None:
        updateData["car_use"] = case.car_use
    if case.driver_name != None:
        updateData["driver_name"] = case.driver_name
    if case.driver_occupation != None:
        updateData["driver_occupation"] = case.driver_occupation
    try:
        query = caseModel.update().where(caseModel.c.id == id).values(**updateData)
        conn.execute(query)
        conn.commit()
    except exc.DataError as exception:
        conn.rollback()
        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: tipo de robo incorrecto", exception=exception)
    except exc.IntegrityError as exception:
        conn.rollback()
        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: llave foránea inexistente", exception=exception)
    except:
        conn.rollback()
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="No se pudo actualizar el caso")

    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Caso editado exitosamente")

@case.post("/finished")
def finishCase(case: CaseId):
    id = case.case_id
    result = caseService.searchCaseById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")
    try:
        query = caseModel.update().where(caseModel.c.id == id).values(finished_at=datetime.now())
        result = conn.execute(query)
    except:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al finalizar caso")
    conn.commit()
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Caso finalizado exitosamente")
