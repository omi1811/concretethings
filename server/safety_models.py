"""
Safety Module Models - User-Configurable Platform
Similar to DigiQC - provides framework, users create their own forms/checklists
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# ============================================================================
# Core Configuration Models (User-Created)
# ============================================================================

class SafetyModule(Base):
    """
    Main safety modules that can be enabled/disabled per company
    Examples: Checklists, Incidents, Permits, Audits, Training
    """
    __tablename__ = "safety_modules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Module Configuration
    module_type: Mapped[str] = mapped_column(String(50), nullable=False)  # checklist, incident, permit, audit, training, observation
    module_name: Mapped[str] = mapped_column(String(255), nullable=False)  # User-defined name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), default="shield")  # Icon identifier
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_modules")
    project: Mapped[Optional["Project"]] = relationship("Project", backref="safety_modules")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "project_id": self.project_id,
            "module_type": self.module_type,
            "module_name": self.module_name,
            "description": self.description,
            "icon": self.icon,
            "is_active": self.is_active,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FormTemplate(Base):
    """
    User-created form templates (checklists, permits, audits, etc.)
    Highly flexible - users define their own fields and structure
    """
    __tablename__ = "safety_form_templates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_modules.id"), nullable=False)
    
    # Template Info
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # User-defined code
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # User-defined category
    
    # Form Structure (JSON) - User defines fields
    # Example: [{"type": "text", "label": "Site Name", "required": true}, ...]
    form_fields: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Scoring & Validation
    has_scoring: Mapped[bool] = mapped_column(Boolean, default=False)
    scoring_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Custom scoring rules
    
    # Workflow
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approval_levels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Multi-level approvals
    
    # Auto-assignment
    auto_assign: Mapped[bool] = mapped_column(Boolean, default=False)
    assignment_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Contractor, supervisor, etc.
    
    # Frequency & Scheduling
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Daily, weekly, etc.
    
    # Version Control
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_form_templates.id"), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_form_templates")
    project: Mapped[Optional["Project"]] = relationship("Project", backref="safety_form_templates")
    module: Mapped["SafetyModule"] = relationship("SafetyModule", backref="form_templates")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "project_id": self.project_id,
            "module_id": self.module_id,
            "template_name": self.template_name,
            "template_code": self.template_code,
            "description": self.description,
            "category": self.category,
            "form_fields": self.form_fields,
            "has_scoring": self.has_scoring,
            "scoring_config": self.scoring_config,
            "requires_approval": self.requires_approval,
            "approval_levels": self.approval_levels,
            "version": self.version,
            "is_latest": self.is_latest,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# Form Submissions (Data Captured)
# ============================================================================

class FormSubmission(Base):
    """
    Actual form submissions - flexible to accommodate any template
    """
    __tablename__ = "safety_form_submissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_form_templates.id"), nullable=False)
    
    # Submission Data
    submission_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    form_data: Mapped[dict] = mapped_column(JSON, nullable=False)  # User-entered data matching template fields
    
    # Location & Context
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    geo_location: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {lat, lon}
    
    # Media Attachments
    photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Array of photo URLs
    videos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    documents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Scoring (if applicable)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status & Workflow
    status: Mapped[str] = mapped_column(String(50), default="submitted")  # submitted, approved, rejected, closed
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low, medium, high, critical
    
    # Approvals
    approval_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    approvals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Track multi-level approvals
    
    # Due Date & SLA
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_submissions")
    project: Mapped["Project"] = relationship("Project", backref="safety_submissions")
    template: Mapped["FormTemplate"] = relationship("FormTemplate", backref="submissions")
    submitter: Mapped["User"] = relationship("User", foreign_keys=[submitted_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "submission_number": self.submission_number,
            "company_id": self.company_id,
            "project_id": self.project_id,
            "template_id": self.template_id,
            "form_data": self.form_data,
            "location": self.location,
            "geo_location": self.geo_location,
            "photos": self.photos,
            "videos": self.videos,
            "score": self.score,
            "score_percentage": self.score_percentage,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "submitted_by": self.submitted_by,
        }


# ============================================================================
# Worker Management
# ============================================================================

class Worker(Base):
    """
    Workers/Personnel database with attendance and safety tracking
    """
    __tablename__ = "safety_workers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Worker Info
    worker_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Employment
    contractor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    skill_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Safety Training & Certifications
    training_records: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # QR/NFC for Attendance
    qr_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nfc_tag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    joined_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_workers")
    project: Mapped[Optional["Project"]] = relationship("Project", backref="safety_workers")
    
    def to_dict(self):
        return {
            "id": self.id,
            "worker_code": self.worker_code,
            "full_name": self.full_name,
            "phone": self.phone,
            "contractor": self.contractor,
            "skill_category": self.skill_category,
            "designation": self.designation,
            "training_records": self.training_records,
            "certifications": self.certifications,
            "is_active": self.is_active,
            "joined_date": self.joined_date.isoformat() if self.joined_date else None,
        }


class WorkerAttendance(Base):
    """
    Daily worker attendance with safety logs
    """
    __tablename__ = "safety_worker_attendance"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    worker_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_workers.id"), nullable=False)
    
    # Attendance
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Method
    check_in_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # qr, nfc, gps, manual
    check_in_location: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # PPE Verification
    ppe_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    ppe_items_checked: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {helmet: true, gloves: true, ...}
    ppe_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Safety Induction
    induction_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    induction_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    worker: Mapped["Worker"] = relationship("Worker", backref="attendance_records")
    company: Mapped["Company"] = relationship("Company", backref="worker_attendance")
    project: Mapped["Project"] = relationship("Project", backref="worker_attendance")
    
    def to_dict(self):
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "date": self.date.isoformat() if self.date else None,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "check_in_method": self.check_in_method,
            "ppe_verified": self.ppe_verified,
            "ppe_items_checked": self.ppe_items_checked,
            "induction_completed": self.induction_completed,
        }


# ============================================================================
# Actions & Follow-ups
# ============================================================================

class SafetyAction(Base):
    """
    Actions arising from form submissions (incidents, audits, observations)
    """
    __tablename__ = "safety_actions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("safety_form_submissions.id"), nullable=False)
    
    # Action Details
    action_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Priority & Due Date
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="open")  # open, in_progress, completed, overdue
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completion_photos: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # SLA Tracking
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", backref="safety_actions")
    project: Mapped["Project"] = relationship("Project", backref="safety_actions")
    submission: Mapped["FormSubmission"] = relationship("FormSubmission", backref="actions")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assigned_to])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "action_number": self.action_number,
            "action_description": self.action_description,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
