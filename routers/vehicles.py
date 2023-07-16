from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from configuration.db import conn
from models.vehicle import vehicle as vehicleModel
from schemas.vehicle import Vehicle
from sqlalchemy import exc
from services import vehicleService

vehicle = APIRouter()

"""
Funciones:
C: createVehicle
"""

# Endpoint creación vehículo
@vehicle.post("/create")
def createVehicle(newVehicle: Vehicle):
    patente = newVehicle.licence_plate.upper()
    if not vehicleService.verificarPatente(patente):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se respeta el formato de patente")
    query = vehicleModel.insert().values(
        brand=newVehicle.brand,
        model=newVehicle.model,
        licence_plate=patente
    )
    try:
        conn.execute(query)
        conn.commit() # Confirmar la transacción
        return {"message": "Vehículo creado exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback() # Revertir la transacción en caso de error
        return {"message": f"Error al guardar el vehículo: {str(e)}"}