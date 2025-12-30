from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Building schemas
class BuildingBase(BaseModel):
    name: str
    address: Optional[str] = None
    description: Optional[str] = None

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Floor schemas
class FloorBase(BaseModel):
    building_id: int
    floor_number: int
    name: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    image_url: Optional[str] = None
    walkable_graph: Optional[dict] = None

class FloorCreate(FloorBase):
    pass

class Floor(FloorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# WiFi scan schemas
class WifiScan(BaseModel):
    bssid: str
    rssi: float

class FingerprintBase(BaseModel):
    floor_id: int
    x: float = Field(..., description="Ground truth x position in meters")
    y: float = Field(..., description="Ground truth y position in meters")
    device_model: Optional[str] = None
    wifi_scans: List[WifiScan]

class FingerprintCreate(FingerprintBase):
    pass

class Fingerprint(FingerprintBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Batch fingerprint upload
class FingerprintBatch(BaseModel):
    fingerprints: List[FingerprintCreate]

# Radio map response for localization
class RadioMapPoint(BaseModel):
    x: float
    y: float
    wifi_scans: List[WifiScan]

class RadioMap(BaseModel):
    floor_id: int
    points: List[RadioMapPoint]

# Access Point schemas
class AccessPointBase(BaseModel):
    bssid: str
    ssid: Optional[str] = None

class AccessPoint(AccessPointBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True
