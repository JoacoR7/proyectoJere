from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.company import company as companyModel
from services import companyService
from schemas.company import Company
from sqlalchemy import exc

company = APIRouter()

"""
Funciones:
C: createCompany
R: getCompanies (obtengo todas las compañías) - getCompany (obtengo una compañía por id)
U: changeCompanyName (edito el nombre de una compañía)
D: deleteCompany (borro la compañía)
"""

# Registrar compañía
@company.post("/create", name="Crear nueva compañía")
async def createCompany(newCompany: Company):
    findCompany = companyService.searchCompanyByName(newCompany.name)
    if findCompany:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La compañía ya existe")
    newCompany = companyModel.insert().values(
        name=newCompany.name
    )
    try:
        conn.execute(newCompany)
        conn.commit()  # Confirmar la transacción
        return {"message": "Compañía creada exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear la compañía: {str(e)}"}

# Obtener listado de compañías de la db
@company.get("", name="Obtener todas las compañías de la bd")
async def getCompanies(): 
    # Obtengo todos los registros de la tabla "companies" de la bd
    result = conn.execute(companyModel.select()).fetchall()
    if not result:
        # Si no se encuentran compañías, devuelve una respuesta vacía con el código de estado 204
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No hay compañías")
    data = []
    # En la lista data acumulo todos los usuarios en forma de diccionario
    for company in result:
        newCompany = companyService.companyJSON(result=company)
        data.append(newCompany)
    # Convierte la lista de diccionarios en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

# Obtener una compañía por id
@company.get("/{id}", name="Obtener una compañía por su id")
async def getCompany(id: int):
    # Busca una compañía por su ID
    result = companyService.searchCompanyById(id)
    if not result:
        raise HTTPException(status_code=204, detail="Compañía no encontrada")
    # Creo un diccionario con los datos de la compañía encontrada
    data = companyService.companyJSON(result=result)
    # Convierte el diccionario en formato JSON
    json = jsonable_encoder(data)
    return JSONResponse(content=json)

@company.put("/changeName/{id}", name="Cambiar nombre compañía")
async def changeCompanyName(id: int, company: Company):
    result = companyService.searchCompanyById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compañía no encontrada")
    result = companyService.searchCompanyByName(company.name)
    if result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la compañía ya existe")
    try:
        query = companyModel.update().where(companyModel.c.id == id).values(name=company.name)
        result = conn.execute(query)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    conn.commit()
    return {"message": "Nombre de compañía editado exitosamente"}    

# Borrar compañía
@company.delete("/{id}", name="Borrar compañía")
async def deleteCompany(id: int):
    result = companyService.searchCompanyById(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="Compañía no encontrada")
    try:
        query = companyModel.delete().where(companyModel.c.id == id)
        result = conn.execute(query)
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error al eliminar compañía")
    conn.commit()
    return {"message": "Compañía eliminada exitosamente"}

