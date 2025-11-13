"""
Toolbox Talk (TBT) Enhanced Models with QR Code Attendance

Enhanced models for TBT with:
- Link to conductor (User who conducts TBT)
- Worker attendance via QR code scanning
- Session management
- Attendance verification
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from .db import Base
except ImportError:
    from db import Base


class TBTSession(Base):
    """
    Toolbox Talk Session
    Represents a single TBT briefing session with conductor and location details
    """
    __tablename__ = "tbt_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Conductor (person conducting the TBT)
    conductor_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    conductor_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Cached for display
    conductor_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Site Engineer, Safety Officer, etc.
    
    # Session details
    session_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)  # "Concrete Pouring Safety", "Working at Height"
    topic_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # General, Activity-Specific, Environmental
    
    # Location and activity
    location: Mapped[str] = mapped_column(String(255), nullable=False)  # "Block A, Floor 5, Column C-D/3-4"
    activity: Mapped[str] = mapped_column(String(100), nullable=False)  # Concreting, Scaffolding, Blockwork, etc.
    
    # Duration
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    
    # Session content
    key_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of discussion points
    hazards_discussed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of hazards
    ppe_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of PPE items
    emergency_contacts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object
    
    # Group photo (mandatory)
    photo_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # For cloud storage
    
    # Additional information
    weather_conditions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # "Clear, 28°C"
    special_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Any special remarks
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")  # draft, active, completed
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # QR Code for attendance (unique per session)
    qr_code_data: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # URL or unique token for QR
    qr_code_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="tbt_sessions")
    conductor = relationship("User", foreign_keys=[conductor_id], backref="tbt_sessions_conducted")
    attendances = relationship("TBTAttendance", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self, include_attendances=False) -> dict:
        import json
        
        result = {
            "id": self.id,
            "projectId": self.project_id,
            "conductorId": self.conductor_id,
            "conductorName": self.conductor_name,
            "conductorRole": self.conductor_role,
            "sessionDate": self.session_date.isoformat(),
            "topic": self.topic,
            "topicCategory": self.topic_category,
            "location": self.location,
            "activity": self.activity,
            "durationMinutes": self.duration_minutes,
            "keyPoints": json.loads(self.key_points) if self.key_points else [],
            "hazardsDiscussed": json.loads(self.hazards_discussed) if self.hazards_discussed else [],
            "ppeRequired": json.loads(self.ppe_required) if self.ppe_required else [],
            "emergencyContacts": json.loads(self.emergency_contacts) if self.emergency_contacts else {},
            "photoFilename": self.photo_filename,
            "photoUrl": self.photo_url,
            "weatherConditions": self.weather_conditions,
            "specialNotes": self.special_notes,
            "status": self.status,
            "isCompleted": self.is_completed,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "qrCodeData": self.qr_code_data,
            "qrCodeExpiresAt": self.qr_code_expires_at.isoformat() if self.qr_code_expires_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "attendanceCount": len(self.attendances) if self.attendances else 0
        }
        
        if include_attendances:
            result["attendances"] = [att.to_dict() for att in self.attendances]
        
        return result


class TBTAttendance(Base):
    """
    TBT Attendance Record
    Tracks individual worker attendance at TBT sessions via QR code scanning
    """
    __tablename__ = "tbt_attendances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbt_sessions.id"), nullable=False)
    
    # Worker details (supports both registered workers and manual entry)
    worker_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_workers.id"), nullable=True)
    worker_name: Mapped[str] = mapped_column(String(255), nullable=False)
    worker_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Worker ID/Employee number
    worker_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Contractor company
    worker_trade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Mason, Steel Fixer, etc.
    
    # Attendance method
    check_in_method: Mapped[str] = mapped_column(String(50), nullable=False, default="qr")  # qr, manual, nfc
    check_in_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # QR Code verification
    qr_code_scanned: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # QR code that was scanned
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Device used for check-in
    
    # Signature (for verification)
    has_signed: Mapped[bool] = mapped_column(Boolean, default=True)
    signature_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional info
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("TBTSession", back_populates="attendances")
    worker = relationship("Worker", foreign_keys=[worker_id])
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "workerId": self.worker_id,
            "workerName": self.worker_name,
            "workerCode": self.worker_code,
            "workerCompany": self.worker_company,
            "workerTrade": self.worker_trade,
            "checkInMethod": self.check_in_method,
            "checkInTime": self.check_in_time.isoformat(),
            "qrCodeScanned": self.qr_code_scanned,
            "deviceInfo": self.device_info,
            "hasSigned": self.has_signed,
            "signatureTimestamp": self.signature_timestamp.isoformat() if self.signature_timestamp else None,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat()
        }


class TBTTopic(Base):
    """
    TBT Topic Library
    Pre-defined topics for quick TBT creation
    """
    __tablename__ = "tbt_topics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)  # NULL = global
    
    # Topic details
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # General, Activity-Specific, Environmental, Health
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Template content (JSON arrays)
    key_points_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    hazards_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    ppe_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)  # Track popularity
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", backref="tbt_topics")
    
    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "companyId": self.company_id,
            "topicName": self.topic_name,
            "category": self.category,
            "description": self.description,
            "keyPointsTemplate": json.loads(self.key_points_template) if self.key_points_template else [],
            "hazardsTemplate": json.loads(self.hazards_template) if self.hazards_template else [],
            "ppeTemplate": json.loads(self.ppe_template) if self.ppe_template else [],
            "isActive": self.is_active,
            "usageCount": self.usage_count,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
