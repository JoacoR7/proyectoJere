# Inicia el servidor: uvicorn main:app --reload
from fastapi import FastAPI, Depends, Request
from routers import business, users, images, vehicles, cases
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from services import authService
import uvicorn

app = FastAPI()

#NOTAS
# Revisar photo upload
# case: devolver http 400 al enviar una llave foránea inexistente

async def auth_middleware(request: Request, call_next):
    current_path = request.url.path
    unprotected_routes = ["/docs", "/openapi.json", "/users/login", "/users/register",'/images/upload','/case/validate','/case/dropCase', '/case/finished','/case/expire']
    if current_path in unprotected_routes or current_path[:-1] in unprotected_routes:
        response = await call_next(request)
        return response
    else:
        # Verifico el token
        user, response = await authService.auth_user(request)
        if(user == None):
            return response
        request.state.user = user
        response = await authService.isEnabled(request)
        if(response != None):
            return response
        response = await call_next(request)
        return response

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.middleware('http')(auth_middleware)

# Incluye las rutas definidas en la carpeta routers
app.include_router(users.user, tags=["Endpoints usuarios"], prefix="/users")
app.include_router(business.business, tags=["Endpoints compañías"], prefix="/business")
app.include_router(images.image, tags=["Endpoints imagen"], prefix="/images")
app.include_router(vehicles.vehicle, tags=["Endpoints vehículos"], prefix="/vehicle")
app.include_router(cases.case, tags=["Endpoints casos"], prefix="/case")
