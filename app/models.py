from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    feature_count = Column(Integer, default=0)
    crs = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PROCESSING")

    measurements = relationship(
        "Measurement",
        back_populates="file",
        cascade="all, delete-orphan"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)

    feature_id = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)

    # Store feature attributes as JSON text.
    properties = Column(Text, nullable=True)

    # Store geometry as GeoJSON text.
    geometry = Column(Text, nullable=True)

    area = Column(Float, nullable=True)
    length = Column(Float, nullable=True)

    message = Column(String, nullable=True)

    file = relationship(
        "File",
        back_populates="measurements"
    )