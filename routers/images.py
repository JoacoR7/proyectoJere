from fastapi import APIRouter, status
from schemas.image import Image as imageSchema
from models.image import image as imageModel
from configuration.db import conn
from sqlalchemy import exc
import base64
from utils import customResponses
from services import imageService, caseService
from utils.kvalidator import (
    cedula_extractor,
    dni_extractor,
    car_validator,
    cedula_validator,
    dni_validator,
    licencia_front_validator,
    licencia_back_validator,

)


image = APIRouter()

"""
Funciones:
C: upload
R: getImage
"""

@image.post("/upload")
def upload(newPhoto: imageSchema):
    validated = False
    if newPhoto.validation_attemps<3:
        data = {
        "data": newPhoto.photo
        }
        if(newPhoto.type == "LATERAL_DERECHO" or newPhoto.type == "LATERAL_IZQUIERDO" 
            or newPhoto.type == "PARTE_FRONTAL" or newPhoto.type == "PARTE_TRASERA" 
            or newPhoto.type == "RUEDA" or newPhoto.type == "CERRADURA"):
            validated  =  car_validator(data).get("is_valid")
        elif(newPhoto.type == "DOCUMENTACION_FRONTAL" or newPhoto.type == "DOCUMENTACION_DORSAL"):
            return customResponses.JsonEmitter.response(status.HTTP_200_OK, content=dni_extractor(data))
            if(not dni_extractor(data).get("error") and newPhoto.photo_detail == "DNI"):
                validated = True
                extracted_data = dni_extractor(data)
            elif(cedula_validator(data) and newPhoto.photo_detail == "CEDULA"):
                extracted_data = cedula_extractor(data)
                validated = True
            elif(licencia_front_validator(data) and newPhoto.photo_detail == "LICENCIA"):
                validated = True
            elif(licencia_back_validator(data) and newPhoto.photo_detail == "LICENCIA"):
                validated = True

    if(newPhoto.validation_attemps <3 and not validated):
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail="Imagen no válida")
    
    caseId = newPhoto.case_id
    result = caseService.searchCaseById(caseId)
    if not result:
        return customResponses.JsonEmitter.response(status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")

    # Convierto la imagen de Base64 a bytes
    blob = base64.b64decode(newPhoto.photo)

    query = imageModel.insert().values(
        photo=blob,
        case_id=newPhoto.case_id,
        validated = validated,
        validation_attemps=newPhoto.validation_attemps,
        metadata=newPhoto.metadata,
        type=newPhoto.type
    )
    try:
        result = conn.execute(query)
        conn.commit() # Confirmar la transacción
        return customResponses.JsonEmitter.response(status.HTTP_201_CREATED, detail="Imagen guardada exitosamente")
    except exc.SQLAlchemyError as e:
        conn.rollback() # Revertir la transacción en caso de error
        return customResponses.JsonEmitter.response(status.HTTP_400_BAD_REQUEST, detail=f"Error al guardar la imagen: {str(e)}")

@image.get("/{id}")
def getImage(id:int):
    query = imageModel.select().where(imageModel.c.id == id)
    result = conn.execute(query).first()
    if not result:
        return customResponses.JsonEmitter.response(status=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    image = imageService.imageJSON(result)
    return customResponses.JsonEmitter.response(status=status.HTTP_200_OK, content=image)
