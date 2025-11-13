from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, LargeBinary, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from .db import Base, SessionLocal
except ImportError:
    from db import Base, SessionLocal


# Database session wrapper for backward compatibility with Flask-SQLAlchemy style code
class _DBWrapper:
    """
    Wrapper to provide db.session compatibility for legacy code.
    New code should use session_scope() context manager instead.
    
    This uses SQLAlchemy's scoped_session which is thread-local and request-safe.
    """
    @property
    def session(self):
        """Returns the scoped session (thread-local, auto-managed by SQLAlchemy)."""
        return SessionLocal

# Create a global db instance for backward compatibility
db = _DBWrapper()


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Multi-App Subscription Model
    # subscribed_apps: JSON array of app names: ["safety"], ["concrete"], or ["safety", "concrete"]
    subscribed_apps: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default='["safety", "concrete"]')  # JSON array
    
    # SaaS Pricing Model - Project-based subscription
    subscription_plan: Mapped[str] = mapped_column(String(50), default="trial")  # trial, basic, pro, enterprise
    active_projects_limit: Mapped[int] = mapped_column(Integer, default=1)  # Number of projects allowed
    price_per_project: Mapped[float] = mapped_column(Float, default=5000.0)  # ₹5000/month per project
    
    # Billing & Status
    billing_status: Mapped[str] = mapped_column(String(50), default="active")  # active, suspended, cancelled
    subscription_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_billing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Company Details
    company_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    company_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # GST Number
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        import json as json_module
        return {
            "id": self.id,
            "name": self.name,
            "subscribedApps": json_module.loads(self.subscribed_apps) if self.subscribed_apps else ["safety", "concrete"],
            "subscriptionPlan": self.subscription_plan,
            "activeProjectsLimit": self.active_projects_limit,
            "pricePerProject": self.price_per_project,
            "billingStatus": self.billing_status,
            "subscriptionStartDate": self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            "subscriptionEndDate": self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            "lastPaymentDate": self.last_payment_date.isoformat() if self.last_payment_date else None,
            "nextBillingDate": self.next_billing_date.isoformat() if self.next_billing_date else None,
            "companyEmail": self.company_email,
            "companyPhone": self.company_phone,
            "companyAddress": self.company_address,
            "gstin": self.gstin,
            "isActive": bool(self.is_active),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
    
    def has_app(self, app_name: str) -> bool:
        """Check if company has subscribed to specific app"""
        import json as json_module
        apps = json_module.loads(self.subscribed_apps) if self.subscribed_apps else []
        return app_name in apps
    
    def has_both_apps(self) -> bool:
        """Check if company has both safety and concrete apps"""
        import json as json_module
        apps = json_module.loads(self.subscribed_apps) if self.subscribed_apps else []
        return "safety" in apps and "concrete" in apps


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # Mandatory phone number
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Company Association
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Global Roles (DigiQC-style hierarchy)
    is_support_admin: Mapped[bool] = mapped_column(Integer, default=0)  # YOU - Super admin across all companies
    is_company_admin: Mapped[bool] = mapped_column(Integer, default=0)  # Company admin - manages projects
    is_system_admin: Mapped[bool] = mapped_column(Integer, default=0)  # DEPRECATED - use is_support_admin
    
    # User Details
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Site Engineer, QC Manager, etc.
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # URL or path
    
    # Status & Security
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    is_email_verified: Mapped[bool] = mapped_column(Integer, default=0)
    is_phone_verified: Mapped[bool] = mapped_column(Integer, default=0)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    account_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Activity Tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Who invited this user

    company = relationship("Company", backref="users")

    def to_dict(self, include_sensitive=False) -> dict:
        data = {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "fullName": self.full_name,
            "designation": self.designation,
            "profilePhoto": self.profile_photo,
            "companyId": self.company_id,
            "isSupportAdmin": bool(self.is_support_admin),
            "isCompanyAdmin": bool(self.is_company_admin),
            "isSystemAdmin": bool(self.is_system_admin),  # Backward compatibility
            "isActive": bool(self.is_active),
            "isEmailVerified": bool(self.is_email_verified),
            "isPhoneVerified": bool(self.is_phone_verified),
            "lastLogin": self.last_login.isoformat() if self.last_login else None,
            "lastActivity": self.last_activity.isoformat() if self.last_activity else None,
            "createdAt": self.created_at.isoformat(),
            "createdBy": self.created_by
        }
        if include_sensitive:
            data["failedLoginAttempts"] = self.failed_login_attempts
            data["accountLockedUntil"] = self.account_locked_until.isoformat() if self.account_locked_until else None
        return data


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Project Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)  # e.g., PRJ-2025-001
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Project Dates
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Project Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, on-hold, completed, cancelled
    is_active: Mapped[bool] = mapped_column(Integer, default=1)  # Counts towards billing if True
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    company = relationship("Company", backref="projects")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "companyId": self.company_id,
            "name": self.name,
            "projectCode": self.project_code,
            "description": self.description,
            "location": self.location,
            "clientName": self.client_name,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "actualEndDate": self.actual_end_date.isoformat() if self.actual_end_date else None,
            "status": self.status,
            "isActive": bool(self.is_active),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by
        }


