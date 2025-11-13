"""
Quality Training with QR Attendance API (Cross-App Feature)

REQUIRES: Company must have BOTH Safety + Concrete app subscriptions

Provides QR-based attendance tracking for quality/technical training:
- Mix design training
- Quality procedures training
- Technical competency training
- Certification programs

Trainer scans worker QR codes (same as TBT - workers don't have smartphones!)
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

from flask_jwt_extended import get_jwt_identity

try:
    from .db import session_scope
    from .training_attendance_models import TrainingAttendance
    from .models import TrainingRecord, User, Project, ProjectMembership
    from .safety_models import Worker
    from .subscription_middleware import require_both_apps
except ImportError:
    from db import session_scope
    from training_attendance_models import TrainingAttendance
    from models import TrainingRecord, User, Project, ProjectMembership
    from safety_models import Worker
    from subscription_middleware import require_both_apps


def get_current_user_id():
    """Extract user_id from JWT identity."""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('user_id')
    return int(identity)

import logging
logger = logging.getLogger(__name__)

training_qr_bp = Blueprint('training_qr', __name__)


# ============================================================================
# WORKER QR ATTENDANCE FOR QUALITY TRAINING (CROSS-APP FEATURE)
# ============================================================================

@training_qr_bp.route('/api/training/<int:training_id>/scan-worker', methods=['POST'])
@require_both_apps()
def scan_worker_for_training(training_id):
    """
    Trainer scans worker's QR code (helmet sticker) to mark training attendance
    
    REQUIRES: Company has BOTH Safety + Concrete apps
    
    Body:
    {
        "worker_code": "W12345",
        "device_info": "iPad Pro" (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            # Get training record
            training = session.query(TrainingRecord).filter_by(id=training_id).first()
            
            if not training:
                return jsonify({"error": "Training record not found"}), 404
            
            # Only trainer can scan
            if training.trainer_id != user_id:
                return jsonify({"error": "Only trainer can scan worker QR"}), 403
            
            worker_code = data.get("worker_code")
            if not worker_code:
                return jsonify({"error": "Worker code is required"}), 400
            
            # Look up registered worker from Safety app
            worker = session.query(Worker).filter_by(
                worker_code=worker_code,
                project_id=training.project_id
            ).first()
            
            if not worker:
                return jsonify({"error": f"Worker {worker_code} not found in this project"}), 404
            
            # Check if already attended
            existing = session.query(TrainingAttendance).filter_by(
                training_record_id=training_id,
                worker_code=worker_code
            ).first()
            
            if existing:
                return jsonify({
                    "success": False,
                    "message": f"{worker.full_name} already marked attendance at {existing.check_in_time.strftime('%H:%M:%S')}",
                    "attendance": existing.to_dict()
                }), 200
            
            # Create attendance record
            attendance = TrainingAttendance(
                training_record_id=training_id,
                worker_id=worker.id,
                worker_name=worker.full_name,
                worker_code=worker.worker_code,
                worker_company=worker.company_name,
                worker_trade=worker.trade,
                check_in_method='qr',
                check_in_time=datetime.utcnow(),
                qr_code_scanned=f"WORKER-{worker_code}",
                device_info=data.get("device_info", "Unknown device"),
                has_signed=True,
                signature_timestamp=datetime.utcnow()
            )
            
            session.add(attendance)
            session.flush()
            
            logger.info(f"Worker {worker.full_name} ({worker_code}) marked attendance for training {training_id}")
            
            return jsonify({
                "success": True,
                "message": f"{worker.full_name} attendance marked successfully",
                "attendance": attendance.to_dict(),
                "worker": {
                    "name": worker.full_name,
                    "code": worker.worker_code,
                    "company": worker.company_name,
                    "trade": worker.trade,
                    "checkInTime": attendance.check_in_time.strftime('%H:%M:%S')
                }
            }), 201
            
    except Exception as e:
        logger.error(f"Error scanning worker QR for training: {str(e)}")
        return jsonify({"error": str(e)}), 500


@training_qr_bp.route('/api/training/<int:training_id>/attendance-manual', methods=['POST'])
@require_both_apps()
def add_manual_training_attendance(training_id):
    """
    Trainer manually adds worker attendance (fallback if QR not working)
    
    REQUIRES: Company has BOTH Safety + Concrete apps
    
    Body:
    {
        "worker_code": "W12345" OR "worker_name": "John Doe"
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            training = session.query(TrainingRecord).filter_by(id=training_id).first()
            
            if not training:
                return jsonify({"error": "Training record not found"}), 404
            
            # Only trainer can add attendance
            if training.trainer_id != user_id:
                return jsonify({"error": "Only trainer can add attendance"}), 403
            
            worker_code = data.get("worker_code")
            worker_name = data.get("worker_name")
            worker = None
            
            if worker_code:
                # Look up worker
                worker = session.query(Worker).filter_by(
                    worker_code=worker_code,
                    project_id=training.project_id
                ).first()
                
                if worker:
                    worker_name = worker.full_name
            
            if not worker_name:
                return jsonify({"error": "Worker name or code required"}), 400
            
            # Create manual attendance
            attendance = TrainingAttendance(
                training_record_id=training_id,
                worker_id=worker.id if worker else None,
                worker_name=worker_name,
                worker_code=worker_code or "MANUAL",
                worker_company=data.get("worker_company") or (worker.company_name if worker else None),
                worker_trade=data.get("worker_trade") or (worker.trade if worker else None),
                check_in_method="manual",
                check_in_time=datetime.utcnow(),
                qr_code_scanned=None,
                device_info="Manual entry",
                has_signed=True,
                signature_timestamp=datetime.utcnow()
            )
            
            session.add(attendance)
            
            logger.info(f"Manual attendance added: {worker_name} for training {training_id}")
            
            return jsonify({
                "success": True,
                "attendance": attendance.to_dict()
            }), 201
            
    except Exception as e:
        logger.error(f"Error adding manual training attendance: {str(e)}")
        return jsonify({"error": str(e)}), 500


@training_qr_bp.route('/api/training/<int:training_id>/attendance', methods=['GET'])
@require_both_apps()
def get_training_attendance(training_id):
    """Get all attendance records for a training session"""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            training = session.query(TrainingRecord).filter_by(id=training_id).first()
            
            if not training:
                return jsonify({"error": "Training record not found"}), 404
            
            # Verify access
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=training.project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "No access to this training"}), 403
            
            # Get all attendances
            attendances = session.query(TrainingAttendance).filter_by(
                training_record_id=training_id
            ).order_by(TrainingAttendance.check_in_time).all()
            
            return jsonify({
                "success": True,
                "training": {
                    "id": training.id,
                    "topic": training.training_topic,
                    "trainer": training.trainer.full_name if training.trainer else "Unknown",
                    "date": training.training_date.isoformat(),
                    "location": training.building,
                    "activity": training.activity
                },
                "attendances": [a.to_dict() for a in attendances],
                "attendanceCount": len(attendances)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching training attendance: {str(e)}")
        return jsonify({"error": str(e)}), 500


@training_qr_bp.route('/api/training/<int:training_id>/assessment', methods=['POST'])
@require_both_apps()
def record_worker_assessment(training_id):
    """
    Record assessment score for worker after training
    
    Body:
    {
        "attendance_id": 123,
        "score": 85.5,
        "passed": true,
        "issue_certificate": true
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            training = session.query(TrainingRecord).filter_by(id=training_id).first()
            
            if not training or training.trainer_id != user_id:
                return jsonify({"error": "Unauthorized"}), 403
            
            attendance = session.query(TrainingAttendance).filter_by(
                id=data["attendance_id"],
                training_record_id=training_id
            ).first()
            
            if not attendance:
                return jsonify({"error": "Attendance record not found"}), 404
            
            # Update assessment details
            attendance.assessment_score = data.get("score")
            attendance.passed_assessment = data.get("passed")
            
            if data.get("issue_certificate") and data.get("passed"):
                attendance.certificate_issued = True
                attendance.certificate_number = f"CERT-{training_id}-{attendance.id}-{datetime.utcnow().strftime('%Y%m%d')}"
            
            logger.info(f"Assessment recorded for {attendance.worker_name}: {data.get('score')}")
            
            return jsonify({
                "success": True,
                "attendance": attendance.to_dict()
            }), 200
            
    except Exception as e:
        logger.error(f"Error recording assessment: {str(e)}")
        return jsonify({"error": str(e)}), 500


@training_qr_bp.route('/api/training/reports/worker-certifications', methods=['GET'])
@require_both_apps()
def worker_certifications_report():
    """
    Get worker certification report
    
    Query params:
    - project_id (optional)
    - worker_code (optional)
    """
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            # Get user's projects
            memberships = session.query(ProjectMembership).filter_by(user_id=user_id).all()
            project_ids = [m.project_id for m in memberships]
            
            # Base query
            query = session.query(TrainingAttendance).join(TrainingRecord).filter(
                TrainingRecord.project_id.in_(project_ids),
                TrainingAttendance.certificate_issued == True
            )
            
            # Apply filters
            if request.args.get('project_id'):
                query = query.filter(TrainingRecord.project_id == int(request.args['project_id']))
            
            if request.args.get('worker_code'):
                query = query.filter(TrainingAttendance.worker_code == request.args['worker_code'])
            
            certifications = query.order_by(TrainingAttendance.created_at.desc()).all()
            
            # Group by worker
            worker_certs = {}
            for cert in certifications:
                code = cert.worker_code
                if code not in worker_certs:
                    worker_certs[code] = {
                        "workerCode": code,
                        "workerName": cert.worker_name,
                        "company": cert.worker_company,
                        "trade": cert.worker_trade,
                        "certifications": []
                    }
                
                worker_certs[code]["certifications"].append({
                    "certificateNumber": cert.certificate_number,
                    "trainingTopic": cert.training_record.training_topic,
                    "trainingDate": cert.training_record.training_date.isoformat(),
                    "score": cert.assessment_score,
                    "issuedAt": cert.updated_at.isoformat()
                })
            
            return jsonify({
                "success": True,
                "workers": list(worker_certs.values()),
                "totalWorkers": len(worker_certs),
                "totalCertifications": len(certifications)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching certifications report: {str(e)}")
        return jsonify({"error": str(e)}), 500
