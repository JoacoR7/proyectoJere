# Inicia el servidor: uvicorn main:app --reload
from fastapi import FastAPI
from routers import users, company, images, vehicles, cases

app = FastAPI()

# Incluye las rutas definidas en la carpeta routers
app.include_router(users.user, tags=["Endpoints usuarios"], prefix="/users")
app.include_router(company.company, tags=["Endpoints compañías"], prefix="/company")
app.include_router(images.image, tags=["Endpoints imagen"], prefix="/images")
app.include_router(vehicles.vehicle, tags=["Endpoints vehículos"], prefix="/vehicle")
app.include_router(cases.case, tags=["Endpoints casos"], prefix="/case")