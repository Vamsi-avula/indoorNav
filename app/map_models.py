from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FloorPlanVersion(Base):
    """Version control for floor plans"""
    __tablename__ = "floor_plan_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'image', 'pdf'
    file_size = Column(Integer)
    width = Column(Float)  # pixels
    height = Column(Float)  # pixels
    scale = Column(Float, default=1.0)  # pixels per meter
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String)  # user ID or name
    is_active = Column(Boolean, default=True)
    change_notes = Column(Text)
    
    # Relationships
    floor = relationship("Floor", back_populates="versions")
    pois = relationship("PointOfInterest", back_populates="version")
    routing_nodes = relationship("RoutingNode", back_populates="version")
    routing_edges = relationship("RoutingEdge", back_populates="version")

class PointOfInterest(Base):
    """Points of Interest on floor plans"""
    __tablename__ = "points_of_interest"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("floor_plan_versions.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'room', 'elevator', 'stairs', 'restroom', etc.
    poi_type = Column(String, nullable=False)  # specific type within category
    x_coordinate = Column(Float, nullable=False)  # pixel coordinates
    y_coordinate = Column(Float, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    properties = Column(JSON)  # additional properties like accessibility, hours, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    version = relationship("FloorPlanVersion", back_populates="pois")

class RoutingNode(Base):
    """Navigation graph nodes"""
    __tablename__ = "routing_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("floor_plan_versions.id"), nullable=False)
    x_coordinate = Column(Float, nullable=False)
    y_coordinate = Column(Float, nullable=False)
    node_type = Column(String, nullable=False)  # 'junction', 'decision_point', 'poi_connection'
    is_active = Column(Boolean, default=True)
    properties = Column(JSON)  # additional node properties
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    version = relationship("FloorPlanVersion", back_populates="routing_nodes")
    edges_from = relationship("RoutingEdge", foreign_keys="RoutingEdge.from_node_id", back_populates="from_node")
    edges_to = relationship("RoutingEdge", foreign_keys="RoutingEdge.to_node_id", back_populates="to_node")

class RoutingEdge(Base):
    """Navigation graph edges (connections between nodes)"""
    __tablename__ = "routing_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("floor_plan_versions.id"), nullable=False)
    from_node_id = Column(Integer, ForeignKey("routing_nodes.id"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("routing_nodes.id"), nullable=False)
    distance = Column(Float, nullable=False)  # in meters
    travel_time = Column(Float)  # in seconds
    edge_type = Column(String, nullable=False)  # 'walkway', 'elevator', 'stairs'
    is_bidirectional = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    properties = Column(JSON)  # accessibility, slope, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    version = relationship("FloorPlanVersion", back_populates="routing_edges")
    from_node = relationship("RoutingNode", foreign_keys=[from_node_id], back_populates="edges_from")
    to_node = relationship("RoutingNode", foreign_keys=[to_node_id], back_populates="edges_to")

class MapPublishing(Base):
    """Map publishing workflow and version control"""
    __tablename__ = "map_publishing"
    
    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("floor_plan_versions.id"), nullable=False)
    status = Column(String, nullable=False)  # 'draft', 'review', 'approved', 'published', 'archived'
    published_at = Column(DateTime(timezone=True))
    published_by = Column(String)
    review_notes = Column(Text)
    validation_results = Column(JSON)  # validation errors/warnings
    is_current = Column(Boolean, default=False)  # currently published version
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    floor = relationship("Floor")
    version = relationship("FloorPlanVersion")
