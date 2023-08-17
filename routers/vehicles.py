from fastapi import APIRouter, status
from services import vehicleService
from utils import customResponses
from schemas.vehicle import VehicleUpdate
from models.vehicle import vehicle as vehicleModel
from configuration.db import conn
from sqlalchemy import exc

vehicle = APIRouter()

"""
Funciones:
C: createVehicle
"""

@vehicle.get("/read/{id}")
def getVehicle(id):
    vehicle = vehicleService.searchVehicleById(id)
    if not vehicle:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    data = vehicleService.vehicleJSON(result=vehicle)
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=data)

@vehicle.patch("/update/{id}")
async def updateVehicle(id: int, vehicleUpdate: VehicleUpdate):
    vehicle = vehicleService.searchVehicleById(id)
    if not vehicle:
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Vehículo no encontrado")
    updateData = {}
    if vehicleUpdate.brand != None:
        updateData["brand"] = vehicleUpdate.brand
    if vehicleUpdate.model != None:
        updateData["model"] = vehicleUpdate.model
    if vehicleUpdate.licence_plate != None:
        updateData["licence_plate"] = vehicleUpdate.licence_plate
    if vehicleUpdate.type != None:
        updateData["type"] = vehicleUpdate.type
    try:
        query = vehicleModel.update().where(vehicleModel.c.id == id).values(**updateData)
        conn.execute(query)
        conn.commit()
    except exc.DataError as exception:

        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: tipo de vehículo incorrecto", exception=exception)
    except:
        conn.rollback()
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Error al actualizar el vehículo")
    
    return customResponses.JsonEmitter.response(status.HTTP_200_OK, detail="Vehículo actualizado exitosamente")