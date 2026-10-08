from typing import List
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import File as FileModel, Measurement
from app.schemas import FileResponse, MeasurementResponse
from app.services.file_processor import process_file
from app.services.measurement import calculate_measurements


router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or ""
    extension = os.path.splitext(filename)[1].lower()

    if extension not in [".zip", ".kml"]:
        raise HTTPException(
            status_code=400,
            detail="Only .zip and .kml files are supported."
        )

    # Generate a unique and safe server-side filename.
    safe_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        # Save uploaded file.
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process geospatial file.
        gdf = process_file(file_path, filename)

        crs = str(gdf.crs) if gdf.crs else None

        # Calculate measurements.
        measurement_results = calculate_measurements(gdf)

        # Save file information.
        file_record = FileModel(
            filename=filename,
            feature_count=len(gdf),
            crs=crs,
            status="COMPLETED"
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Save feature information and measurements.
        for result in measurement_results:

            measurement = Measurement(
                file_id=file_record.id,
                feature_id=result["feature_id"],
                geometry_type=result["geometry_type"],
                properties=result["properties"],
                geometry=result["geometry"],
                area=result["area"],
                length=result["length"],
                message=result["message"]
            )

            db.add(measurement)

        db.commit()

        return file_record

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"File processing failed: {str(e)}"
        )

    finally:

        # Remove temporary uploaded file.
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get(
    "/{file_id}",
    response_model=FileResponse
)
def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    file_record = db.query(FileModel).filter(
        FileModel.id == file_id
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return file_record


@router.get(
    "/{file_id}/measurements/",
    response_model=List[MeasurementResponse]
)
def get_measurements(
    file_id: int,
    db: Session = Depends(get_db)
):
    file_record = db.query(FileModel).filter(
        FileModel.id == file_id
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    measurements = db.query(Measurement).filter(
        Measurement.file_id == file_id
    ).all()

    return measurements