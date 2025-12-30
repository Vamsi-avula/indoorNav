from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    floors = relationship("Floor", back_populates="building")

class Floor(Base):
    __tablename__ = "floors"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    floor_number = Column(Integer, nullable=False)
    name = Column(String)
    width = Column(Float)  # meters
    height = Column(Float)  # meters
    image_url = Column(String)  # floorplan image
    floor_plan_image = Column(String)  # uploaded floor plan image path
    walkable_graph = Column(JSON)  # navigation graph as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    building = relationship("Building", back_populates="floors")
    fingerprints = relationship("Fingerprint", back_populates="floor")

class Fingerprint(Base):
    __tablename__ = "fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)
    x = Column(Float, nullable=False)  # ground truth x position in meters
    y = Column(Float, nullable=False)  # ground truth y position in meters
    device_model = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    wifi_scans = Column(JSON, nullable=False)  # [{bssid, rssi}, ...]
    
    floor = relationship("Floor", back_populates="fingerprints")

class AccessPoint(Base):
    __tablename__ = "access_points"
    
    id = Column(Integer, primary_key=True, index=True)
    bssid = Column(String, unique=True, nullable=False, index=True)
    ssid = Column(String)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
