from fastapi import APIRouter, File
from fastapi.responses import StreamingResponse
from schemas.image import Image
from models.image import image as imageModel
from configuration.db import conn
from sqlalchemy import exc
from io import BytesIO
from PIL import Image

image = APIRouter()

@image.post("/upload")
def upload(case_id: int, validated: bool, validation_attemps: int, photo: bytes = File(...)):
    query = imageModel.insert().values(
        photo=photo,
        case_id=case_id,
        validated=validated,
        validation_attemps=validation_attemps
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
