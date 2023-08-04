from fastapi import APIRouter, File
from fastapi.responses import StreamingResponse
from schemas.image import Image as imageSchema
from models.image import image as imageModel
from configuration.db import conn
from sqlalchemy import exc
from io import BytesIO
from PIL import Image

image = APIRouter()

"""
Funciones:
C: upload
R: getImage
"""

@image.post("/upload")
def upload(photo: imageSchema, newPhoto: bytes = File(...)):
    print(photo)
    query = imageModel.insert().values(
        photo=newPhoto,
        case_id=photo.case_id,
        validated=photo.validated,
        validation_attemps=photo.validation_attemps,
        metadata=photo.metadata
    )
    try:
        result = conn.execute(query)
        conn.commit() # Confirmar la transacción
        return {"message": "Imagen guardada exitosamente"}
    except exc.SQLAlchemyError as e:
        conn.rollback() # Revertir la transacción en caso de error
        return {"message": f"Error al guardar la imagen: {str(e)}"}

@image.get("/{id}")
def getImage(id:int):
    # Consultar la imagen en la base de datos
    query = imageModel.select().where(imageModel.c.id == id)
    result = conn.execute(query).fetchone()
    if result is None:
        return {"message": "Imagen no encontrada"}

    image_data = result[1]
    img = Image.open(BytesIO(image_data))

    # Convertir la imagen a formato JPEG y guardarla en un búfer
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    # Devolver la imagen como respuesta HTTP
    return StreamingResponse(buffer, media_type="image/jpeg")
