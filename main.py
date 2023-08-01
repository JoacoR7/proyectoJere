# Inicia el servidor: uvicorn main:app --reload
from fastapi import FastAPI, Depends, Request
from routers import business, users, images, vehicles, cases
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from services import authService
app = FastAPI()

#NOTAS
# Middleware que verifica el token del usuario para permitirle o no ejecutar tareas
# Servicio de autenticación de rol admin para verificar si tiene permisos para realizar cierta tarea
# Update user con patch sólo para el dato correspondiente
# Para acceder a Koyeb tenés que poner la tarjeta :(
# Render parece ser gratuito, pero hay que poner el proyecto como público en github para poder ver si funciona
# El id de usuario, compañía, etc lo recibo como json?
# Case dropped letter es de caso, no?

async def auth_middleware(request: Request, call_next):
    current_path = request.url.path
    unprotected_routes = ["/docs", "/openapi.json", "/users/login", "/users/register"]
    #protected_routes = []
    if current_path in unprotected_routes or current_path[:-1] in unprotected_routes: #or current_path not in protected_routes:
        response = await call_next(request)
        return response
    else:
        # Verifico el token
        user, response = await authService.auth_user(request)
        if(user == None):
            return response
        request.state.user = user
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