class ProjectMembership(Base):
    """
    DigiQC-style project membership with granular roles and permissions.
    Roles: ProjectAdmin, QualityManager, QualityEngineer, SiteEngineer, DataEntry, Viewer
    """
    __tablename__ = "project_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Role Assignment (DigiQC-style)
    role: Mapped[str] = mapped_column(String(64), default="Viewer")
    # Roles:
    # - ProjectAdmin: Full project control, approve all data
    # - QualityManager: Verify tests, approve results, manage QC team
    # - QualityEngineer: Perform tests, enter data, upload photos
    # - SiteEngineer: View data, enter batch info, limited editing
    # - DataEntry: Basic data entry only
    # - Watchman: Material vehicle register ONLY, no other features
    # - Viewer: Read-only access
    # - RMCVendor: View own batches only
    
    # Granular Permissions (can override role defaults)
    can_create_batch: Mapped[bool] = mapped_column(Integer, default=1)
    can_edit_batch: Mapped[bool] = mapped_column(Integer, default=1)
    can_delete_batch: Mapped[bool] = mapped_column(Integer, default=0)
    can_approve_batch: Mapped[bool] = mapped_column(Integer, default=0)
    
    can_create_test: Mapped[bool] = mapped_column(Integer, default=1)
    can_edit_test: Mapped[bool] = mapped_column(Integer, default=1)
    can_delete_test: Mapped[bool] = mapped_column(Integer, default=0)
    can_approve_test: Mapped[bool] = mapped_column(Integer, default=0)
    
    can_manage_team: Mapped[bool] = mapped_column(Integer, default=0)
    can_generate_reports: Mapped[bool] = mapped_column(Integer, default=1)
    can_export_data: Mapped[bool] = mapped_column(Integer, default=0)
    can_manage_settings: Mapped[bool] = mapped_column(Integer, default=0)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    added_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", backref="memberships")
    user = relationship("User", backref="memberships", foreign_keys=[user_id])
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "userId": self.user_id,
            "role": self.role,
            "permissions": {
                "canCreateBatch": bool(self.can_create_batch),
                "canEditBatch": bool(self.can_edit_batch),
                "canDeleteBatch": bool(self.can_delete_batch),
                "canApproveBatch": bool(self.can_approve_batch),
                "canCreateTest": bool(self.can_create_test),
                "canEditTest": bool(self.can_edit_test),
                "canDeleteTest": bool(self.can_delete_test),
                "canApproveTest": bool(self.can_approve_test),
                "canManageTeam": bool(self.can_manage_team),
                "canGenerateReports": bool(self.can_generate_reports),
                "canExportData": bool(self.can_export_data),
                "canManageSettings": bool(self.can_manage_settings)
            },
            "isActive": bool(self.is_active),
            "joinedAt": self.joined_at.isoformat(),
            "addedBy": self.added_by
        }


class RMCVendor(Base):
    """
    Ready-Mix Concrete Vendor/Supplier Management.
    Each vendor can supply multiple mix designs.
    """
    __tablename__ = "rmc_vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Vendor Details
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Business Details
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    is_approved: Mapped[bool] = mapped_column(Integer, default=0)  # Quality approval
    
    # Data Protection - Soft Delete Only
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    company = relationship("Company", backref="rmc_vendors")
    project = relationship("Project", backref="rmc_vendors")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "companyId": self.company_id,
            "projectId": self.project_id,
            "vendorName": self.vendor_name,
            "contactPersonName": self.contact_person_name,
            "contactPhone": self.contact_phone,
            "contactEmail": self.contact_email,
            "address": self.address,
            "licenseNumber": self.license_number,
            "gstin": self.gstin,
            "isActive": bool(self.is_active),
            "isApproved": bool(self.is_approved),
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "createdAt": self.created_at.isoformat(),
            "approvedAt": self.approved_at.isoformat() if self.approved_at else None
        }


