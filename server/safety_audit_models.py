"""
Safety Audit Models
Database models for safety inspection audits, checklists, and findings
ISO 45001:2018 Clause 9.2 (Internal Audit)
"""

from server.db import Base, session_scope
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class AuditType(enum.Enum):
    """Types of safety audits"""
    COMPREHENSIVE = "COMPREHENSIVE"  # Full site audit
    FOCUSED = "FOCUSED"  # Specific area/activity
    PERMIT_TO_WORK = "PERMIT_TO_WORK"  # PTW compliance
    HOUSEKEEPING = "HOUSEKEEPING"  # Housekeeping standards
    PPE_COMPLIANCE = "PPE_COMPLIANCE"  # PPE usage check
    WORKING_AT_HEIGHT = "WORKING_AT_HEIGHT"  # Height work safety
    EXCAVATION = "EXCAVATION"  # Excavation safety
    ELECTRICAL = "ELECTRICAL"  # Electrical safety
    SCAFFOLDING = "SCAFFOLDING"  # Scaffold inspection
    EQUIPMENT = "EQUIPMENT"  # Equipment safety
    FIRE_SAFETY = "FIRE_SAFETY"  # Fire prevention
    EMERGENCY_PREPAREDNESS = "EMERGENCY_PREPAREDNESS"  # Emergency response

class AuditStatus(enum.Enum):
    """Audit lifecycle states"""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FINDINGS_PENDING = "FINDINGS_PENDING"
    ACTIONS_PENDING = "ACTIONS_PENDING"
    CLOSED = "CLOSED"

class FindingSeverity(enum.Enum):
    """Severity of audit findings"""
    OBSERVATION = "OBSERVATION"  # Good practice or suggestion
    MINOR_NC = "MINOR_NC"  # Minor non-conformance (ISO 45001)
    MAJOR_NC = "MAJOR_NC"  # Major non-conformance (ISO 45001)
    CRITICAL = "CRITICAL"  # Imminent danger

class AuditGrade(enum.Enum):
    """Overall audit performance grade"""
    EXCELLENT = "EXCELLENT"  # 90-100%
    GOOD = "GOOD"  # 75-89%
    SATISFACTORY = "SATISFACTORY"  # 60-74%
    POOR = "POOR"  # 40-59%
    CRITICAL = "CRITICAL"  # <40%


