from models.vehicle import vehicle
from configuration.db import conn
from utils import customResponses
from fastapi import status
from sqlalchemy import exc

"""def verificarPatente(patente):
    formato1 = r'^[A-Z]{3}\s\d{3}$'
    formato2 = r'^[A-Z]{2}\s\d{3}\s?[A-Z]{2}$'
    
    if re.match(formato1, patente) or re.match(formato2, patente):
        return True
    else:
        return False
    """
#Buscar vehículo por id
def searchVehicleById(id: int):
    query = vehicle.select().where(vehicle.c.id == id)
    result = conn.execute(query).first()
    return result

# Devuelvo un diccionario con los datos del vehículo
def vehicleJSON(id=None, result = None):
    if result == None:
        if id != None:
            result = searchVehicleById(id)
        else:
            return None
    
    vehicle = {
        "id": result[0],
        "brand": result[1],
        "model": result[2],
        "licence_plate": result[4],
        "type": result[3]
    }
    return vehicle

def createVehicle(newVehicle):
    patente = newVehicle.licence_plate.upper()
    """if not vehicleService.verificarPatente(patente):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se respeta el formato de patente")"""
    query = vehicle.insert().values(
        brand=newVehicle.brand,
        model=newVehicle.model,
        licence_plate=patente,
        type=newVehicle.type
    )
    try:
        result = conn.execute(query)
        # Confirmar la transacción
        id = result.lastrowid
        return id, None
    except exc.DataError as exception:

        sqlalchemyStatusError = customResponses.sqlAlchemySplitter.split(exception)
        return None, customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"SQLAlchemy error {sqlalchemyStatusError}: tipo de vehículo incorrecto", exception=exception)
    except exc.SQLAlchemyError as e:
        # Revertir la transacción en caso de error
        return None, customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"Error al guardar el vehículo: {str(e)}")
    