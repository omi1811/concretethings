"""
Geo-Fencing Models
Database models for location-based access control
Ensures workers are physically present on-site before data entry
"""

from server.db import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import math

class GeofenceLocation(Base):
    """
    Project Geo-fence Boundary
    Defines the GPS boundary for each project
    """
    __tablename__ = 'geofence_locations'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, unique=True)
    
    # Geofence Details
    location_name = Column(String(200), nullable=False)  # "Site Main Gate"
    location_description = Column(Text)
    
    # Center Point (GPS coordinates)
    center_latitude = Column(Numeric(10, 7), nullable=False)  # e.g., 19.0760
    center_longitude = Column(Numeric(10, 7), nullable=False)  # e.g., 72.8777
    
    # Radius (in meters)
    radius_meters = Column(Integer, nullable=False, default=100)  # Default 100m
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Verification Settings
    is_active = Column(Boolean, default=True)
    strict_mode = Column(Boolean, default=True)  # If True, reject outside geofence; If False, log warning
    
    # Tolerance
    tolerance_meters = Column(Integer, default=20)  # Allow 20m GPS error margin
    
    # Audit Trail
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='geofence_locations')
    project = relationship('Project', backref='geofence_location', uselist=False)
    
    def is_within_geofence(self, latitude, longitude):
        """
        Check if given GPS coordinates are within geofence
        Uses Haversine formula to calculate distance
        Returns: (bool, distance_meters)
        """
        distance = self.calculate_distance(latitude, longitude)
        allowed_distance = self.radius_meters + self.tolerance_meters
        return distance <= allowed_distance, distance
    
    def calculate_distance(self, latitude, longitude):
        """
        Calculate distance between geofence center and given point
        Uses Haversine formula
        Returns: distance in meters
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat1 = math.radians(float(self.center_latitude))
        lon1 = math.radians(float(self.center_longitude))
        lat2 = math.radians(float(latitude))
        lon2 = math.radians(float(longitude))
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return round(distance, 2)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            
            'location': {
                'name': self.location_name,
                'description': self.location_description,
                'center_latitude': float(self.center_latitude),
                'center_longitude': float(self.center_longitude),
                'radius_meters': self.radius_meters,
                'tolerance_meters': self.tolerance_meters,
                'total_allowed_radius': self.radius_meters + self.tolerance_meters
            },
            
            'address': {
                'full_address': self.address,
                'city': self.city,
                'state': self.state,
                'pincode': self.pincode
            },
            
            'settings': {
                'is_active': self.is_active,
                'strict_mode': self.strict_mode
            },
            
            'audit_trail': {
                'created_by': self.created_by,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_by': self.updated_by,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }


class LocationVerification(Base):
    """
    Location Verification Log
    Audit trail of all location verification attempts
    """
    __tablename__ = 'location_verifications'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # User
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Location Submitted
    submitted_latitude = Column(Numeric(10, 7), nullable=False)
    submitted_longitude = Column(Numeric(10, 7), nullable=False)
    submitted_accuracy = Column(Numeric(10, 2))  # GPS accuracy in meters
    
    # Verification Result
    is_verified = Column(Boolean, nullable=False)
    distance_from_center = Column(Numeric(10, 2))  # Meters
    allowed_radius = Column(Integer)  # Geofence radius + tolerance at time of verification
    
    # Context
    action = Column(String(100))  # "TBT_CREATE", "PTW_SUBMIT", "NC_RAISE", etc.
    endpoint = Column(String(200))  # API endpoint called
    request_id = Column(String(100))  # Unique request identifier
    
    # IP & Device
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    device_info = Column(String(200))
    
    # Timestamp
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Audit Trail
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='location_verifications')
    project = relationship('Project', backref='location_verifications')
    user = relationship('User', backref='location_verifications')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            
            'user': {
                'id': self.user_id,
                'name': self.user.name if self.user else None,
                'email': self.user.email if self.user else None
            } if self.user else None,
            
            'location': {
                'latitude': float(self.submitted_latitude),
                'longitude': float(self.submitted_longitude),
                'accuracy': float(self.submitted_accuracy) if self.submitted_accuracy else None
            },
            
            'verification': {
                'is_verified': self.is_verified,
                'distance_from_center': float(self.distance_from_center) if self.distance_from_center else None,
                'allowed_radius': self.allowed_radius,
                'within_geofence': self.is_verified
            },
            
            'context': {
                'action': self.action,
                'endpoint': self.endpoint,
                'request_id': self.request_id
            },
            
            'device': {
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'device_info': self.device_info
            },
            
            'timestamp': self.verified_at.isoformat() if self.verified_at else None
        }
