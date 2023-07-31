from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.business import business as businessModel
from services import businessService, authService
from schemas.business import Business
from sqlalchemy import exc

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
async def createbusiness(newbusiness: Business, request: Request):
    await authService.verifyAdmin(request)
    findbusiness = businessService.searchBusinessByName(newbusiness.name)
    if findbusiness:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La compañía ya existe")
    newbusiness = businessModel.insert().values(
        name=newbusiness.name,
        case_dropped_letter=newbusiness.case_dropped_letter

    )
    try:
        conn.execute(newbusiness)
        conn.commit()  # Confirmar la transacción
        return {"message": "Compañía creada exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear la compañía: {str(e)}"}

# Obtener listado de compañías de la db
@business.get("", name="Obtener todas las compañías de la bd")
async def getCompanies():
    # Obtengo todos los registros de la tabla "companies" de la bd
    result = conn.execute(businessModel.select()).fetchall()
    if not result:
        # Si no se encuentran compañías, devuelve una respuesta vacía con el código de estado 204
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No hay compañías")
    data = []
    # En la lista data acumulo todos los usuarios en forma de diccionario
    for business in result:
        newbusiness = businessService.businessJSON(result=business)
        data.append(newbusiness)
    # Convierte la lista de diccionarios en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

# Obtener una compañía por id
@business.get("/{id}", name="Obtener una compañía por su id")
async def getbusiness(id: int):
    # Busca una compañía por su ID
    result = businessService.searchBusinessById(id)
    if not result:
        raise HTTPException(status_code=204, detail="Compañía no encontrada")
    # Creo un diccionario con los datos de la compañía encontrada
    data = businessService.businessJSON(result=result)
    # Convierte el diccionario en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

@business.patch("/changeName/{id}", name="Cambiar nombre compañía")
async def changebusinessName(id: int, name: str, request: Request):
    await authService.verifyAdmin(request)
    result = businessService.searchBusinessById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    result = businessService.searchBusinessByName(name)
    if result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la compañía ya existe")
    try:
        query = businessModel.update().where(businessModel.c.id == id).values(name=name)
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Nombre de compañía editado exitosamente"}    