class MixDesign(Base):
    __tablename__ = "mix_designs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    rmc_vendor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rmc_vendors.id"), nullable=True)
    
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mix_design_id: Mapped[str] = mapped_column(String(255), nullable=False)
    specified_strength_psi: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # ISO 22965-2:2021 - Concrete Grade with Special Properties
    concrete_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # M20, M30, M40FF (Free Flow/SCC)
    is_self_compacting: Mapped[bool] = mapped_column(Integer, default=0)  # True for FF (Free Flow) grades
    is_free_flow: Mapped[bool] = mapped_column(Integer, default=0)  # SCC/FF indicator

    slump_inches: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    air_content_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    batch_volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # 'cubic_yards' | 'cubic_meters'

    materials: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File storage
    document_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Image storage (for thumbnails or small images)
    image_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    image_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # Store small images in DB
    image_mimetype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Quality Approval Workflow
    uploaded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Integer, default=0)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Data Protection - Soft Delete Only
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", backref="mix_designs")
    rmc_vendor = relationship("RMCVendor", backref="mix_designs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "rmcVendorId": self.rmc_vendor_id,
            "projectName": self.project_name,
            "mixDesignId": self.mix_design_id,
            "specifiedStrengthPsi": self.specified_strength_psi,
            "slumpInches": self.slump_inches,
            "airContentPercent": self.air_content_percent,
            "batchVolume": self.batch_volume,
            "volumeUnit": self.volume_unit,
            "materials": self.materials,
            "notes": self.notes,
            "documentName": self.document_name,
            "ocrText": self.ocr_text,
            "imageName": self.image_name,
            "hasImage": self.image_data is not None,
            "isApproved": bool(self.is_approved),
            "uploadedBy": self.uploaded_by,
            "approvedBy": self.approved_by,
            "approvedAt": self.approved_at.isoformat() if self.approved_at else None,
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


class PourActivity(Base):
    """
    Pour Activity/Concrete Pour Register - Groups multiple batches for a single concrete pour.
    Represents one pouring activity (e.g., "Slab on Grid A-12, Level 5").
    Multiple vehicles/batches can be linked to one pour activity.
    """
    __tablename__ = "pour_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Pour Identification
    pour_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)  # e.g., POUR-2025-001
    pour_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Location Details (where concrete is poured)
    building_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    floor_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    zone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    grid_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    structural_element_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Beam/Column/Slab/Footing/Wall
    element_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Concrete Details
    concrete_type: Mapped[str] = mapped_column(String(20), default="Normal")  # Normal or PT (Post-Tensioned)
    design_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., M30, M40
    total_quantity_planned: Mapped[float] = mapped_column(Float, nullable=False)  # Total m³ planned
    total_quantity_received: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Actual total from batches
    
    # Pour Status
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress/completed/cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Workflow
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    completed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", backref="pour_activities")
    batches = relationship("BatchRegister", back_populates="pour_activity")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "pourId": self.pour_id,
            "pourDate": self.pour_date.isoformat(),
            "location": {
                "buildingName": self.building_name,
                "floorLevel": self.floor_level,
                "zone": self.zone,
                "gridReference": self.grid_reference,
                "structuralElementType": self.structural_element_type,
                "elementId": self.element_id,
                "description": self.location_description
            },
            "concreteType": self.concrete_type,
            "designGrade": self.design_grade,
            "totalQuantityPlanned": self.total_quantity_planned,
            "totalQuantityReceived": self.total_quantity_received,
            "status": self.status,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdBy": self.created_by,
            "completedBy": self.completed_by,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


