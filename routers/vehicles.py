from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.vehicle import vehicle as vehicleModel
from schemas.vehicle import Vehicle
from sqlalchemy import exc
from services import vehicleService
from utils import customResponses

vehicle = APIRouter()

"""
Funciones:
C: createVehicle
"""

# Endpoint creación vehículo
@vehicle.post("/create")
def createVehicle(newVehicle: Vehicle):
    patente = newVehicle.licence_plate.upper()
    """if not vehicleService.verificarPatente(patente):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se respeta el formato de patente")"""
    query = vehicleModel.insert().values(
        brand=newVehicle.brand,
        model=newVehicle.model,
        licence_plate=patente,
        type=newVehicle.type
    )
    try:
        conn.execute(query)
        conn.commit() # Confirmar la transacción
        return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Vehículo creado exitosamente")
    except exc.DataError as exception:
        conn.rollback()
        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: tipo de vehículo incorrecto", exception=exception)
    except exc.SQLAlchemyError as e:
        conn.rollback() # Revertir la transacción en caso de error
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"Error al guardar el vehículo: {str(e)}")
    
@vehicle.get("/read/{id}")
def getVehicle(id):
    vehicle = vehicleService.searchVehicleById(id)
    if not vehicle:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    data = vehicleService.vehicleJSON(result=vehicle)
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)