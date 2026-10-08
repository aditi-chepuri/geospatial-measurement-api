from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routers.files import router as files_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for uploading and measuring geospatial files.",
    version="1.0.0"
)


app.include_router(files_router)


@app.get("/")
def home():
    return {
        "message": "Geospatial File Measurement API is running"
    }