class BatchRegister(Base):
    """
    Batch/Delivery Register - Records RMC deliveries with mandatory batch sheet photo.
    Entry persons create, Quality persons verify.
    """
    __tablename__ = "batch_registers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    mix_design_id: Mapped[int] = mapped_column(Integer, ForeignKey("mix_designs.id"), nullable=False)
    rmc_vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("rmc_vendors.id"), nullable=False)
    
    # Link to Pour Activity (optional - batch can be standalone or part of a pour)
    pour_activity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("pour_activities.id"), nullable=True)
    
    # Batch Details
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    delivery_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    delivery_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # HH:MM format
    quantity_ordered: Mapped[float] = mapped_column(Float, nullable=False)  # in cubic meters/yards
    quantity_received: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Batch Sheet Documentation (MANDATORY)
    batch_sheet_photo_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    batch_sheet_photo_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    batch_sheet_photo_mimetype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Delivery Details
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    driver_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Concrete temp on arrival
    slump_tested: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Actual slump
    
    # Detailed Location Tracking (User must specify where concrete is poured)
    building_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # e.g., "Tower A", "Block 1"
    floor_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Ground Floor", "Level 5", "Basement 2"
    zone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "North Wing", "East Zone"
    grid_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Grid A-12 to A-15"
    structural_element_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Beam/Column/Slab/Footing/Wall
    element_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Column C-12", "Beam B-45"
    pour_location_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Detailed description
    
    # GPS Coordinates (Optional but useful)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Entry & Verification Workflow
    entered_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # Entry person
    verification_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/rejected
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Quality person
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data Protection - Soft Delete Only
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", backref="batch_registers")
    mix_design = relationship("MixDesign", backref="batch_registers")
    rmc_vendor = relationship("RMCVendor", backref="batch_registers")
    pour_activity = relationship("PourActivity", back_populates="batches")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "mixDesignId": self.mix_design_id,
            "rmcVendorId": self.rmc_vendor_id,
            "pourActivityId": self.pour_activity_id,
            "batchNumber": self.batch_number,
            "deliveryDate": self.delivery_date.isoformat(),
            "deliveryTime": self.delivery_time,
            "quantityOrdered": self.quantity_ordered,
            "quantityReceived": self.quantity_received,
            "hasBatchSheetPhoto": self.batch_sheet_photo_data is not None,
            "vehicleNumber": self.vehicle_number,
            "driverName": self.driver_name,
            "temperatureCelsius": self.temperature_celsius,
            "slumpTested": self.slump_tested,
            "location": {
                "buildingName": self.building_name,
                "floorLevel": self.floor_level,
                "zone": self.zone,
                "gridReference": self.grid_reference,
                "structuralElementType": self.structural_element_type,
                "elementId": self.element_id,
                "description": self.pour_location_description,
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "enteredBy": self.entered_by,
            "verificationStatus": self.verification_status,
            "verifiedBy": self.verified_by,
            "verifiedAt": self.verified_at.isoformat() if self.verified_at else None,
            "rejectionReason": self.rejection_reason,
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class CubeTestRegister(Base):
    """
    Concrete Cube/Cylinder Test Register per IS 516-1959 / ASTM C39.
    Supports multi-age testing (7-day, 28-day, etc.) with 3 cubes per set.
    Auto-calculates pass/fail and triggers alerts.
    """
    __tablename__ = "cube_test_registers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("batch_registers.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Test Set Identification
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Sequential per batch
    test_age_days: Mapped[int] = mapped_column(Integer, nullable=False)  # 3, 5, 7, 28, 56, 90 (5 for PT concrete)
    cube_identifier: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'A', 'B', 'C' for individual cubes in a set
    
    # Link to Pour Activity (if batch is part of a pour)
    pour_activity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("pour_activities.id"), nullable=True)
    
    # Third-party Testing Assignment
    third_party_lab_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("third_party_labs.id"), nullable=True)
    sent_to_lab_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expected_result_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Casting Details
    casting_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    casting_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cast_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ISO 1920-3:2019 - Structure and Location Details
    structure_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Beam/Column/Slab/Wall/Footing
    structure_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Full location description
    
    # ISO 6784-1:2013 - Concrete Grade and Type
    concrete_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # M20, M30, M40FF (Free Flow)
    concrete_type: Mapped[str] = mapped_column(String(20), default="Normal")  # Normal or PT (Post-Tensioned)
    concrete_source: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'RMC' or 'Site Mix'
    
    # ISO 1920-3:2019 - Sample Details
    number_of_cubes: Mapped[int] = mapped_column(Integer, default=3)  # Typically 3 per set (A, B, C)
    sample_identification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Sample ID/Label
    
    # Curing Conditions (ISO 1920-4:2020)
    curing_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Water/Wet burlap/Curing compound
    curing_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Should be 23±2°C
    
    # Testing Details
    testing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    tested_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    testing_machine_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    machine_calibration_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Cube 1 (per IS 516: 150mm x 150mm x 150mm standard cube)
    cube_1_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_1_length_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_1_width_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_1_height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_1_load_kn: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Load at failure
    cube_1_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Calculated strength
    
    # Cube 2
    cube_2_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_length_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_width_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_load_kn: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Cube 3
    cube_3_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_length_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_width_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_load_kn: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Results
    average_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Auto-calculated
    required_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # From mix design
    strength_ratio_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # (actual/required)*100
    pass_fail_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # pass/fail/pending
    
    # Failure Mode (per IS 516)
    failure_mode_cube_1: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Satisfactory/Shear/etc
    failure_mode_cube_2: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failure_mode_cube_3: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Verification & NCR
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Quality Manager
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ncr_generated: Mapped[bool] = mapped_column(Integer, default=0)  # Non-Conformance Report
    ncr_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Integer, default=0)  # WhatsApp alert sent
    
    # ISO 17025:2017 - Digital Signature for Documentation
    tester_signature_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # Digital signature image
    tester_signature_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verifier_signature_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # QM signature
    verifier_signature_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data Protection - Soft Delete Only (CRITICAL DATA - NO PERMANENT DELETE)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batch_register = relationship("BatchRegister", backref="cube_tests")
    project = relationship("Project", backref="cube_tests")
    pour_activity = relationship("PourActivity", backref="cube_tests")

    def calculate_results(self):
        """Auto-calculate average strength and pass/fail status."""
        strengths = []
        if self.cube_1_strength_mpa is not None:
            strengths.append(self.cube_1_strength_mpa)
        if self.cube_2_strength_mpa is not None:
            strengths.append(self.cube_2_strength_mpa)
        if self.cube_3_strength_mpa is not None:
            strengths.append(self.cube_3_strength_mpa)
        
        if strengths:
            self.average_strength_mpa = sum(strengths) / len(strengths)
            
            if self.required_strength_mpa:
                self.strength_ratio_percent = (self.average_strength_mpa / self.required_strength_mpa) * 100
                
                # IS 516 Criteria: Average should be >= required strength
                # Individual cube should not be less than 75% of required strength
                individual_pass = all(s >= (self.required_strength_mpa * 0.75) for s in strengths)
                average_pass = self.average_strength_mpa >= self.required_strength_mpa
                
                if average_pass and individual_pass:
                    self.pass_fail_status = "pass"
                else:
                    self.pass_fail_status = "fail"
            else:
                self.pass_fail_status = "pending"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "batchId": self.batch_id,
            "projectId": self.project_id,
            "setNumber": self.set_number,
            "testAgeDays": self.test_age_days,
            "cubeIdentifier": self.cube_identifier,
            "pourActivityId": self.pour_activity_id,
            "thirdPartyLabId": self.third_party_lab_id,
            "sentToLabDate": self.sent_to_lab_date.isoformat() if self.sent_to_lab_date else None,
            "expectedResultDate": self.expected_result_date.isoformat() if self.expected_result_date else None,
            
            # ISO Compliant Fields
            "castingDate": self.casting_date.isoformat(),
            "castingTime": self.casting_time,
            "castBy": self.cast_by,
            "structureType": self.structure_type,
            "structureLocation": self.structure_location,
            "concreteGrade": self.concrete_grade,
            "concreteType": self.concrete_type,
            "concreteSource": self.concrete_source,
            "numberOfCubes": self.number_of_cubes,
            "sampleIdentification": self.sample_identification,
            
            "curingMethod": self.curing_method,
            "curingTemperature": self.curing_temperature,
            "testingDate": self.testing_date.isoformat() if self.testing_date else None,
            "testedBy": self.tested_by,
            "testingMachineId": self.testing_machine_id,
            "machineCalibrationDate": self.machine_calibration_date.isoformat() if self.machine_calibration_date else None,
            "cube1": {
                "name": "A",
                "weight": self.cube_1_weight_kg,
                "dimensions": {"length": self.cube_1_length_mm, "width": self.cube_1_width_mm, "height": self.cube_1_height_mm},
                "load": self.cube_1_load_kn,
                "strength": self.cube_1_strength_mpa,
                "failureMode": self.failure_mode_cube_1
            },
            "cube2": {
                "name": "B",
                "weight": self.cube_2_weight_kg,
                "dimensions": {"length": self.cube_2_length_mm, "width": self.cube_2_width_mm, "height": self.cube_2_height_mm},
                "load": self.cube_2_load_kn,
                "strength": self.cube_2_strength_mpa,
                "failureMode": self.failure_mode_cube_2
            },
            "cube3": {
                "name": "C",
                "weight": self.cube_3_weight_kg,
                "dimensions": {"length": self.cube_3_length_mm, "width": self.cube_3_width_mm, "height": self.cube_3_height_mm},
                "load": self.cube_3_load_kn,
                "strength": self.cube_3_strength_mpa,
                "failureMode": self.failure_mode_cube_3
            },
            "averageStrengthMpa": self.average_strength_mpa,
            "requiredStrengthMpa": self.required_strength_mpa,
            "strengthRatioPercent": self.strength_ratio_percent,
            "passFailStatus": self.pass_fail_status,
            "verifiedBy": self.verified_by,
            "verifiedAt": self.verified_at.isoformat() if self.verified_at else None,
            "ncrGenerated": bool(self.ncr_generated),
            "ncrNumber": self.ncr_number,
            "notificationSent": bool(self.notification_sent),
            
            # Digital Signatures
            "hasTesterSignature": self.tester_signature_data is not None,
            "testerSignatureTimestamp": self.tester_signature_timestamp.isoformat() if self.tester_signature_timestamp else None,
            "hasVerifierSignature": self.verifier_signature_data is not None,
            "verifierSignatureTimestamp": self.verifier_signature_timestamp.isoformat() if self.verifier_signature_timestamp else None,
            
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


