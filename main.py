# Inicia el server: uvicorn main:app --reload
from fastapi import FastAPI
from routers import users

app = FastAPI()

app.include_router(users.user)