from pydantic import BaseModel
from typing import Optional


class FileResponse(BaseModel):
    id: int
    filename: str
    feature_count: int
    crs: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class MeasurementResponse(BaseModel):
    id: int
    feature_id: int
    geometry_type: str

    properties: Optional[str] = None
    geometry: Optional[str] = None

    area: Optional[float] = None
    length: Optional[float] = None

    message: Optional[str] = None

    class Config:
        from_attributes = True