# ============================================================================
# Third-Party Test Register Models (ISO/IEC 17025:2017)
# ============================================================================

class ThirdPartyLab(Base):
    """
    Third-party testing laboratory master.
    ISO/IEC 17025:2017 - Accredited testing laboratories.
    """
    __tablename__ = "third_party_labs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Lab details
    lab_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lab_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    
    # Contact information
    contact_person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Address
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Accreditation details (ISO/IEC 17025)
    nabl_accreditation_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nabl_accreditation_valid_till: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scope_of_accreditation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # e.g., "Concrete, Steel, Soil"
    
    # Approval workflow
    is_approved: Mapped[bool] = mapped_column(Integer, default=0)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    
    # Soft delete (CRITICAL DATA - NO PERMANENT DELETE)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", backref="third_party_labs")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "companyId": self.company_id,
            "labName": self.lab_name,
            "labCode": self.lab_code,
            "contactPerson": {
                "name": self.contact_person_name,
                "phone": self.contact_phone,
                "email": self.contact_email
            },
            "address": {
                "street": self.address,
                "city": self.city,
                "state": self.state,
                "pincode": self.pincode
            },
            "accreditation": {
                "nablNumber": self.nabl_accreditation_number,
                "validTill": self.nabl_accreditation_valid_till.isoformat() if self.nabl_accreditation_valid_till else None,
                "scope": self.scope_of_accreditation
            },
            "isApproved": bool(self.is_approved),
            "approvedBy": self.approved_by,
            "approvedAt": self.approved_at.isoformat() if self.approved_at else None,
            "isActive": bool(self.is_active),
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class ThirdPartyCubeTest(Base):
    """
    Third-party cube test register with certificate photo.
    For concrete tests conducted by external NABL-accredited labs.
    ISO/IEC 17025:2017 compliance.
    """
    __tablename__ = "third_party_cube_tests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("batch_registers.id"), nullable=False)
    lab_id: Mapped[int] = mapped_column(Integer, ForeignKey("third_party_labs.id"), nullable=False)
    
    # Test identification
    lab_test_report_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    test_age_days: Mapped[int] = mapped_column(Integer, nullable=False)  # 7, 28, 56, 90
    
    # Sample details
    sample_collection_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sample_received_at_lab_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    testing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Test results (from certificate)
    number_of_cubes_tested: Mapped[int] = mapped_column(Integer, nullable=False)
    cube_1_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_2_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cube_3_strength_mpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_strength_mpa: Mapped[float] = mapped_column(Float, nullable=False)
    required_strength_mpa: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Pass/Fail (as per lab certificate)
    pass_fail_status: Mapped[str] = mapped_column(String(20), nullable=False)  # 'pass', 'fail'
    
    # MANDATORY: Certificate/Result sheet photo (ISO/IEC 17025 - documented evidence)
    certificate_photo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_photo_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    certificate_photo_mimetype: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Verification by internal quality team
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # NCR tracking (if test fails)
    ncr_generated: Mapped[bool] = mapped_column(Integer, default=0)
    ncr_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    notification_sent: Mapped[bool] = mapped_column(Integer, default=0)
    
    # Soft delete (CRITICAL DATA - NO PERMANENT DELETE)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="third_party_cube_tests")
    batch = relationship("BatchRegister", backref="third_party_cube_tests")
    lab = relationship("ThirdPartyLab", backref="cube_tests")
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "batchId": self.batch_id,
            "labId": self.lab_id,
            "labTestReportNumber": self.lab_test_report_number,
            "testAgeDays": self.test_age_days,
            "sampleDetails": {
                "collectionDate": self.sample_collection_date.isoformat(),
                "receivedAtLabDate": self.sample_received_at_lab_date.isoformat(),
                "testingDate": self.testing_date.isoformat()
            },
            "testResults": {
                "numberOfCubes": self.number_of_cubes_tested,
                "cube1StrengthMpa": self.cube_1_strength_mpa,
                "cube2StrengthMpa": self.cube_2_strength_mpa,
                "cube3StrengthMpa": self.cube_3_strength_mpa,
                "averageStrengthMpa": self.average_strength_mpa,
                "requiredStrengthMpa": self.required_strength_mpa,
                "passFailStatus": self.pass_fail_status
            },
            "certificate": {
                "fileName": self.certificate_photo_name,
                "mimeType": self.certificate_photo_mimetype
            },
            "verification": {
                "verifiedBy": self.verified_by,
                "verifiedAt": self.verified_at.isoformat() if self.verified_at else None,
                "remarks": self.verification_remarks
            },
            "ncr": {
                "generated": bool(self.ncr_generated),
                "number": self.ncr_number,
                "notificationSent": bool(self.notification_sent)
            },
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


