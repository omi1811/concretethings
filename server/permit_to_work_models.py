"""
Permit-to-Work (PTW) System Models
Based on ISO 45001:2018 Occupational Health and Safety Management Systems
and common industry best practices (no copyrighted content)

Multi-signature workflow:
1. Contractor requests permit
2. Site Engineer reviews and approves
3. Safety Officer final approval
4. Work authorized to proceed
5. Contractor closes permit after completion
6. Final sign-off by authorized personnel
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean, ForeignKey, JSON, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class PermitType(Base):
    """
    Types of work permits (configurable per company)
    Examples: Hot Work, Confined Space, Working at Height, Electrical, Excavation
    """
    __tablename__ = "permit_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Permit Type Details
    permit_type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    permit_code: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., HW, CS, WAH
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, critical
    
    # Requirements (JSON)
    required_ppe: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    safety_precautions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    required_equipment: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Approval Requirements
    requires_site_engineer: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_safety_officer: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_area_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    max_validity_hours: Mapped[int] = mapped_column(Integer, default=8)  # Default 8 hours
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="permit_types")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "permit_type_name": self.permit_type_name,
            "permit_code": self.permit_code,
            "description": self.description,
            "risk_level": self.risk_level,
            "required_ppe": self.required_ppe,
            "max_validity_hours": self.max_validity_hours,
            "requires_site_engineer": self.requires_site_engineer,
            "requires_safety_officer": self.requires_safety_officer,
        }


class WorkPermit(Base):
    """
    Main Work Permit (PTW) with multi-signature workflow
    """
    __tablename__ = "work_permits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    permit_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("permit_types.id"), nullable=False)
    
    # Permit Identification
    permit_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    work_description: Mapped[str] = mapped_column(Text, nullable=False)
    work_location: Mapped[str] = mapped_column(String(255), nullable=False)
    geo_location: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Contractor Details
    contractor_company: Mapped[str] = mapped_column(String(255), nullable=False)
    contractor_supervisor: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    contractor_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    number_of_workers: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Work Schedule
    work_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    estimated_duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Validity Period
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Hazards & Precautions
    identified_hazards: Mapped[dict] = mapped_column(JSON, nullable=False)  # List of hazards
    safety_measures: Mapped[dict] = mapped_column(JSON, nullable=False)  # Precautions taken
    ppe_required: Mapped[dict] = mapped_column(JSON, nullable=False)  # PPE list
    equipment_checklist: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Isolation/Lock-out Tag-out (LOTO)
    requires_isolation: Mapped[bool] = mapped_column(Boolean, default=False)
    isolation_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Emergency Information
    emergency_contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    emergency_contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    nearest_hospital: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_aid_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status & Workflow
    status: Mapped[str] = mapped_column(String(50), default="draft")
    # Status flow: draft → submitted → site_engineer_review → safety_officer_review → approved → in_progress → suspended → completed → closed
    workflow_stage: Mapped[str] = mapped_column(String(50), default="contractor_request")
    
    # Attachments
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Risk assessments, method statements
    photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    work_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    work_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Suspension/Cancellation
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspension_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    suspended_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="work_permits")
    project: Mapped["Project"] = relationship("Project", backref="work_permits")
    permit_type: Mapped["PermitType"] = relationship("PermitType", backref="work_permits")
    contractor: Mapped["User"] = relationship("User", foreign_keys=[contractor_supervisor])
    suspender: Mapped[Optional["User"]] = relationship("User", foreign_keys=[suspended_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "permit_number": self.permit_number,
            "work_description": self.work_description,
            "work_location": self.work_location,
            "contractor_company": self.contractor_company,
            "work_date": self.work_date.isoformat() if self.work_date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "workflow_stage": self.workflow_stage,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_expired": self.is_expired,
        }


class PermitSignature(Base):
    """
    Digital signatures for multi-level approval
    Creates a complete audit trail of who signed when
    """
    __tablename__ = "permit_signatures"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_permits.id"), nullable=False)
    
    # Signer Details
    signer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    # Roles: contractor, site_engineer, safety_officer, area_owner, closing_contractor, closing_engineer
    signer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    signer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    signer_designation: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Signature Details
    signature_type: Mapped[str] = mapped_column(String(50), default="digital")  # digital, drawn, typed
    signature_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Base64 image or text
    
    # Action
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    # Actions: request, approve, reject, suspend, resume, close, verify_closure
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # IP & Device Info (for audit)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamp
    signed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    permit: Mapped["WorkPermit"] = relationship("WorkPermit", backref="signatures")
    signer: Mapped["User"] = relationship("User", foreign_keys=[signer_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "permit_id": self.permit_id,
            "signer_role": self.signer_role,
            "signer_name": self.signer_name,
            "signer_designation": self.signer_designation,
            "action": self.action,
            "comments": self.comments,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
        }


class PermitExtension(Base):
    """
    Permit time extensions (if work takes longer than planned)
    Requires re-approval
    """
    __tablename__ = "permit_extensions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_permits.id"), nullable=False)
    
    # Extension Request
    requested_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    extension_reason: Mapped[str] = mapped_column(Text, nullable=False)
    extended_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    additional_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Approval
    approval_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approval_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    permit: Mapped["WorkPermit"] = relationship("WorkPermit", backref="extensions")
    requester: Mapped["User"] = relationship("User", foreign_keys=[requested_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "extension_reason": self.extension_reason,
            "extended_until": self.extended_until.isoformat() if self.extended_until else None,
            "additional_hours": self.additional_hours,
            "approval_status": self.approval_status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
        }


class PermitChecklist(Base):
    """
    Safety checklist items to be verified before permit approval
    """
    __tablename__ = "permit_checklists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_permits.id"), nullable=False)
    
    # Checklist Item
    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Photo Evidence
    verification_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    permit: Mapped["WorkPermit"] = relationship("WorkPermit", backref="checklists")
    verifier: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "item_description": self.item_description,
            "is_mandatory": self.is_mandatory,
            "is_verified": self.is_verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }


class PermitAuditLog(Base):
    """
    Complete audit trail of all permit actions
    """
    __tablename__ = "permit_audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_permits.id"), nullable=False)
    
    # Action Details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Previous & New State
    previous_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    action_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permit: Mapped["WorkPermit"] = relationship("WorkPermit", backref="audit_logs")
    performer: Mapped["User"] = relationship("User", foreign_keys=[performed_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "action_description": self.action_description,
            "action_timestamp": self.action_timestamp.isoformat() if self.action_timestamp else None,
        }
