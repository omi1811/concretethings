"""
Incident Investigation Models

Incident reporting and investigation management for:
- Fatality, injury, near-miss, property damage incidents
- Root cause analysis (5 Whys, Fishbone)
- Corrective and preventive actions
- Investigation team management
- Witness statements
- Regulatory reporting

Compliance: ISO 45001:2018 Clause 10.2 (Incident Investigation), OSHA 29 CFR 1904
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Numeric, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from .models import Base
import enum


class IncidentType(enum.Enum):
    """Types of incidents"""
    FATALITY = "fatality"
    MAJOR_INJURY = "major_injury"
    MINOR_INJURY = "minor_injury"
    NEAR_MISS = "near_miss"
    PROPERTY_DAMAGE = "property_damage"
    FIRE = "fire"
    EXPLOSION = "explosion"
    CHEMICAL_SPILL = "chemical_spill"
    EQUIPMENT_FAILURE = "equipment_failure"


class IncidentStatus(enum.Enum):
    """Investigation status"""
    REPORTED = "reported"
    UNDER_INVESTIGATION = "under_investigation"
    ACTIONS_PENDING = "actions_pending"
    ACTIONS_IN_PROGRESS = "actions_in_progress"
    CLOSED = "closed"


class IncidentReport(Base):
    """
    Incident reports with full investigation workflow.
    
    Tracks:
    - Incident details (type, severity, location, date/time)
    - Injured persons and witnesses
    - Investigation team and findings
    - Root cause analysis
    - Corrective and preventive actions
    - Cost impact and lost time
    - Regulatory reporting
    """
    __tablename__ = 'incident_reports'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    reported_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Incident identification
    incident_number = Column(String(50), unique=True, nullable=False)  # INC-{project}-{year}-{seq}
    incident_type = Column(Enum(IncidentType), nullable=False)
    incident_date = Column(DateTime, nullable=False)
    incident_time = Column(String(10))  # HH:MM format
    location = Column(String(500), nullable=False)  # Building, floor, area
    location_latitude = Column(Numeric(10, 8))  # For heatmap
    location_longitude = Column(Numeric(11, 8))
    
    # Severity (1-5 scale)
    severity = Column(Integer, nullable=False)  # 1=Minor, 2=Moderate, 3=Serious, 4=Critical, 5=Fatality
    
    # Description
    incident_description = Column(Text, nullable=False)
    immediate_action_taken = Column(Text)
    
    # People involved
    injured_persons = Column(JSON)  # [{name, age, company, injury_type, body_part, hospital, status}]
    witnesses = Column(JSON)  # [{name, company, contact, statement, statement_date}]
    
    # Investigation
    investigation_required = Column(Boolean, default=True)
    investigation_team = Column(JSON)  # [{user_id, name, role, assignment_date}]
    investigation_start_date = Column(DateTime)
    investigation_end_date = Column(DateTime)
    investigation_lead = Column(Integer, ForeignKey('users.id'))  # Lead investigator
    
    # Root Cause Analysis
    immediate_causes = Column(JSON)  # Direct causes
    underlying_causes = Column(JSON)  # System/organizational causes
    root_cause_analysis = Column(Text)  # 5 Whys, Fishbone diagram findings
    contributing_factors = Column(JSON)  # Environmental, equipment, human factors
    
    # Corrective Actions (immediate)
    corrective_actions = Column(JSON)  # [{action, responsible_user_id, deadline, status, completion_date}]
    
    # Preventive Actions (long-term)
    preventive_actions = Column(JSON)  # [{action, responsible_user_id, deadline, status, completion_date}]
    
    # Impact Assessment
    lost_time_hours = Column(Numeric(10, 2), default=0)  # Hours of work lost
    lost_time_days = Column(Integer, default=0)  # Full days lost
    medical_cost = Column(Numeric(12, 2), default=0)  # Medical expenses
    property_damage_cost = Column(Numeric(12, 2), default=0)  # Property damage
    total_cost = Column(Numeric(12, 2), default=0)  # Total financial impact
    
    # Property Damage Details
    property_damage_description = Column(Text)
    damaged_equipment = Column(JSON)  # [{equipment, extent, estimated_cost}]
    
    # Regulatory Reporting
    reportable_to_authority = Column(Boolean, default=False)  # OSHA, local authorities
    authority_name = Column(String(200))  # "OSHA", "Factory Inspector", etc.
    authority_notified = Column(Boolean, default=False)
    authority_notification_date = Column(DateTime)
    authority_reference_number = Column(String(100))
    authority_report_pdf = Column(String(500))  # S3 path to official report
    
    # Evidence
    photos = Column(JSON)  # [{url, description, uploaded_by, uploaded_at}]
    documents = Column(JSON)  # [{url, type, description, uploaded_at}]
    
    # Lessons Learned
    lessons_learned = Column(Text)
    recommendations = Column(Text)
    
    # Status
    status = Column(Enum(IncidentStatus), default=IncidentStatus.REPORTED)
    
    # Closure
    closed_by = Column(Integer, ForeignKey('users.id'))
    closed_date = Column(DateTime)
    closure_remarks = Column(Text)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'))
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    project = relationship("Project", foreign_keys=[project_id])
    reporter = relationship("User", foreign_keys=[reported_by])
    lead_investigator = relationship("User", foreign_keys=[investigation_lead])
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'incidentNumber': self.incident_number,
            'incidentType': self.incident_type.value if self.incident_type else None,
            'incidentDate': self.incident_date.isoformat() if self.incident_date else None,
            'incidentTime': self.incident_time,
            'location': self.location,
            'locationCoordinates': {
                'lat': float(self.location_latitude) if self.location_latitude else None,
                'lng': float(self.location_longitude) if self.location_longitude else None,
            },
            'severity': self.severity,
            'severityLabel': ['', 'Minor', 'Moderate', 'Serious', 'Critical', 'Fatality'][self.severity] if self.severity else None,
            'description': self.incident_description,
            'immediateAction': self.immediate_action_taken,
            'reportedBy': {
                'id': self.reporter.id,
                'name': self.reporter.full_name,
                'role': self.reporter.role,
            } if self.reporter else None,
            'injuredPersons': self.injured_persons or [],
            'injuredCount': len(self.injured_persons) if self.injured_persons else 0,
            'witnesses': self.witnesses or [],
            'investigation': {
                'required': self.investigation_required,
                'team': self.investigation_team or [],
                'lead': {
                    'id': self.lead_investigator.id,
                    'name': self.lead_investigator.full_name,
                } if self.lead_investigator else None,
                'startDate': self.investigation_start_date.isoformat() if self.investigation_start_date else None,
                'endDate': self.investigation_end_date.isoformat() if self.investigation_end_date else None,
            },
            'rootCauseAnalysis': {
                'immediateCauses': self.immediate_causes or [],
                'underlyingCauses': self.underlying_causes or [],
                'analysis': self.root_cause_analysis,
                'contributingFactors': self.contributing_factors or [],
            },
            'correctiveActions': self.corrective_actions or [],
            'preventiveActions': self.preventive_actions or [],
            'impact': {
                'lostTimeHours': float(self.lost_time_hours) if self.lost_time_hours else 0,
                'lostTimeDays': self.lost_time_days,
                'medicalCost': float(self.medical_cost) if self.medical_cost else 0,
                'propertyDamageCost': float(self.property_damage_cost) if self.property_damage_cost else 0,
                'totalCost': float(self.total_cost) if self.total_cost else 0,
            },
            'propertyDamage': {
                'description': self.property_damage_description,
                'damagedEquipment': self.damaged_equipment or [],
            },
            'regulatory': {
                'reportable': self.reportable_to_authority,
                'authorityName': self.authority_name,
                'notified': self.authority_notified,
                'notificationDate': self.authority_notification_date.isoformat() if self.authority_notification_date else None,
                'referenceNumber': self.authority_reference_number,
            },
            'evidence': {
                'photos': self.photos or [],
                'documents': self.documents or [],
            },
            'lessonsLearned': self.lessons_learned,
            'recommendations': self.recommendations,
            'status': self.status.value if self.status else None,
            'closure': {
                'closed': self.status == IncidentStatus.CLOSED,
                'closedBy': self.closed_by,
                'closedDate': self.closed_date.isoformat() if self.closed_date else None,
                'remarks': self.closure_remarks,
            },
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def calculate_incident_rate(self, total_hours_worked: int):
        """
        Calculate OSHA Incident Rate.
        Formula: (Number of injuries × 200,000) / Total hours worked by all employees
        200,000 = 100 employees working 40 hours/week for 50 weeks
        """
        if total_hours_worked == 0:
            return 0
        injured_count = len(self.injured_persons) if self.injured_persons else 0
        return (injured_count * 200000) / total_hours_worked
    
    def calculate_severity_rate(self, total_hours_worked: int):
        """
        Calculate OSHA Severity Rate.
        Formula: (Lost time days × 200,000) / Total hours worked
        """
        if total_hours_worked == 0:
            return 0
        return (self.lost_time_days * 200000) / total_hours_worked