# ============================================================================
# Material Testing & Approved Brands (ISO 9001:2015 Clause 8.4)
# ============================================================================

class MaterialCategory(Base):
    """
    Material categories for construction materials.
    ISO 9001:2015 - Clause 8.4 (Control of externally provided processes, products and services)
    """
    __tablename__ = "material_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Category details
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Steel, Glass, Railing, Paint, etc.
    category_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Applicable standards
    applicable_standards: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # e.g., "IS 1786, IS 2062"
    
    # Testing requirements
    requires_testing: Mapped[bool] = mapped_column(Integer, default=1)
    test_frequency: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Per batch", "Per lot"
    
    # Status
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", backref="material_categories")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "companyId": self.company_id,
            "categoryName": self.category_name,
            "categoryCode": self.category_code,
            "description": self.description,
            "applicableStandards": self.applicable_standards,
            "requiresTesting": bool(self.requires_testing),
            "testFrequency": self.test_frequency,
            "isActive": bool(self.is_active),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class ApprovedBrand(Base):
    """
    Approved brands/manufacturers for each material category.
    Company-specific approved vendor list.
    ISO 9001:2015 - Clause 8.4.1 (Evaluation and selection of suppliers)
    """
    __tablename__ = "approved_brands"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_categories.id"), nullable=False)
    
    # Brand details
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Specifications
    grade_specification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Fe 500D", "6mm Clear"
    compliance_standards: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # e.g., "IS 1786:2008, IS 2062:2011"
    
    # Approval details
    approved_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approval_validity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Test certificate (optional - if brand provides type test certificate)
    type_test_certificate_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type_test_certificate_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    type_test_certificate_mimetype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    
    # Remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", backref="approved_brands")
    category = relationship("MaterialCategory", backref="approved_brands")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "companyId": self.company_id,
            "categoryId": self.category_id,
            "brandName": self.brand_name,
            "manufacturerName": self.manufacturer_name,
            "gradeSpecification": self.grade_specification,
            "complianceStandards": self.compliance_standards,
            "approvedBy": self.approved_by,
            "approvedAt": self.approved_at.isoformat(),
            "approvalValidity": self.approval_validity.isoformat() if self.approval_validity else None,
            "hasTypeCertificate": bool(self.type_test_certificate_data),
            "isActive": bool(self.is_active),
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class MaterialTestRegister(Base):
    """
    Material test register for steel, glass, railing, etc.
    Links to third-party lab tests with certificate photos.
    ISO 9001:2015 - Clause 8.6 (Release of products and services)
    """
    __tablename__ = "material_test_registers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_categories.id"), nullable=False)
    brand_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("approved_brands.id"), nullable=True)
    lab_id: Mapped[int] = mapped_column(Integer, ForeignKey("third_party_labs.id"), nullable=False)
    
    # Material identification
    material_description: Mapped[str] = mapped_column(Text, nullable=False)
    grade_specification: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(20), nullable=False)  # MT, SQM, RMT, etc.
    
    # Supplier details
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    batch_lot_number: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Invoice/Challan details
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    invoice_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Location where material is used
    location_description: Mapped[str] = mapped_column(Text, nullable=False)  # e.g., "Building A, 3rd Floor Column"
    
    # Test details
    lab_test_report_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sample_collection_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    testing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Test results (generic - varies by material type)
    test_parameters: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of test parameters
    test_results: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of results
    pass_fail_status: Mapped[str] = mapped_column(String(20), nullable=False)  # 'pass', 'fail'
    
    # MANDATORY: Test certificate photo
    certificate_photo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_photo_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    certificate_photo_mimetype: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Verification
    entered_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # NCR tracking (if test fails)
    ncr_generated: Mapped[bool] = mapped_column(Integer, default=0)
    ncr_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    
    # Soft delete (CRITICAL DATA - NO PERMANENT DELETE)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="material_tests")
    category = relationship("MaterialCategory", backref="material_tests")
    brand = relationship("ApprovedBrand", backref="material_tests")
    lab = relationship("ThirdPartyLab", backref="material_tests")
    entered_by_user = relationship("User", foreign_keys=[entered_by])
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    
    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "projectId": self.project_id,
            "categoryId": self.category_id,
            "brandId": self.brand_id,
            "labId": self.lab_id,
            "material": {
                "description": self.material_description,
                "gradeSpecification": self.grade_specification,
                "quantity": self.quantity,
                "quantityUnit": self.quantity_unit
            },
            "supplier": {
                "name": self.supplier_name,
                "manufacturer": self.manufacturer_name,
                "batchLotNumber": self.batch_lot_number
            },
            "invoice": {
                "number": self.invoice_number,
                "date": self.invoice_date.isoformat()
            },
            "location": self.location_description,
            "testDetails": {
                "reportNumber": self.lab_test_report_number,
                "sampleCollectionDate": self.sample_collection_date.isoformat(),
                "testingDate": self.testing_date.isoformat(),
                "testParameters": json.loads(self.test_parameters) if self.test_parameters else {},
                "testResults": json.loads(self.test_results) if self.test_results else {},
                "passFailStatus": self.pass_fail_status
            },
            "certificate": {
                "fileName": self.certificate_photo_name,
                "mimeType": self.certificate_photo_mimetype
            },
            "verification": {
                "enteredBy": self.entered_by,
                "verifiedBy": self.verified_by,
                "verifiedAt": self.verified_at.isoformat() if self.verified_at else None,
                "status": self.verification_status,
                "remarks": self.verification_remarks
            },
            "ncr": {
                "generated": bool(self.ncr_generated),
                "number": self.ncr_number
            },
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class TrainingRecord(Base):
    """
    Site training register with photos and trainee tracking.
    Records training sessions with location, activity, and attendees.
    """
    __tablename__ = "training_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    trainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Training details
    training_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    training_topic: Mapped[str] = mapped_column(String(255), nullable=False)
    trainee_names_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of names
    
    # Location and activity
    building: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Building/location name
    activity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Blockwork, Gypsum, Plastering, etc.
    
    # Duration
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Training photo (mandatory - either clicked or uploaded)
    photo_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    photo_mimetype: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Additional information
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="training_records")
    trainer = relationship("User", foreign_keys=[trainer_id], backref="trainings_conducted")
    deleted_by_user = relationship("User", foreign_keys=[deleted_by])
    
    def to_dict(self) -> dict:
        import json
        # Parse trainee names from JSON
        try:
            trainee_names = json.loads(self.trainee_names_json)
        except:
            trainee_names = []
        
        return {
            "id": self.id,
            "projectId": self.project_id,
            "trainerId": self.trainer_id,
            "trainingDate": self.training_date.isoformat(),
            "trainingTopic": self.training_topic,
            "traineeNames": trainee_names,
            "traineeCount": len(trainee_names),
            "building": self.building,
            "activity": self.activity,
            "durationMinutes": self.duration_minutes,
            "hasPhoto": bool(self.photo_data),
            "photoFilename": self.photo_filename,
            "remarks": self.remarks,
            "isDeleted": bool(self.is_deleted),
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class TestReminder(Base):
    """
    Test Reminder Schedule for Cube Testing.
    Automatically created when cube sets are cast, sends notifications on testing day.
    """
    __tablename__ = "test_reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cube_test_id: Mapped[int] = mapped_column(Integer, ForeignKey("cube_test_registers.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Schedule Details
    reminder_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)  # The date testing should be done
    test_age_days: Mapped[int] = mapped_column(Integer, nullable=False)  # 3, 7, 28, 56 days
    
    # Notification Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/sent/completed/cancelled
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notified_user_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of user IDs who were notified
    
    # Completion tracking
    test_completed: Mapped[bool] = mapped_column(Integer, default=0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cube_test = relationship("CubeTestRegister", backref="reminders")
    project = relationship("Project", backref="test_reminders")
    
    def to_dict(self) -> dict:
        import json
        try:
            notified_users = json.loads(self.notified_user_ids) if self.notified_user_ids else []
        except:
            notified_users = []
            
        return {
            "id": self.id,
            "cubeTestId": self.cube_test_id,
            "projectId": self.project_id,
            "reminderDate": self.reminder_date.isoformat(),
            "testAgeDays": self.test_age_days,
            "status": self.status,
            "notificationSentAt": self.notification_sent_at.isoformat() if self.notification_sent_at else None,
            "notifiedUserIds": notified_users,
            "testCompleted": bool(self.test_completed),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class MaterialVehicleRegister(Base):
    """
    Material Vehicle Register - For watchmen/security to log all material vehicles.
    Separate from RMC batches, includes photos (MTC, vehicle, etc.)
    """
    __tablename__ = "material_vehicle_register"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Vehicle Entry Details
    vehicle_number: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # RMC Truck, TMT Truck, etc.
    
    # Material Details
    material_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Concrete, Steel, Cement, Sand, etc.
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    challan_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Driver Details
    driver_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    driver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    driver_license: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Entry/Exit Times
    entry_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Calculated
    
    # Time Limit Check
    allowed_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # From project settings
    exceeded_time_limit: Mapped[bool] = mapped_column(Integer, default=0)
    time_warning_sent: Mapped[bool] = mapped_column(Integer, default=0)
    time_warning_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Photos - JSON array of photo URLs
    photos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON: [{"type": "MTC", "url": "..."}, ...]
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="on_site")  # on_site, exited
    purpose: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Delivery, Loading, etc.
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Linkage to RMC Batch (if applicable)
    linked_batch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("batch_registers.id"), nullable=True)
    is_linked_to_batch: Mapped[bool] = mapped_column(Integer, default=0)
    
    # Metadata
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # Watchman
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", backref="vehicle_entries")
    creator = relationship("User", foreign_keys=[created_by], backref="created_vehicle_entries")
    
    def to_dict(self) -> dict:
        import json
        photos_list = []
        if self.photos:
            try:
                photos_list = json.loads(self.photos)
            except:
                photos_list = []
        
        return {
            "id": self.id,
            "projectId": self.project_id,
            "vehicleNumber": self.vehicle_number,
            "vehicleType": self.vehicle_type,
            "materialType": self.material_type,
            "supplierName": self.supplier_name,
            "challanNumber": self.challan_number,
            "driverName": self.driver_name,
            "driverPhone": self.driver_phone,
            "driverLicense": self.driver_license,
            "entryTime": self.entry_time.isoformat(),
            "exitTime": self.exit_time.isoformat() if self.exit_time else None,
            "durationHours": self.duration_hours,
            "allowedTimeHours": self.allowed_time_hours,
            "exceededTimeLimit": bool(self.exceeded_time_limit),
            "timeWarningSent": bool(self.time_warning_sent),
            "timeWarningSentAt": self.time_warning_sent_at.isoformat() if self.time_warning_sent_at else None,
            "photos": photos_list,
            "status": self.status,
            "purpose": self.purpose,
            "remarks": self.remarks,
            "linkedBatchId": self.linked_batch_id,
            "isLinkedToBatch": bool(self.is_linked_to_batch),
            "createdBy": self.created_by,
            "updatedBy": self.updated_by,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }


