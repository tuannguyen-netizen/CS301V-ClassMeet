from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="ClassMeet API")
app.include_router(router)