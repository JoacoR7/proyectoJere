from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.business import business as businessModel
from services import businessService, authService
from schemas.business import Business, BusinessName
from sqlalchemy import exc
from utils import customResponses

business = APIRouter()

"""
Funciones:
C: createbusiness
R: getCompanies (obtengo todas las compañías) - getbusiness (obtengo una compañía por id)
U: changebusinessName (edito el nombre de una compañía)
D: deletebusiness (borro la compañía)
"""

# Registrar compañía
@business.post("/create", name="Crear nueva compañía")
async def createbusiness(newbusiness: BusinessName, request: Request):
    await authService.verifyAdmin(request)
    findbusiness = businessService.searchBusinessByName(newbusiness.name)
    if findbusiness:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="El nombre de compañía ya está en uso")
    if newbusiness.name == "":
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Nombre inválido")
    newbusiness = businessModel.insert().values(
        name=newbusiness.name
    )
    try:
        conn.execute(newbusiness)
        conn.commit()  # Confirmar la transacción
        return customResponses.JsonEmitter.response(status.HTTP_201_CREATED, detail="Compañía creada exitosamente")
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la compañía: {str(e)}")

# Obtener listado de compañías de la db
@business.get("", name="Obtener todas las compañías de la bd")
async def getCompanies():
    # Obtengo todos los registros de la tabla "companies" de la bd
    result = conn.execute(businessModel.select()).fetchall()
    if not result:
        # Si no se encuentran compañías, devuelve una respuesta vacía con el código de estado 204
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="No hay compañías")
    data = []
    # En la lista data acumulo todos los usuarios en forma de diccionario
    for business in result:
        newbusiness = businessService.businessJSON(result=business)
        data.append(newbusiness)
    # Convierte la lista de diccionarios en formato JSON
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

# Obtener una compañía por id
@business.get("/{id}", name="Obtener una compañía por su id")
async def getbusiness(id: int):
    # Busca una compañía por su ID
    result = businessService.searchBusinessById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    # Creo un diccionario con los datos de la compañía encontrada
    data = businessService.businessJSON(result=result)
    # Convierte el diccionario en formato JSON
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

@business.patch("/update/{id}", name="Actualizar compañía")
async def changebusinessName(id: int, business: BusinessName, request: Request):
    response = await authService.verifyAdmin(request)
    if response:
        return response
    result = businessService.searchBusinessById(id)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    # result = businessService.searchBusinessByName(business.name)
    # if result:
    #     return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="El nombre de la compañía ya existe")
    try:
        query = businessModel.update().where(businessModel.c.id == id).values(name=business.name)
        result = conn.execute(query)
    except:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al cambiar el nombre de compañía")
    conn.commit()
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Nombre de compañía editado exitosamente")