class SafetyAudit(Base):
    """
    Safety Audit Record
    Represents a scheduled or completed safety inspection/audit
    """
    __tablename__ = 'safety_audits'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Audit Identification
    audit_number = Column(String(50), unique=True, nullable=False)  # AUDIT-{project}-{year}-{seq}
    audit_type = Column(Enum(AuditType), nullable=False)
    audit_title = Column(String(200), nullable=False)  # "Q4 2025 Comprehensive Safety Audit"
    audit_description = Column(Text)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Auditor Information
    lead_auditor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    audit_team = Column(JSON)  # [{user_id, name, role}]
    
    # Execution
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    audit_duration_minutes = Column(Integer)  # Calculated field
    
    # Location/Scope
    audit_location = Column(String(200))  # "Block A - Floors 5-10"
    audit_scope = Column(Text)  # Detailed scope description
    areas_covered = Column(JSON)  # ["Excavation", "Scaffolding", "PPE"]
    
    # Checklist
    checklist_id = Column(Integer, ForeignKey('audit_checklists.id'))
    checklist_items = Column(JSON)  # Snapshot of checklist at audit time
    # [{
    #     item_id, category, item, compliant: true/false/na,
    #     evidence_photo, remarks, corrective_action_required
    # }]
    
    # Scoring
    total_items = Column(Integer, default=0)
    compliant_items = Column(Integer, default=0)
    non_compliant_items = Column(Integer, default=0)
    not_applicable_items = Column(Integer, default=0)
    compliance_percentage = Column(Numeric(5, 2))  # 0.00 to 100.00
    audit_grade = Column(Enum(AuditGrade))  # EXCELLENT/GOOD/SATISFACTORY/POOR/CRITICAL
    
    # Findings
    total_findings = Column(Integer, default=0)
    observations = Column(Integer, default=0)  # Good practices
    minor_ncs = Column(Integer, default=0)
    major_ncs = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    
    findings_details = Column(JSON)  # Detailed findings array
    # [{
    #     severity, category, finding, evidence_photos, location,
    #     corrective_action, responsible_user_id, deadline, status
    # }]
    
    # Evidence
    photos = Column(JSON)  # [{url, description, category, timestamp, uploaded_by}]
    documents = Column(JSON)  # [{url, type, description, timestamp, uploaded_by}]
    
    # Strengths & Weaknesses
    positive_observations = Column(Text)  # Good practices noted
    areas_of_concern = Column(Text)  # Major concerns
    
    # Recommendations
    immediate_actions_required = Column(Text)
    long_term_improvements = Column(Text)
    training_recommendations = Column(JSON)  # [{topic, target_audience, priority}]
    
    # Report
    audit_report_pdf = Column(String(500))  # S3 path to generated report
    report_generated_at = Column(DateTime)
    
    # Status
    status = Column(Enum(AuditStatus), default=AuditStatus.SCHEDULED)
    
    # Action Tracking
    actions_assigned = Column(Integer, default=0)
    actions_completed = Column(Integer, default=0)
    actions_overdue = Column(Integer, default=0)
    
    # Closure
    closed_by_id = Column(Integer, ForeignKey('users.id'))
    closed_date = Column(DateTime)
    closure_remarks = Column(Text)
    
    # Compliance References
    iso_clauses_checked = Column(JSON)  # ["4.1", "9.2", "10.2"]
    osha_standards_checked = Column(JSON)  # ["1926.21", "1926.501"]
    
    # Audit Trail
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='safety_audits')
    project = relationship('Project', backref='safety_audits')
    lead_auditor = relationship('User', foreign_keys=[lead_auditor_id])
    scheduled_by = relationship('User', foreign_keys=[scheduled_by_id])
    closed_by = relationship('User', foreign_keys=[closed_by_id])
    checklist = relationship('AuditChecklist')
    
    def calculate_score(self):
        """Calculate compliance percentage and grade"""
        if self.total_items > 0:
            self.compliance_percentage = round((self.compliant_items / self.total_items) * 100, 2)
            
            # Assign grade
            if self.compliance_percentage >= 90:
                self.audit_grade = AuditGrade.EXCELLENT
            elif self.compliance_percentage >= 75:
                self.audit_grade = AuditGrade.GOOD
            elif self.compliance_percentage >= 60:
                self.audit_grade = AuditGrade.SATISFACTORY
            elif self.compliance_percentage >= 40:
                self.audit_grade = AuditGrade.POOR
            else:
                self.audit_grade = AuditGrade.CRITICAL
        else:
            self.compliance_percentage = 0.0
            self.audit_grade = None
    
    def count_findings(self):
        """Count findings by severity"""
        if self.findings_details:
            self.observations = sum(1 for f in self.findings_details if f.get('severity') == 'OBSERVATION')
            self.minor_ncs = sum(1 for f in self.findings_details if f.get('severity') == 'MINOR_NC')
            self.major_ncs = sum(1 for f in self.findings_details if f.get('severity') == 'MAJOR_NC')
            self.critical_findings = sum(1 for f in self.findings_details if f.get('severity') == 'CRITICAL')
            self.total_findings = len(self.findings_details)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        self.calculate_score()
        self.count_findings()
        
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'audit_number': self.audit_number,
            'audit_type': self.audit_type.value if self.audit_type else None,
            'audit_title': self.audit_title,
            'audit_description': self.audit_description,
            
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_by_id': self.scheduled_by_id,
            
            'lead_auditor_id': self.lead_auditor_id,
            'lead_auditor_name': self.lead_auditor.name if self.lead_auditor else None,
            'audit_team': self.audit_team or [],
            
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'audit_duration_minutes': self.audit_duration_minutes,
            
            'audit_location': self.audit_location,
            'audit_scope': self.audit_scope,
            'areas_covered': self.areas_covered or [],
            
            'checklist_id': self.checklist_id,
            'checklist_items': self.checklist_items or [],
            
            'scoring': {
                'total_items': self.total_items,
                'compliant_items': self.compliant_items,
                'non_compliant_items': self.non_compliant_items,
                'not_applicable_items': self.not_applicable_items,
                'compliance_percentage': float(self.compliance_percentage) if self.compliance_percentage else 0.0,
                'audit_grade': self.audit_grade.value if self.audit_grade else None
            },
            
            'findings_summary': {
                'total_findings': self.total_findings,
                'observations': self.observations,
                'minor_ncs': self.minor_ncs,
                'major_ncs': self.major_ncs,
                'critical_findings': self.critical_findings
            },
            'findings_details': self.findings_details or [],
            
            'evidence': {
                'photos': self.photos or [],
                'documents': self.documents or []
            },
            
            'analysis': {
                'positive_observations': self.positive_observations,
                'areas_of_concern': self.areas_of_concern,
                'immediate_actions_required': self.immediate_actions_required,
                'long_term_improvements': self.long_term_improvements,
                'training_recommendations': self.training_recommendations or []
            },
            
            'audit_report_pdf': self.audit_report_pdf,
            'report_generated_at': self.report_generated_at.isoformat() if self.report_generated_at else None,
            
            'status': self.status.value if self.status else None,
            
            'actions': {
                'assigned': self.actions_assigned,
                'completed': self.actions_completed,
                'overdue': self.actions_overdue
            },
            
            'closure': {
                'closed_by_id': self.closed_by_id,
                'closed_by_name': self.closed_by.name if self.closed_by else None,
                'closed_date': self.closed_date.isoformat() if self.closed_date else None,
                'closure_remarks': self.closure_remarks
            },
            
            'compliance_references': {
                'iso_clauses_checked': self.iso_clauses_checked or [],
                'osha_standards_checked': self.osha_standards_checked or []
            },
            
            'audit_trail': {
                'created_by': self.created_by,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_by': self.updated_by,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }


class AuditChecklist(Base):
    """
    Audit Checklist Template
    Reusable checklist for specific audit types
    """
    __tablename__ = 'audit_checklists'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Checklist Details
    checklist_name = Column(String(200), nullable=False)  # "Comprehensive Safety Audit Checklist"
    checklist_code = Column(String(50))  # "CSA-001"
    audit_type = Column(Enum(AuditType), nullable=False)
    checklist_description = Column(Text)
    
    # Version Control
    version = Column(String(20), default="1.0")
    effective_date = Column(DateTime)
    revision_date = Column(DateTime)
    
    # Checklist Items
    categories = Column(JSON, nullable=False)  # Category names
    # ["General Housekeeping", "PPE Compliance", "Working at Height", ...]
    
    items = Column(JSON, nullable=False)  # Full checklist
    # [{
    #     item_id, category, item_description,
    #     compliance_criteria, reference_standard,
    #     severity_if_non_compliant, photo_required
    # }]
    
    # Statistics
    total_items = Column(Integer)
    total_categories = Column(Integer)
    
    # Compliance References
    iso_45001_clauses = Column(JSON)  # ["4.1", "9.2", "10.2"]
    osha_standards = Column(JSON)  # ["1926.21", "1926.501"]
    local_regulations = Column(JSON)  # Indian standards
    
    # Usage
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Default template for audit type
    
    # Audit Trail
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='audit_checklists')
    audits = relationship('SafetyAudit', backref='audit_checklist_template')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'checklist_name': self.checklist_name,
            'checklist_code': self.checklist_code,
            'audit_type': self.audit_type.value if self.audit_type else None,
            'checklist_description': self.checklist_description,
            
            'version': self.version,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'revision_date': self.revision_date.isoformat() if self.revision_date else None,
            
            'categories': self.categories or [],
            'items': self.items or [],
            
            'statistics': {
                'total_items': self.total_items or len(self.items) if self.items else 0,
                'total_categories': self.total_categories or len(self.categories) if self.categories else 0
            },
            
            'compliance_references': {
                'iso_45001_clauses': self.iso_45001_clauses or [],
                'osha_standards': self.osha_standards or [],
                'local_regulations': self.local_regulations or []
            },
            
            'is_active': self.is_active,
            'is_default': self.is_default,
            
            'audit_trail': {
                'created_by': self.created_by,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_by': self.updated_by,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }


# ========================================
# STANDARD CHECKLIST TEMPLATES
# ========================================

COMPREHENSIVE_AUDIT_CHECKLIST = {
    "checklist_name": "Comprehensive Safety Audit Checklist",
    "checklist_code": "CSA-001",
    "audit_type": "COMPREHENSIVE",
    "version": "1.0",
    "categories": [
        "General Housekeeping",
        "Personal Protective Equipment (PPE)",
        "Working at Height",
        "Excavation Safety",
        "Electrical Safety",
        "Fire Prevention & Emergency Preparedness",
        "Material Handling & Storage",
        "Scaffolding & Formwork",
        "Equipment & Machinery",
        "Confined Space",
        "Chemical Safety",
        "Permit to Work System",
        "Toolbox Talks & Training",
        "First Aid & Medical Facilities",
        "Incident Reporting & Investigation",
        "Safety Signage & Barricading"
    ],
    "items": [
        # General Housekeeping (10 items)
        {"item_id": 1, "category": "General Housekeeping", "item_description": "Site is clean and free from debris", "compliance_criteria": "No scattered materials, waste segregated", "reference_standard": "IS 3764:1992", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 2, "category": "General Housekeeping", "item_description": "Walkways and access routes are clear", "compliance_criteria": "Minimum 1m width, no obstructions", "reference_standard": "IS 3764:1992", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 3, "category": "General Housekeeping", "item_description": "Waste bins provided and used properly", "compliance_criteria": "Separate bins for dry/wet waste, emptied daily", "reference_standard": "IS 3764:1992", "severity_if_non_compliant": "OBSERVATION", "photo_required": False},
        {"item_id": 4, "category": "General Housekeeping", "item_description": "Sharp objects (nails, rebars) covered or removed", "compliance_criteria": "No exposed sharp edges", "reference_standard": "IS 3764:1992", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 5, "category": "General Housekeeping", "item_description": "Lighting adequate in all work areas", "compliance_criteria": "Minimum 200 lux for general work", "reference_standard": "IS 3646:1966", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        
        # PPE (15 items)
        {"item_id": 6, "category": "Personal Protective Equipment (PPE)", "item_description": "All workers wearing safety helmets", "compliance_criteria": "100% compliance, helmets ISI marked", "reference_standard": "IS 2925:1984", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 7, "category": "Personal Protective Equipment (PPE)", "item_description": "Safety shoes worn by all workers", "compliance_criteria": "100% compliance, shoes with steel toe cap", "reference_standard": "IS 15298:2002", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 8, "category": "Personal Protective Equipment (PPE)", "item_description": "Reflective jackets worn (if required)", "compliance_criteria": "Worn by workers near vehicle movement areas", "reference_standard": "IS 3314:1974", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 9, "category": "Personal Protective Equipment (PPE)", "item_description": "Hand gloves provided and used", "compliance_criteria": "Appropriate gloves for task (welding, chemical, general)", "reference_standard": "IS 4770:1990", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        {"item_id": 10, "category": "Personal Protective Equipment (PPE)", "item_description": "Safety goggles/face shields used (welding, grinding)", "compliance_criteria": "100% compliance during welding/grinding", "reference_standard": "IS 5983:1970", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        
        # Working at Height (12 items)
        {"item_id": 11, "category": "Working at Height", "item_description": "Fall protection provided for work >2m", "compliance_criteria": "Guardrails, safety nets, or full-body harness", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 12, "category": "Working at Height", "item_description": "Full-body harness used (if >6m)", "compliance_criteria": "Harness + double lanyard, anchorage >5000 lbs", "reference_standard": "IS 3521:1997", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 13, "category": "Working at Height", "item_description": "Ladders in good condition", "compliance_criteria": "No broken rungs, non-slip feet, secured", "reference_standard": "IS 4011:1992", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 14, "category": "Working at Height", "item_description": "Opening/edges barricaded", "compliance_criteria": "Yellow/red barrier tape, minimum 1m from edge", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        
        # Excavation (8 items)
        {"item_id": 15, "category": "Excavation Safety", "item_description": "Excavation >1.5m has shoring/benching", "compliance_criteria": "Shoring installed as per soil type", "reference_standard": "IS 4453:1980", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 16, "category": "Excavation Safety", "item_description": "Barricading around excavation", "compliance_criteria": "Minimum 1m distance, warning signs posted", "reference_standard": "IS 4453:1980", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 17, "category": "Excavation Safety", "item_description": "Ladder/safe access provided", "compliance_criteria": "Ladder within 7.5m of any worker in trench", "reference_standard": "IS 4453:1980", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 18, "category": "Excavation Safety", "item_description": "Competent person inspects daily", "compliance_criteria": "Daily inspection log maintained", "reference_standard": "IS 4453:1980", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        
        # Electrical (10 items)
        {"item_id": 19, "category": "Electrical Safety", "item_description": "Temporary wiring properly insulated", "compliance_criteria": "No exposed wires, ELCB/RCCB installed", "reference_standard": "IS 3043:1987", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 20, "category": "Electrical Safety", "item_description": "Electrical panels locked and labeled", "compliance_criteria": "Only authorized electrician access, danger signs posted", "reference_standard": "IS 3043:1987", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 21, "category": "Electrical Safety", "item_description": "Earthing provided for all equipment", "compliance_criteria": "Earthing resistance <5 ohms", "reference_standard": "IS 3043:1987", "severity_if_non_compliant": "CRITICAL", "photo_required": False},
        {"item_id": 22, "category": "Electrical Safety", "item_description": "Extension cords in good condition", "compliance_criteria": "No cuts, splices, or temporary joints", "reference_standard": "IS 694:2010", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        
        # Fire Safety (8 items)
        {"item_id": 23, "category": "Fire Prevention & Emergency Preparedness", "item_description": "Fire extinguishers available and accessible", "compliance_criteria": "ABC type, within 23m, inspected monthly", "reference_standard": "IS 2190:2010", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 24, "category": "Fire Prevention & Emergency Preparedness", "item_description": "Emergency assembly point marked", "compliance_criteria": "Signage visible, minimum 50m from structure", "reference_standard": "IS 2190:2010", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 25, "category": "Fire Prevention & Emergency Preparedness", "item_description": "Flammable materials stored properly", "compliance_criteria": "Separate storage, ventilated, away from ignition sources", "reference_standard": "IS 2190:2010", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 26, "category": "Fire Prevention & Emergency Preparedness", "item_description": "Hot work permit system followed", "compliance_criteria": "PTW issued for all welding/cutting/grinding", "reference_standard": "IS 2190:2010", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        
        # Scaffolding (10 items)
        {"item_id": 27, "category": "Scaffolding & Formwork", "item_description": "Scaffold tagged (Green/Yellow/Red)", "compliance_criteria": "Tag visible, inspection certificate attached", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 28, "category": "Scaffolding & Formwork", "item_description": "Scaffold has guardrails (top/mid/toe)", "compliance_criteria": "Top rail 1m, mid-rail 0.5m, toe board 150mm", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 29, "category": "Scaffolding & Formwork", "item_description": "Scaffold base plates on solid ground", "compliance_criteria": "Level base, mud sills if required", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        {"item_id": 30, "category": "Scaffolding & Formwork", "item_description": "Scaffold tied to structure", "compliance_criteria": "Tied at every 4m vertical, 6m horizontal", "reference_standard": "IS 3696:1966", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        
        # Equipment (8 items)
        {"item_id": 31, "category": "Equipment & Machinery", "item_description": "Operator certified/trained", "compliance_criteria": "Valid operator license/certificate", "reference_standard": "IS 4216:1982", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        {"item_id": 32, "category": "Equipment & Machinery", "item_description": "Pre-use inspection done", "compliance_criteria": "Daily checklist completed and signed", "reference_standard": "IS 4216:1982", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        {"item_id": 33, "category": "Equipment & Machinery", "item_description": "Reverse alarm functional", "compliance_criteria": "Audible >15m, tested daily", "reference_standard": "IS 4216:1982", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        {"item_id": 34, "category": "Equipment & Machinery", "item_description": "Guards installed on moving parts", "compliance_criteria": "Pulleys, belts, gears fully guarded", "reference_standard": "IS 4216:1982", "severity_if_non_compliant": "CRITICAL", "photo_required": True},
        
        # Permit to Work (5 items)
        {"item_id": 35, "category": "Permit to Work System", "item_description": "PTW system implemented for high-risk work", "compliance_criteria": "Permits for height, hot work, confined space, excavation, electrical", "reference_standard": "ISO 45001:2018", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        {"item_id": 36, "category": "Permit to Work System", "item_description": "All permits signed by authorized persons", "compliance_criteria": "3-level approval (Issuer, Receiver, Safety Officer)", "reference_standard": "ISO 45001:2018", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        {"item_id": 37, "category": "Permit to Work System", "item_description": "Checklist completed before permit approval", "compliance_criteria": "All safety measures verified and signed", "reference_standard": "ISO 45001:2018", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        
        # Training (5 items)
        {"item_id": 38, "category": "Toolbox Talks & Training", "item_description": "TBT conducted daily", "compliance_criteria": "Attendance >80%, records maintained", "reference_standard": "ISO 45001:2018", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        {"item_id": 39, "category": "Toolbox Talks & Training", "item_description": "Workers can explain safety procedures", "compliance_criteria": "Random workers interviewed, can explain TBT topic", "reference_standard": "ISO 45001:2018", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        {"item_id": 40, "category": "Toolbox Talks & Training", "item_description": "Safety induction records available", "compliance_criteria": "All workers have induction certificate (within 1 year)", "reference_standard": "ISO 45001:2018 Clause 7.2", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        
        # First Aid (5 items)
        {"item_id": 41, "category": "First Aid & Medical Facilities", "item_description": "First aid box available and stocked", "compliance_criteria": "Within 100m, contents as per IS 7133:1993", "reference_standard": "IS 7133:1993", "severity_if_non_compliant": "MAJOR_NC", "photo_required": True},
        {"item_id": 42, "category": "First Aid & Medical Facilities", "item_description": "Trained first aider present on site", "compliance_criteria": "Certificate valid, name displayed", "reference_standard": "Factories Act 1948", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        {"item_id": 43, "category": "First Aid & Medical Facilities", "item_description": "Emergency contact numbers displayed", "compliance_criteria": "Hospital, ambulance, police numbers visible", "reference_standard": "IS 7133:1993", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        
        # Incident Reporting (3 items)
        {"item_id": 44, "category": "Incident Reporting & Investigation", "item_description": "Incident reporting system in place", "compliance_criteria": "Workers know how to report incidents/near-misses", "reference_standard": "ISO 45001:2018 Clause 10.2", "severity_if_non_compliant": "MINOR_NC", "photo_required": False},
        {"item_id": 45, "category": "Incident Reporting & Investigation", "item_description": "Incident investigation records maintained", "compliance_criteria": "RCA done for all incidents >Severity 3", "reference_standard": "ISO 45001:2018 Clause 10.2", "severity_if_non_compliant": "MAJOR_NC", "photo_required": False},
        
        # Signage (5 items)
        {"item_id": 46, "category": "Safety Signage & Barricading", "item_description": "Warning signs posted at hazardous locations", "compliance_criteria": "Excavation, height work, electrical, chemical areas", "reference_standard": "IS 9457:1980", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 47, "category": "Safety Signage & Barricading", "item_description": "Barricades in good condition", "compliance_criteria": "Red/white tape, sturdy posts, visible", "reference_standard": "IS 9457:1980", "severity_if_non_compliant": "MINOR_NC", "photo_required": True},
        {"item_id": 48, "category": "Safety Signage & Barricading", "item_description": "Mandatory signs (PPE) displayed", "compliance_criteria": "Helmet, shoes, goggles signs at entry", "reference_standard": "IS 9457:1980", "severity_if_non_compliant": "OBSERVATION", "photo_required": True},
    ],
    "iso_45001_clauses": ["4.1", "6.1", "7.2", "8.1", "9.1", "9.2", "10.2"],
    "osha_standards": ["1926.21", "1926.95", "1926.100", "1926.404", "1926.501", "1926.651", "1926.1053"],
    "local_regulations": ["Factories Act 1948", "Building & Other Construction Workers Act 1996", "IS 3764:1992 (Safety Code for Excavation Work)"]
}


def seed_standard_checklists(company_id, created_by):
    """
    Load standard checklist templates for a company
    Call this function once when company is created
    """
    from server.db import SessionLocal
    session = SessionLocal()
    
    try:
        # Check if already seeded
        existing = session.query(AuditChecklist).filter_by(
            company_id=company_id,
            checklist_code="CSA-001",
            is_deleted=False
        ).first()
        
        if existing:
            session.close()
            return {"message": "Standard checklists already exist", "count": 0}
        
        # Create comprehensive checklist
        checklist = AuditChecklist(
            company_id=company_id,
            checklist_name=COMPREHENSIVE_AUDIT_CHECKLIST["checklist_name"],
            checklist_code=COMPREHENSIVE_AUDIT_CHECKLIST["checklist_code"],
            audit_type=AuditType[COMPREHENSIVE_AUDIT_CHECKLIST["audit_type"]],
            checklist_description="ISO 45001 & OSHA compliant comprehensive safety audit checklist covering 16 categories and 48 critical safety items",
            version=COMPREHENSIVE_AUDIT_CHECKLIST["version"],
            effective_date=datetime.utcnow(),
            categories=COMPREHENSIVE_AUDIT_CHECKLIST["categories"],
            items=COMPREHENSIVE_AUDIT_CHECKLIST["items"],
            total_items=len(COMPREHENSIVE_AUDIT_CHECKLIST["items"]),
            total_categories=len(COMPREHENSIVE_AUDIT_CHECKLIST["categories"]),
            iso_45001_clauses=COMPREHENSIVE_AUDIT_CHECKLIST["iso_45001_clauses"],
            osha_standards=COMPREHENSIVE_AUDIT_CHECKLIST["osha_standards"],
            local_regulations=COMPREHENSIVE_AUDIT_CHECKLIST["local_regulations"],
            is_active=True,
            is_default=True,
            created_by=created_by
        )
        
        session.add(checklist)
        session.commit()
        
        result = {
            "message": "Standard checklist template created successfully",
            "checklist_id": checklist.id,
            "total_items": checklist.total_items
        }
        
        session.close()
        return result
        
    except Exception as e:
        session.rollback()
        session.close()
        raise e
