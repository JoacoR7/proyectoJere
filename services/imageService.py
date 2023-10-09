from models.image import image
from configuration.db import conn
import base64

def getImages(caseId):
    query = image.select().where(image.c.case_id == caseId)
    result = conn.execute(query).fetchall()
    return result

def encodeImage(blob):
    base64Data = base64.b64encode(blob).decode('utf-8')
    return base64Data

def imageJSON(image):
    data = {
        "id": image[0],
        "case_id": image[2],
        "type": image[3],
        "validated": image[4],
        "validation_attemps": image[5],
        "metadata": image[7],
        "detail": image[6],
        "photo": encodeImage(image[1])
    }
    return data