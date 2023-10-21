from models.case import case
from models.caseAccessToken import caseAccessToken as caseAccessModel
from configuration.db import conn
from datetime import timedelta, datetime
from jose import jwt, JWTError
from sqlalchemy import exc
from fastapi import status,HTTPException
from fastapi.responses import JSONResponse
from services import userService, businessService, imageService, vehicleService

ALGORITHM = "HS256"
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

# Buscar compañía por id
def searchCaseById(id: int):
    query = case.select().where(case.c.id == id)
    result = conn.execute(query).first()
    return result

def generateToken(creationDate, caseId, time):
    
    exp = creationDate + timedelta(minutes=time)
    access_token = {"caseId": caseId,
                    "exp": exp}
    access_token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return access_token, exp

def createAccessToken(creationDate, caseId, time=1440):
    access_token, exp = generateToken(creationDate, caseId, time)
    query = caseAccessModel.insert().values(
        access_token = access_token,
        due_date = exp 
    )
    try:
        conn.execute(query)
        conn.commit()  # Confirmar la transacción
        return access_token
    except exc.SQLAlchemyError as e:
        conn.rollback()  # Revertir la transacción en caso de error
        return {"message": f"Error al crear el token: {str(e)}"}
    
def verifyAccessToken(accessToken):
    # try:
        # case = jwt.decode(accessToken, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False})
        # if case is None:
        #     return None, response

    currDate = int(datetime.now().timestamp())
    caseDb = searchAccessToken(accessToken)

    raise HTTPException(status_code=404, detail={"currDate": currDate,"caseDbDate":caseDb[2].timestamp()})

    if currDate > caseDb[2].timestamp():
        return None

    # except JWTError:
    #     return None
    
    return case

def searchAccessToken(accessToken):
    query = caseAccessModel.select().where(caseAccessModel.c.access_token == accessToken)
    result = conn.execute(query).first()
    return result

def caseJSON(caseId, userId, companyId, vehicle, 
            accidentNumber, createdAt, finishedAt, dropped,
            policy, insuredName, insuredDNI, insuredPhone,
            insuredAdress, accidentDate, accidentPlace, car_use,
            driver_name, driver_occupation, thefType, showImages = False):
    user = userService.userJSON(id=userId)
    business = businessService.businessJSON(id=companyId)
    images = True if imageService.getImages(caseId) else False
    vehicle = vehicleService.vehicleJSON(id=vehicle)
    imagesJSON = []
    if showImages:
        for image in imageService.getImages(caseId):
            imagesJSON.append(imageService.imageJSON(image))
    case = {
        "id": caseId,
        "user": user,
        "photo": imagesJSON if showImages else images,
        "business": business,
        "vehicle": vehicle,
        "accident_number": accidentNumber,
        "created_at": createdAt,
        "finished_at": finishedAt,
        "dropped": dropped,
        "policy": policy,
        "insured_name": insuredName,
        "insured_dni": insuredDNI,
        "insured_phone": insuredPhone,
        "insured_address": insuredAdress,
        "accident_date": accidentDate,
        "accident_place": accidentPlace,
        "theft_type": thefType,
        "car_use": car_use,
        "driver_name": driver_name,
        "driver_occupation": driver_occupation
    }

    return case
