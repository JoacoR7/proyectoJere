import re
from models.vehicle import vehicle
from configuration.db import conn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

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
        "licence_plate": result[3],
        "type": result[4]
    }

    return vehicle
    