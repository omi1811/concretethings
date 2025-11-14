"""
Concrete Quality Non-Conformance (NC) Models

Complete workflow for raising, tracking, and resolving quality issues
in concrete construction projects.

Features:
- Multi-level hierarchical tags (configured by System Admin)
- Photo evidence with gallery/camera support
- Location tracking
- Severity-based scoring system
- Contractor assignment and response
- Email/WhatsApp/In-app notifications
- Issue transfer capability
- Monthly/weekly scoring reports
- Complete audit trail

Compliance: ISO 9001:2015 Clause 8.7 (Control of nonconforming outputs)
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Date, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from server.db import Base


class NCIssueSeverity(enum.Enum):
    """NC Issue severity levels with associated scores"""
    HIGH = "high"  # 1 point
    MODERATE = "moderate"  # 0.5 points
    LOW = "low"  # 0.25 points


class NCIssueStatus(enum.Enum):
    """NC Issue lifecycle status"""
    RAISED = "raised"  # Issue raised, pending contractor response
    ACKNOWLEDGED = "acknowledged"  # Contractor acknowledged
    IN_PROGRESS = "in_progress"  # Contractor working on resolution
    RESOLVED = "resolved"  # Contractor claims resolved
    VERIFIED = "verified"  # Raiser verified resolution
    CLOSED = "closed"  # Issue closed
    REJECTED = "rejected"  # Contractor rejected the NC
    TRANSFERRED = "transferred"  # Issue transferred to different contractor


class ConcreteNCTag(Base):
    """
    Hierarchical tags for categorizing NC issues.
    Configured by System Admin with support team assistance.
    
    Example hierarchy:
    Level 1: Structural
      Level 2: Column
        Level 3: Reinforcement
          Level 4: Cover inadequate
    """
    __tablename__ = 'concrete_nc_tags'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Tag details
    tag_name = Column(String(100), nullable=False)
    tag_level = Column(Integer, nullable=False)  # 1, 2, 3, 4 (hierarchical depth)
    parent_tag_id = Column(Integer, ForeignKey('concrete_nc_tags.id'), nullable=True)  # Parent in hierarchy
    tag_color = Column(String(20), default='#6366f1')  # Hex color for UI
    display_order = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    parent_tag = relationship('ConcreteNCTag', remote_side=[id], backref='child_tags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tagName': self.tag_name,
            'tagLevel': self.tag_level,
            'parentTagId': self.parent_tag_id,
            'tagColor': self.tag_color,
            'displayOrder': self.display_order,
            'isActive': self.is_active
        }


class ConcreteNCIssue(Base):
    """
    Non-Conformance Issue for Concrete Quality Management.
    
    Workflow:
    1. QAQC/PM/DGM/Sr. Engineer/Third-party auditor raises issue
    2. Contractor supervisor receives notification (WhatsApp/Email/In-app)
    3. Contractor responds (acknowledge/reject/resolve)
    4. Raiser verifies and closes OR requests rework
    5. Sr. Engineer kept in loop throughout
    6. Issues can be transferred between contractors
    """
    __tablename__ = 'concrete_nc_issues'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Issue identification
    nc_number = Column(String(50), unique=True, nullable=False)  # NC-PROJ-YYYY-NNNN
    issue_title = Column(String(255), nullable=False)
    issue_description = Column(Text, nullable=False)
    
    # Location
    location = Column(String(255), nullable=False)  # Typed location (e.g., "3rd Floor, Column C-5")
    latitude = Column(Float, nullable=True)  # Optional GPS
    longitude = Column(Float, nullable=True)
    
    # Tags (hierarchical) - stored as JSON array of tag IDs
    # Example: [15, 42, 78, 103] representing Level1 > Level2 > Level3 > Level4
    tag_ids = Column(JSON, nullable=False)
    
    # Photo evidence (JSON array of file paths)
    # Example: ["uploads/nc/12345_photo1.jpg", "uploads/nc/12345_photo2.jpg"]
    photo_urls = Column(JSON, nullable=False, default=[])
    
    # Severity and deadline
    severity = Column(SQLEnum(NCIssueSeverity), nullable=False)
    severity_score = Column(Float, nullable=False)  # Auto-calculated: HIGH=1.0, MODERATE=0.5, LOW=0.25
    deadline_date = Column(Date, nullable=False)
    
    # Recommendation from raiser
    recommended_action = Column(Text, nullable=True)
    
    # Raised by (QAQC/PM/DGM/Sr. Engineer/Third-party auditor)
    raised_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    raised_by_role = Column(String(100), nullable=False)  # Role at time of raising
    raised_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Assigned to contractor
    assigned_contractor_id = Column(Integer, ForeignKey('rmc_vendors.id'), nullable=False)  # Using RMCVendor as Contractor
    contractor_supervisor_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Specific supervisor
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Sr. Engineer oversight (kept in loop)
    oversight_engineer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(NCIssueStatus), default=NCIssueStatus.RAISED, nullable=False)
    
    # Contractor response
    contractor_acknowledged_at = Column(DateTime, nullable=True)
    contractor_response = Column(Text, nullable=True)
    contractor_action_taken = Column(Text, nullable=True)
    contractor_resolved_at = Column(DateTime, nullable=True)
    contractor_resolution_photos = Column(JSON, default=[])  # Photos of resolved work
    
    # Verification by raiser
    verified_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    verification_approved = Column(Boolean, nullable=True)  # True=closed, False=rejected
    
    # Closure
    closed_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    closure_notes = Column(Text, nullable=True)
    
    # Transfer tracking
    transfer_history = Column(JSON, default=[])  # Array of transfer records
    # Format: [{"from_contractor_id": 5, "to_contractor_id": 7, "transferred_by": 10, "transferred_at": "2025-11-14T10:30:00", "reason": "Wrong contractor assigned"}]
    
    # Scoring (for monthly/weekly reports)
    score_month = Column(Integer, nullable=False)  # Month (1-12)
    score_year = Column(Integer, nullable=False)  # Year (2025, 2026, etc.)
    score_week = Column(Integer, nullable=False)  # Week number (1-53)
    is_scored = Column(Boolean, default=True)  # Can be excluded from scoring if needed
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ncNumber': self.nc_number,
            'projectId': self.project_id,
            'issueTitle': self.issue_title,
            'issueDescription': self.issue_description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'tagIds': self.tag_ids,
            'photoUrls': self.photo_urls,
            'severity': self.severity.value if self.severity else None,
            'severityScore': self.severity_score,
            'deadlineDate': self.deadline_date.isoformat() if self.deadline_date else None,
            'recommendedAction': self.recommended_action,
            'raisedById': self.raised_by_id,
            'raisedByRole': self.raised_by_role,
            'raisedAt': self.raised_at.isoformat() if self.raised_at else None,
            'assignedContractorId': self.assigned_contractor_id,
            'contractorSupervisorId': self.contractor_supervisor_id,
            'oversightEngineerId': self.oversight_engineer_id,
            'status': self.status.value if self.status else None,
            'contractorAcknowledgedAt': self.contractor_acknowledged_at.isoformat() if self.contractor_acknowledged_at else None,
            'contractorResponse': self.contractor_response,
            'contractorActionTaken': self.contractor_action_taken,
            'contractorResolvedAt': self.contractor_resolved_at.isoformat() if self.contractor_resolved_at else None,
            'contractorResolutionPhotos': self.contractor_resolution_photos,
            'verifiedById': self.verified_by_id,
            'verifiedAt': self.verified_at.isoformat() if self.verified_at else None,
            'verificationNotes': self.verification_notes,
            'verificationApproved': self.verification_approved,
            'closedById': self.closed_by_id,
            'closedAt': self.closed_at.isoformat() if self.closed_at else None,
            'closureNotes': self.closure_notes,
            'transferHistory': self.transfer_history,
            'scoreMonth': self.score_month,
            'scoreYear': self.score_year,
            'scoreWeek': self.score_week,
            'isScored': self.is_scored,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ConcreteNCNotification(Base):
    """
    Notification log for NC issue communications.
    Tracks all WhatsApp, Email, and In-app notifications.
    """
    __tablename__ = 'concrete_nc_notifications'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    nc_issue_id = Column(Integer, ForeignKey('concrete_nc_issues.id'), nullable=False)
    
    # Notification details
    notification_type = Column(String(50), nullable=False)  # issue_raised, contractor_response, verified, closed, transferred
    notification_channel = Column(String(20), nullable=False)  # whatsapp, email, in_app
    
    # Recipient
    recipient_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    
    # Message
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    
    # Delivery status
    delivery_status = Column(String(20), default='sent')  # sent, delivered, failed, read
    delivery_timestamp = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ncIssueId': self.nc_issue_id,
            'notificationType': self.notification_type,
            'notificationChannel': self.notification_channel,
            'recipientUserId': self.recipient_user_id,
            'subject': self.subject,
            'message': self.message,
            'deliveryStatus': self.delivery_status,
            'deliveryTimestamp': self.delivery_timestamp.isoformat() if self.delivery_timestamp else None,
            'readAt': self.read_at.isoformat() if self.read_at else None
        }


class ConcreteNCScoreReport(Base):
    """
    Monthly/Weekly scoring reports for contractors based on NC issues.
    
    Scoring system:
    - High severity NC (open): +1.0 point
    - Moderate severity NC (open): +0.5 points
    - Low severity NC (open): +0.25 points
    
    Lower score = Better performance
    """
    __tablename__ = 'concrete_nc_score_reports'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    contractor_id = Column(Integer, ForeignKey('rmc_vendors.id'), nullable=False)
    
    # Report period
    report_type = Column(String(20), nullable=False)  # monthly, weekly
    report_year = Column(Integer, nullable=False)
    report_month = Column(Integer, nullable=True)  # For monthly reports
    report_week = Column(Integer, nullable=True)  # For weekly reports
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    
    # Issue counts
    total_issues_raised = Column(Integer, default=0)
    high_severity_issues = Column(Integer, default=0)
    moderate_severity_issues = Column(Integer, default=0)
    low_severity_issues = Column(Integer, default=0)
    
    # Closure stats
    issues_closed = Column(Integer, default=0)
    issues_open = Column(Integer, default=0)
    issues_overdue = Column(Integer, default=0)
    
    # Score calculation
    total_score = Column(Float, default=0.0)  # Sum of severity scores for open issues
    performance_grade = Column(String(10), nullable=True)  # A, B, C, D, F based on score
    
    # Average resolution time (in days)
    avg_resolution_days = Column(Float, nullable=True)
    
    # Generated by
    generated_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'projectId': self.project_id,
            'contractorId': self.contractor_id,
            'reportType': self.report_type,
            'reportYear': self.report_year,
            'reportMonth': self.report_month,
            'reportWeek': self.report_week,
            'reportPeriodStart': self.report_period_start.isoformat() if self.report_period_start else None,
            'reportPeriodEnd': self.report_period_end.isoformat() if self.report_period_end else None,
            'totalIssuesRaised': self.total_issues_raised,
            'highSeverityIssues': self.high_severity_issues,
            'moderateSeverityIssues': self.moderate_severity_issues,
            'lowSeverityIssues': self.low_severity_issues,
            'issuesClosed': self.issues_closed,
            'issuesOpen': self.issues_open,
            'issuesOverdue': self.issues_overdue,
            'totalScore': self.total_score,
            'performanceGrade': self.performance_grade,
            'avgResolutionDays': self.avg_resolution_days,
            'generatedAt': self.generated_at.isoformat() if self.generated_at else None
        }
