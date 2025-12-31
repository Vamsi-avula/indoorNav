from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Floor Plan Version Schemas
class FloorPlanVersionBase(BaseModel):
    version_number: int
    file_type: str
    scale: float = 1.0
    change_notes: Optional[str] = None

class FloorPlanVersionCreate(FloorPlanVersionBase):
    floor_id: int
    file_path: str
    file_size: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None
    created_by: Optional[str] = None

class FloorPlanVersionUpdate(BaseModel):
    scale: Optional[float] = None
    change_notes: Optional[str] = None
    is_active: Optional[bool] = None

class FloorPlanVersion(FloorPlanVersionBase):
    id: int
    floor_id: int
    file_path: str
    file_size: Optional[int]
    width: Optional[float]
    height: Optional[float]
    created_at: datetime
    created_by: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

# POI Schemas
class POIBase(BaseModel):
    name: str
    category: str
    poi_type: str
    x_coordinate: float
    y_coordinate: float
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class POICreate(POIBase):
    version_id: int

class POIUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    poi_type: Optional[str] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PointOfInterest(POIBase):
    id: int
    version_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Routing Node Schemas
class RoutingNodeBase(BaseModel):
    x_coordinate: float
    y_coordinate: float
    node_type: str
    properties: Optional[Dict[str, Any]] = None

class RoutingNodeCreate(RoutingNodeBase):
    version_id: int

class RoutingNodeUpdate(BaseModel):
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    node_type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class RoutingNode(RoutingNodeBase):
    id: int
    version_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Routing Edge Schemas
class RoutingEdgeBase(BaseModel):
    from_node_id: int
    to_node_id: int
    distance: float
    travel_time: Optional[float] = None
    edge_type: str
    is_bidirectional: bool = True
    properties: Optional[Dict[str, Any]] = None

class RoutingEdgeCreate(RoutingEdgeBase):
    version_id: int

class RoutingEdgeUpdate(BaseModel):
    distance: Optional[float] = None
    travel_time: Optional[float] = None
    edge_type: Optional[str] = None
    is_bidirectional: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class RoutingEdge(RoutingEdgeBase):
    id: int
    version_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Map Publishing Schemas
class MapPublishingBase(BaseModel):
    status: str
    review_notes: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None

class MapPublishingCreate(MapPublishingBase):
    floor_id: int
    version_id: int
    published_by: Optional[str] = None

class MapPublishingUpdate(BaseModel):
    status: Optional[str] = None
    review_notes: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    is_current: Optional[bool] = None

class MapPublishing(MapPublishingBase):
    id: int
    floor_id: int
    version_id: int
    published_at: Optional[datetime]
    published_by: Optional[str]
    is_current: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Combined Schemas for Complex Operations
class FloorPlanWithVersion(BaseModel):
    floor_id: int
    version: FloorPlanVersion
    pois: List[PointOfInterest] = []
    routing_nodes: List[RoutingNode] = []
    routing_edges: List[RoutingEdge] = []

class MapValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    statistics: Dict[str, Any] = {}

class MapPublishingWorkflow(BaseModel):
    version_id: int
    validation_result: MapValidationResult
    publishing_status: str
    next_steps: List[str] = []
