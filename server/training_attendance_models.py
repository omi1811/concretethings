"""
Quality Training with QR Attendance (Cross-App Feature)

IMPORTANT: This feature is ONLY available when company has BOTH Safety + Concrete apps!

Extends TrainingRecord with worker QR attendance tracking:
- Trainer conducts quality training (concrete/QMS topics)
- Workers registered in Safety app can attend
- Trainer scans worker QR codes (helmet stickers) for attendance
- Similar to TBT attendance but for quality/technical training
"""

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

try:
    from .db import Base
except ImportError:
    from db import Base


class TrainingAttendance(Base):
    """
    Worker attendance for quality training sessions (cross-app feature)
    
    Links:
    - training_records (Concrete app)
    - safety_workers (Safety app)
    
    Only available when company has BOTH apps subscribed!
    """
    __tablename__ = "training_attendances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Link to training record (from Concrete/QMS app)
    training_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_records.id"), nullable=False)
    
    # Worker details (from Safety app)
    worker_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("safety_workers.id"), nullable=True)
    worker_name: Mapped[str] = mapped_column(String(255), nullable=False)
    worker_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    worker_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    worker_trade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Attendance tracking
    check_in_method: Mapped[str] = mapped_column(String(20), default='qr')  # qr, manual
    check_in_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    qr_code_scanned: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Which QR code was used
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Device used to scan
    
    # Assessment/certification (optional)
    assessment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    passed_assessment: Mapped[Optional[bool]] = mapped_column(Integer, nullable=True)
    certificate_issued: Mapped[bool] = mapped_column(Integer, default=0)
    certificate_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Digital signature
    has_signed: Mapped[bool] = mapped_column(Integer, default=False)
    signature_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    training_record = relationship("TrainingRecord", backref="attendances")
    worker = relationship("Worker", backref="training_attendances")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trainingRecordId": self.training_record_id,
            "workerId": self.worker_id,
            "workerName": self.worker_name,
            "workerCode": self.worker_code,
            "workerCompany": self.worker_company,
            "workerTrade": self.worker_trade,
            "checkInMethod": self.check_in_method,
            "checkInTime": self.check_in_time.isoformat(),
            "qrCodeScanned": self.qr_code_scanned,
            "deviceInfo": self.device_info,
            "assessmentScore": self.assessment_score,
            "passedAssessment": bool(self.passed_assessment) if self.passed_assessment is not None else None,
            "certificateIssued": bool(self.certificate_issued),
            "certificateNumber": self.certificate_number,
            "hasSigned": bool(self.has_signed),
            "signatureTimestamp": self.signature_timestamp.isoformat() if self.signature_timestamp else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
