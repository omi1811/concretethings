"""
Safety Induction Models

Worker onboarding and induction management with Aadhar verification,
terms acceptance, safety quiz, and certificate issuance.

Compliance: ISO 45001:2018 Clause 7.2 (Competence)
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .models import Base


class SafetyInduction(Base):
    """
    Safety Induction records for worker onboarding.
    
    Tracks complete induction process:
    - Induction topics covered (18 standard topics)
    - Safety video playback
    - Quiz assessment (10 questions)
    - Aadhar card verification
    - Terms & conditions acceptance
    - Digital signatures
    - Certificate issuance
    """
    __tablename__ = 'safety_inductions'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    worker_id = Column(Integer, ForeignKey('safety_workers.id'), nullable=False)
    conducted_by = Column(Integer, ForeignKey('users.id'), nullable=False)  # Safety Officer
    
    # Induction details
    induction_number = Column(String(50), unique=True, nullable=False)  # IND-{project}-{year}-{seq}
    induction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Topics covered (JSON array)
    # Example: ["PPE Usage", "Working at Height", "Fire Safety", ...]
    induction_topics = Column(JSON, nullable=False)
    
    # Video playback tracking
    video_watched = Column(Boolean, default=False)
    video_url = Column(String(500))  # YouTube, Vimeo, or local storage
    video_duration_seconds = Column(Integer)  # Total video length
    video_watched_seconds = Column(Integer, default=0)  # How much worker watched
    video_completed_at = Column(DateTime)
    
    # Quiz assessment
    quiz_taken = Column(Boolean, default=False)
    quiz_questions = Column(JSON)  # Array of questions with answers
    quiz_answers = Column(JSON)  # Worker's answers
    quiz_score = Column(Integer)  # Out of 10
    quiz_passing_score = Column(Integer, default=7)  # Minimum to pass
    quiz_passed = Column(Boolean, default=False)
    quiz_attempts = Column(Integer, default=0)
    quiz_completed_at = Column(DateTime)
    
    # Aadhar verification (from Worker model, duplicated for history)
    aadhar_number = Column(String(12))  # 12 digits
    aadhar_verified = Column(Boolean, default=False)
    aadhar_verified_by = Column(Integer, ForeignKey('users.id'))  # Safety Officer who verified
    aadhar_verified_at = Column(DateTime)
    aadhar_verification_notes = Column(Text)
    
    # Terms & conditions
    terms_version = Column(String(20))  # "v1.0", "v2.0", etc.
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime)
    terms_pdf_path = Column(String(500))  # S3 path to T&C PDF
    
    # Digital signatures (base64 encoded images)
    worker_signature = Column(Text)  # Worker's signature
    worker_signature_ip = Column(String(50))  # IP address when signed
    worker_signed_at = Column(DateTime)
    
    safety_officer_signature = Column(Text)  # Safety Officer's signature
    safety_officer_signed_at = Column(DateTime)
    
    witness_name = Column(String(200))  # Optional witness
    witness_signature = Column(Text)
    witness_signed_at = Column(DateTime)
    
    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_number = Column(String(100))  # IND-CERT-{worker_id}-{date}
    certificate_pdf_path = Column(String(500))  # S3 path
    certificate_issued_at = Column(DateTime)
    
    # Validity
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)  # 1 year from induction_date
    is_expired = Column(Boolean, default=False)
    
    # Re-induction tracking
    is_reinduction = Column(Boolean, default=False)
    previous_induction_id = Column(Integer, ForeignKey('safety_inductions.id'))
    reinduction_reason = Column(String(500))  # "Annual renewal", "Long absence", etc.
    
    # Status
    status = Column(String(50), default='pending')  # pending, in_progress, quiz_pending, completed, expired, failed
    
    # Remarks
    remarks = Column(Text)
    internal_notes = Column(Text)  # Safety Officer notes (not visible to worker)
    
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
    worker = relationship("Worker", foreign_keys=[worker_id], backref="inductions")
    conductor = relationship("User", foreign_keys=[conducted_by])
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'inductionNumber': self.induction_number,
            'inductionDate': self.induction_date.isoformat() if self.induction_date else None,
            'worker': {
                'id': self.worker.id,
                'name': self.worker.worker_name,
                'code': self.worker.worker_code,
                'company': self.worker.worker_company,
                'trade': self.worker.worker_trade,
            } if self.worker else None,
            'conductedBy': {
                'id': self.conductor.id,
                'name': self.conductor.full_name,
                'role': self.conductor.role,
            } if self.conductor else None,
            'inductionTopics': self.induction_topics or [],
            'videoWatched': self.video_watched,
            'videoProgress': {
                'duration': self.video_duration_seconds,
                'watched': self.video_watched_seconds,
                'percentage': round((self.video_watched_seconds / self.video_duration_seconds * 100), 2) if self.video_duration_seconds else 0,
                'completedAt': self.video_completed_at.isoformat() if self.video_completed_at else None,
            },
            'quiz': {
                'taken': self.quiz_taken,
                'score': self.quiz_score,
                'passingScore': self.quiz_passing_score,
                'passed': self.quiz_passed,
                'attempts': self.quiz_attempts,
                'completedAt': self.quiz_completed_at.isoformat() if self.quiz_completed_at else None,
            },
            'aadhar': {
                'number': self.aadhar_number[-4:] if self.aadhar_number else None,  # Last 4 digits only
                'verified': self.aadhar_verified,
                'verifiedAt': self.aadhar_verified_at.isoformat() if self.aadhar_verified_at else None,
            },
            'terms': {
                'version': self.terms_version,
                'accepted': self.terms_accepted,
                'acceptedAt': self.terms_accepted_at.isoformat() if self.terms_accepted_at else None,
            },
            'signatures': {
                'worker': bool(self.worker_signature),
                'workerSignedAt': self.worker_signed_at.isoformat() if self.worker_signed_at else None,
                'safetyOfficer': bool(self.safety_officer_signature),
                'safetyOfficerSignedAt': self.safety_officer_signed_at.isoformat() if self.safety_officer_signed_at else None,
                'witness': self.witness_name if self.witness_name else None,
            },
            'certificate': {
                'issued': self.certificate_issued,
                'number': self.certificate_number,
                'issuedAt': self.certificate_issued_at.isoformat() if self.certificate_issued_at else None,
                'pdfPath': self.certificate_pdf_path,
            },
            'validity': {
                'validFrom': self.valid_from.isoformat() if self.valid_from else None,
                'validUntil': self.valid_until.isoformat() if self.valid_until else None,
                'isExpired': self.is_expired,
                'daysRemaining': (self.valid_until - datetime.now().date()).days if self.valid_until and not self.is_expired else 0,
            },
            'isReinduction': self.is_reinduction,
            'reinductionReason': self.reinduction_reason,
            'status': self.status,
            'remarks': self.remarks,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class InductionTopic(Base):
    """
    Standard safety induction topics library.
    
    18 standard topics as per ISO 45001 and OSHA requirements.
    """
    __tablename__ = 'induction_topics'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Topic details
    topic_name = Column(String(200), nullable=False)
    topic_description = Column(Text)
    topic_category = Column(String(100))  # "PPE", "Fire Safety", "Emergency", etc.
    
    # Content
    key_points = Column(JSON)  # Array of bullet points
    dos_and_donts = Column(JSON)  # {dos: [...], donts: [...]}
    reference_standards = Column(JSON)  # ["IS 3786", "OSHA 1926.21", ...]
    
    # Media
    video_url = Column(String(500))
    images = Column(JSON)  # Array of image URLs
    documents = Column(JSON)  # Array of PDF URLs
    
    # Quiz questions for this topic
    quiz_questions = Column(JSON)  # [{question, options: [], correct_answer, explanation}]
    
    # Usage
    is_mandatory = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'topicName': self.topic_name,
            'topicDescription': self.topic_description,
            'category': self.topic_category,
            'keyPoints': self.key_points or [],
            'dosAndDonts': self.dos_and_donts or {},
            'referenceStandards': self.reference_standards or [],
            'videoUrl': self.video_url,
            'images': self.images or [],
            'documents': self.documents or [],
            'quizQuestions': len(self.quiz_questions) if self.quiz_questions else 0,
            'isMandatory': self.is_mandatory,
            'isActive': self.is_active,
            'displayOrder': self.display_order,
        }


# Standard 18 induction topics (to be seeded)
STANDARD_INDUCTION_TOPICS = [
    {
        "topic_name": "Personal Protective Equipment (PPE)",
        "topic_category": "PPE",
        "key_points": [
            "Mandatory PPE: Safety helmet, steel-toe boots, safety vest",
            "PPE must be worn at all times on site",
            "Check PPE condition before use",
            "Report damaged PPE immediately",
            "Helmet validity: 3 years from manufacturing"
        ],
        "is_mandatory": True,
        "display_order": 1
    },
    {
        "topic_name": "Working at Height",
        "topic_category": "Fall Prevention",
        "key_points": [
            "Height > 1.8 meters requires fall protection",
            "Use proper scaffolding with guardrails and toe boards",
            "Full body harness mandatory above 6 meters",
            "Check scaffolding tag (green/yellow/red)",
            "Never jump between platforms"
        ],
        "is_mandatory": True,
        "display_order": 2
    },
    {
        "topic_name": "Fire Safety & Emergency Procedures",
        "topic_category": "Emergency",
        "key_points": [
            "Know fire extinguisher locations (every 30 meters)",
            "Assembly point location (green signage)",
            "Fire alarm sound recognition",
            "Emergency contact numbers displayed",
            "Never use lift during fire emergency"
        ],
        "is_mandatory": True,
        "display_order": 3
    },
    {
        "topic_name": "Excavation Safety",
        "topic_category": "Ground Work",
        "key_points": [
            "Excavation > 1.2m requires shoring/sloping",
            "Barricading mandatory around excavations",
            "Check for underground utilities before digging",
            "Ladder access for excavations > 1.2m",
            "Daily inspection by competent person"
        ],
        "is_mandatory": True,
        "display_order": 4
    },
    {
        "topic_name": "Electrical Safety",
        "topic_category": "Electrical",
        "key_points": [
            "Only authorized electricians for electrical work",
            "ELCB/RCCB mandatory for power tools",
            "Check cable condition before use",
            "Minimum 2 meters clearance from overhead lines",
            "Never touch electrical equipment with wet hands"
        ],
        "is_mandatory": True,
        "display_order": 5
    },
    {
        "topic_name": "Housekeeping",
        "topic_category": "General Safety",
        "key_points": [
            "Keep walkways clear (min 1 meter width)",
            "Material stacking height < 1.5 meters",
            "Segregate waste (construction, hazardous, general)",
            "Clean spills immediately",
            "Tools and materials stored properly after use"
        ],
        "is_mandatory": True,
        "display_order": 6
    },
    {
        "topic_name": "Toolbox Talks (TBT)",
        "topic_category": "Daily Safety",
        "key_points": [
            "Daily TBT mandatory before work starts",
            "Duration: 15-30 minutes",
            "Covers: Today's work, hazards, PPE, emergency procedures",
            "Attendance via QR code scanning",
            "Conductor explains in local language"
        ],
        "is_mandatory": True,
        "display_order": 7
    },
    {
        "topic_name": "Permit-to-Work System",
        "topic_category": "Work Authorization",
        "key_points": [
            "PTW required for: Hot work, confined space, height, excavation, electrical, lifting",
            "3-level approval: Contractor → Site Engineer → Safety Officer",
            "Valid only for specified duration",
            "Display permit at work location",
            "Stop work immediately if permit expires"
        ],
        "is_mandatory": True,
        "display_order": 8
    },
    {
        "topic_name": "Confined Space Entry",
        "topic_category": "Specialized Work",
        "key_points": [
            "Confined space: Limited entry/exit, not designed for continuous occupancy",
            "Gas testing mandatory before entry",
            "Continuous ventilation required",
            "Attendant stationed outside",
            "Communication system (radio/rope signals)"
        ],
        "is_mandatory": True,
        "display_order": 9
    },
    {
        "topic_name": "Material Handling & Lifting",
        "topic_category": "Material Handling",
        "key_points": [
            "Maximum manual lift: 25kg per person",
            "Use mechanical aids for heavy loads",
            "Lifting equipment inspection (daily)",
            "Qualified rigger and signalman required",
            "Keep clear of suspended loads"
        ],
        "is_mandatory": True,
        "display_order": 10
    },
    {
        "topic_name": "Incident Reporting",
        "topic_category": "Emergency Response",
        "key_points": [
            "Report ALL incidents (fatality, injury, near-miss, property damage)",
            "Immediate reporting to Safety Officer",
            "Don't disturb incident scene (unless emergency)",
            "Witness statements important",
            "No-blame culture for near-miss reporting"
        ],
        "is_mandatory": True,
        "display_order": 11
    },
    {
        "topic_name": "First Aid & Medical Emergency",
        "topic_category": "Emergency",
        "key_points": [
            "First aid box location (every floor/area)",
            "Trained first aider contact number",
            "Nearest hospital: [To be filled]",
            "Ambulance contact: 108",
            "Don't move seriously injured person (unless immediate danger)"
        ],
        "is_mandatory": True,
        "display_order": 12
    },
    {
        "topic_name": "Chemical & Hazardous Material Safety",
        "topic_category": "Hazardous Materials",
        "key_points": [
            "Read Material Safety Data Sheet (MSDS) before use",
            "Store chemicals in labeled containers",
            "Use appropriate PPE (gloves, goggles, respirator)",
            "Spill kit location and usage",
            "Dispose hazardous waste in designated area"
        ],
        "is_mandatory": False,
        "display_order": 13
    },
    {
        "topic_name": "Scaffolding Safety",
        "topic_category": "Fall Prevention",
        "key_points": [
            "Scaffolding erected by trained scaffolders only",
            "Green tag: Safe to use, Yellow: Caution, Red: Do not use",
            "Maximum load: 225 kg/m² (working platform)",
            "Guardrails mandatory (top, mid, toe board)",
            "Inspect daily before use"
        ],
        "is_mandatory": True,
        "display_order": 14
    },
    {
        "topic_name": "Vehicle & Mobile Equipment Safety",
        "topic_category": "Vehicle Safety",
        "key_points": [
            "Only authorized drivers operate equipment",
            "Pedestrians have right of way",
            "Reverse alarm and flashing beacon mandatory",
            "Banksman required for reversing",
            "Never stand/walk under crane load"
        ],
        "is_mandatory": True,
        "display_order": 15
    },
    {
        "topic_name": "Hot Work Safety",
        "topic_category": "Specialized Work",
        "key_points": [
            "Hot work: Welding, cutting, grinding, torch operations",
            "Permit mandatory for all hot work",
            "Fire extinguisher within 10 meters",
            "Fire watch for 60 minutes after completion",
            "Remove flammable materials within 10-meter radius"
        ],
        "is_mandatory": True,
        "display_order": 16
    },
    {
        "topic_name": "Concrete Pouring Safety",
        "topic_category": "Specialized Work",
        "key_points": [
            "Check formwork stability before pouring",
            "Scaffolding/platforms properly supported",
            "PPE: Helmet, boots, gloves, goggles",
            "Concrete can cause chemical burns (alkaline)",
            "Wash skin immediately if contact occurs"
        ],
        "is_mandatory": True,
        "display_order": 17
    },
    {
        "topic_name": "Weather-Related Hazards",
        "topic_category": "Environmental",
        "key_points": [
            "Stop work during heavy rain/thunderstorm",
            "No work at height if wind speed > 40 km/h",
            "Hydration stations in summer (ORS, water)",
            "Lightning: Move to safe location immediately",
            "Monsoon: Extra caution on wet surfaces"
        ],
        "is_mandatory": False,
        "display_order": 18
    }
]