class ProjectSettings(Base):
    """
    Project-specific settings and configurations
    """
    __tablename__ = "project_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    # Material Vehicle Register Settings
    enable_material_vehicle_addon: Mapped[bool] = mapped_column(Integer, default=0)  # C1 vs C2 company type
    vehicle_allowed_time_hours: Mapped[float] = mapped_column(Float, default=3.0)  # Default 3 hours
    send_time_warnings: Mapped[bool] = mapped_column(Integer, default=1)
    
    # Notification Settings
    enable_test_reminders: Mapped[bool] = mapped_column(Integer, default=1)
    reminder_time: Mapped[str] = mapped_column(String(10), default="09:00")  # Daily reminder time
    notify_project_admins: Mapped[bool] = mapped_column(Integer, default=1)
    notify_quality_engineers: Mapped[bool] = mapped_column(Integer, default=1)
    
    # WhatsApp Notification Settings
    enable_whatsapp_notifications: Mapped[bool] = mapped_column(Integer, default=0)
    enable_email_notifications: Mapped[bool] = mapped_column(Integer, default=1)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", backref="settings")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "projectId": self.project_id,
            "enableMaterialVehicleAddon": bool(self.enable_material_vehicle_addon),
            "vehicleAllowedTimeHours": self.vehicle_allowed_time_hours,
            "sendTimeWarnings": bool(self.send_time_warnings),
            "enableTestReminders": bool(self.enable_test_reminders),
            "reminderTime": self.reminder_time,
            "notifyProjectAdmins": bool(self.notify_project_admins),
            "notifyQualityEngineers": bool(self.notify_quality_engineers),
            "enableWhatsappNotifications": bool(self.enable_whatsapp_notifications),
            "enableEmailNotifications": bool(self.enable_email_notifications),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "updatedBy": self.updated_by
        }




