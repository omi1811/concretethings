"""
Non-Conformance (NC) Management for Safety Module
Handles NC lifecycle: Creation → Assignment → Notification → Action → Verification → Closure
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class NonConformance(Base):
    """
    Non-Conformance Records for Safety Module
    Can be created from any form submission (incident, audit, observation, etc.)
    """
    __tablename__ = "safety_non_conformances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    submission_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_form_submissions.id"), nullable=True)
    
    # NC Identification
    nc_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nc_title: Mapped[str] = mapped_column(String(255), nullable=False)
    nc_description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Severity & Category
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # minor, major, critical
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # safety_violation, quality_issue, etc.
    
    # Assignment & Responsibility
    assigned_to_contractor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Contractor name
    assigned_to_user: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Specific person
    
    # Location & Evidence
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    geo_location: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence_photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Photos showing NC
    evidence_videos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Root Cause Analysis
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    immediate_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Corrective Actions
    proposed_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # By contractor
    approved_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # By safety officer
    
    # Action Implementation
    action_taken: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Photos showing correction
    action_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Verification
    verification_status: Mapped[str] = mapped_column(String(50), default="pending_action")
    # Status flow: pending_action → action_submitted → verified → closed → rejected
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Closure
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closure_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # SLA & Escalation
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    
    # Notifications
    notifications_sent: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Track notification history
    
    # Timestamps
    raised_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    raised_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_ncs")
    project: Mapped["Project"] = relationship("Project", backref="safety_ncs")
    submission: Mapped[Optional["FormSubmission"]] = relationship("FormSubmission", backref="non_conformances")
    raiser: Mapped["User"] = relationship("User", foreign_keys=[raised_by])
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_user])
    verifier: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by])
    closer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[closed_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "nc_number": self.nc_number,
            "nc_title": self.nc_title,
            "nc_description": self.nc_description,
            "severity": self.severity,
            "category": self.category,
            "assigned_to_contractor": self.assigned_to_contractor,
            "assigned_to_user": self.assigned_to_user,
            "location": self.location,
            "geo_location": self.geo_location,
            "evidence_photos": self.evidence_photos,
            "root_cause": self.root_cause,
            "proposed_action": self.proposed_action,
            "approved_action": self.approved_action,
            "action_taken": self.action_taken,
            "action_photos": self.action_photos,
            "verification_status": self.verification_status,
            "is_closed": self.is_closed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue,
            "raised_at": self.raised_at.isoformat() if self.raised_at else None,
            "raised_by": self.raised_by,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class NCComment(Base):
    """
    Comments/discussions on NC between safety officer and contractor
    """
    __tablename__ = "safety_nc_comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nc_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_non_conformances.id"), nullable=False)
    
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Photos/docs
    
    # Author
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    nc: Mapped["NonConformance"] = relationship("NonConformance", backref="comments")
    author: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "nc_id": self.nc_id,
            "comment_text": self.comment_text,
            "attachments": self.attachments,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ContractorNotification(Base):
    """
    Notification log for contractors
    Tracks all notifications sent (WhatsApp, Email, In-app)
    """
    __tablename__ = "safety_contractor_notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Notification Details
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # nc_raised, nc_overdue, nc_rejected, etc.
    notification_channel: Mapped[str] = mapped_column(String(20), nullable=False)  # whatsapp, email, in_app
    
    # Recipient
    recipient_contractor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_user: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Related Entity
    nc_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_non_conformances.id"), nullable=True)
    action_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_actions.id"), nullable=True)
    
    # Message Content
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Delivery Status
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivery_status: Mapped[str] = mapped_column(String(20), default="sent")  # sent, delivered, failed, read
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="contractor_notifications")
    project: Mapped["Project"] = relationship("Project", backref="contractor_notifications")
    nc: Mapped[Optional["NonConformance"]] = relationship("NonConformance", backref="notifications")
    recipient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recipient_user])
    
    def to_dict(self):
        return {
            "id": self.id,
            "notification_type": self.notification_type,
            "notification_channel": self.notification_channel,
            "recipient_contractor": self.recipient_contractor,
            "subject": self.subject,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivery_status": self.delivery_status,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
