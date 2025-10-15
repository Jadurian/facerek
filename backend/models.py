from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    activo = Column(String(50))  # CTA, RDA, Pichi
    uso_imagen = Column(String(50))  # Firmado, No firmado, No autoriza, Espera
    sigue_trabajando = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    photos = relationship("EmployeePhoto", back_populates="employee", cascade="all, delete-orphan")

class EmployeePhoto(Base):
    __tablename__ = 'employee_photos'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    face_encoding = Column(LargeBinary)
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="photos")

class CampaignPhoto(Base):
    __tablename__ = 'campaign_photos'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String(50))  # OK, WARNING, REJECTED
    validation_details = Column(Text)  # JSON string
    
    detections = relationship("PhotoDetection", back_populates="campaign_photo", cascade="all, delete-orphan")

class PhotoDetection(Base):
    __tablename__ = 'photo_detections'
    
    id = Column(Integer, primary_key=True)
    campaign_photo_id = Column(Integer, ForeignKey('campaign_photos.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    confidence = Column(Float)
    bounding_box = Column(Text)  # JSON string
    
    campaign_photo = relationship("CampaignPhoto", back_populates="detections")
    employee = relationship("Employee")
