"""
Toolbox Talk (TBT) API with QR Code Attendance

IMPORTANT: Workers DO NOT have smartphones!
- Only CONDUCTOR scans worker QR codes (helmet stickers)
- No session QR code scanning by workers
- Conductor uses tablet/phone to scan each worker's QR

Complete API for TBT management with:
- Session creation and management
- Worker QR code generation (helmet stickers)
- Conductor scans worker QR codes for attendance
- Conductor information tracking
- Topic library management
- Compliance reporting
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import secrets
import qrcode
import io
import base64
from functools import wraps

from flask_jwt_extended import get_jwt_identity

try:
    from .db import session_scope
    from .tbt_models import TBTSession, TBTAttendance, TBTTopic
    from .safety_models import Worker
    from .models import User, Project, ProjectMembership
except ImportError:
    from db import session_scope
    from tbt_models import TBTSession, TBTAttendance, TBTTopic
    from safety_models import Worker
    from models import User, Project, ProjectMembership


def get_current_user_id():
    """Extract user_id from JWT identity."""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('user_id')
    return int(identity)

import logging
logger = logging.getLogger(__name__)

tbt_bp = Blueprint('tbt', __name__)


def generate_tbt_qr_token():
    """Generate unique token for TBT session QR code"""
    return f"TBT-{secrets.token_urlsafe(16)}"


def generate_qr_code(data):
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


# ============================================================================
# TBT SESSION MANAGEMENT
# ============================================================================

@tbt_bp.route('/api/tbt/sessions', methods=['POST'])
def create_tbt_session():
    """
    Create new TBT session
    
    Body:
    {
        "project_id": 1,
        "topic": "Concrete Pouring Safety",
        "topic_category": "Activity-Specific",
        "location": "Block A, Floor 5",
        "activity": "Concreting",
        "duration_minutes": 30,
        "key_points": ["Check formwork", "PPE mandatory"],
        "hazards_discussed": ["Falls", "Concrete burns"],
        "ppe_required": ["Helmet", "Boots", "Gloves"],
        "emergency_contacts": {"first_aid": "555-1234"},
        "weather_conditions": "Clear, 28°C",
        "special_notes": "New workers on site"
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            # Get user details for conductor info
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify project access
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=data["project_id"]
            ).first()
            
            if not membership:
                return jsonify({"error": "No access to this project"}), 403
            
            # Generate QR code token
            qr_token = generate_tbt_qr_token()
            qr_expires = datetime.utcnow() + timedelta(hours=12)  # QR valid for 12 hours
            
            # Create session
            tbt_session = TBTSession(
                project_id=data["project_id"],
                conductor_id=user_id,
                conductor_name=user.full_name,
                conductor_role=data.get("conductor_role", user.role),
                session_date=datetime.utcnow(),
                topic=data["topic"],
                topic_category=data.get("topic_category"),
                location=data["location"],
                activity=data["activity"],
                duration_minutes=data.get("duration_minutes", 30),
                key_points=json.dumps(data.get("key_points", [])),
                hazards_discussed=json.dumps(data.get("hazards_discussed", [])),
                ppe_required=json.dumps(data.get("ppe_required", [])),
                emergency_contacts=json.dumps(data.get("emergency_contacts", {})),
                weather_conditions=data.get("weather_conditions"),
                special_notes=data.get("special_notes"),
                status="active",
                qr_code_data=qr_token,
                qr_code_expires_at=qr_expires
            )
            
            session.add(tbt_session)
            session.flush()
            
            # Generate QR code image
            qr_url = f"{request.host_url}api/tbt/attend/{qr_token}"
            qr_image = generate_qr_code(qr_url)
            
            logger.info(f"TBT session created: {tbt_session.id} by {user.full_name}")
            
            return jsonify({
                "success": True,
                "session": tbt_session.to_dict(),
                "qrCode": qr_image,
                "qrUrl": qr_url
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating TBT session: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/sessions/<int:session_id>', methods=['GET'])
def get_tbt_session(session_id):
    """Get TBT session details with attendances"""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            tbt_session = session.query(TBTSession).filter_by(id=session_id).first()
            
            if not tbt_session:
                return jsonify({"error": "Session not found"}), 404
            
            # Verify access
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=tbt_session.project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "No access to this session"}), 403
            
            return jsonify({
                "success": True,
                "session": tbt_session.to_dict(include_attendances=True)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching TBT session: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/sessions', methods=['GET'])
def list_tbt_sessions():
    """
    List TBT sessions with filters
    
    Query params:
    - project_id (optional)
    - date_from (optional)
    - date_to (optional)
    - conductor_id (optional)
    - activity (optional)
    - status (optional)
    """
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            # Get user's projects
            memberships = session.query(ProjectMembership).filter_by(user_id=user_id).all()
            project_ids = [m.project_id for m in memberships]
            
            # Base query
            query = session.query(TBTSession).filter(
                TBTSession.project_id.in_(project_ids)
            )
            
            # Apply filters
            if request.args.get('project_id'):
                query = query.filter(TBTSession.project_id == int(request.args['project_id']))
            
            if request.args.get('date_from'):
                date_from = datetime.fromisoformat(request.args['date_from'])
                query = query.filter(TBTSession.session_date >= date_from)
            
            if request.args.get('date_to'):
                date_to = datetime.fromisoformat(request.args['date_to'])
                query = query.filter(TBTSession.session_date <= date_to)
            
            if request.args.get('conductor_id'):
                query = query.filter(TBTSession.conductor_id == int(request.args['conductor_id']))
            
            if request.args.get('activity'):
                query = query.filter(TBTSession.activity == request.args['activity'])
            
            if request.args.get('status'):
                query = query.filter(TBTSession.status == request.args['status'])
            
            # Order by date desc
            query = query.order_by(TBTSession.session_date.desc())
            
            sessions = query.all()
            
            return jsonify({
                "success": True,
                "sessions": [s.to_dict() for s in sessions],
                "count": len(sessions)
            }), 200
            
    except Exception as e:
        logger.error(f"Error listing TBT sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/sessions/<int:session_id>/complete', methods=['POST'])
def complete_tbt_session(session_id):
    """Mark TBT session as completed"""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            tbt_session = session.query(TBTSession).filter_by(id=session_id).first()
            
            if not tbt_session:
                return jsonify({"error": "Session not found"}), 404
            
            # Only conductor can complete
            if tbt_session.conductor_id != user_id:
                return jsonify({"error": "Only conductor can complete session"}), 403
            
            tbt_session.is_completed = True
            tbt_session.completed_at = datetime.utcnow()
            tbt_session.status = "completed"
            
            logger.info(f"TBT session {session_id} completed")
            
            return jsonify({
                "success": True,
                "session": tbt_session.to_dict()
            }), 200
            
    except Exception as e:
        logger.error(f"Error completing TBT session: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CONDUCTOR SCANS WORKER QR CODE (Workers don't have smartphones!)
# ============================================================================

@tbt_bp.route('/api/tbt/sessions/<int:session_id>/scan-worker', methods=['POST'])
def scan_worker_qr(session_id):
    """
    Conductor scans worker's QR code (helmet sticker) to mark attendance
    
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
            # Get TBT session
            tbt_session = session.query(TBTSession).filter_by(id=session_id).first()
            
            if not tbt_session:
                return jsonify({"error": "Session not found"}), 404
            
            # Only conductor can scan
            if tbt_session.conductor_id != user_id:
                return jsonify({"error": "Only conductor can scan worker QR"}), 403
            
            worker_code = data.get("worker_code")
            if not worker_code:
                return jsonify({"error": "Worker code is required"}), 400
            
            # Look up registered worker
            worker = session.query(Worker).filter_by(
                worker_code=worker_code,
                project_id=tbt_session.project_id
            ).first()
            
            if not worker:
                return jsonify({"error": f"Worker {worker_code} not found in this project"}), 404
            
            # Check if already attended
            existing = session.query(TBTAttendance).filter_by(
                session_id=tbt_session.id,
                worker_code=worker_code
            ).first()
            
            if existing:
                return jsonify({
                    "success": False,
                    "message": f"{worker.full_name} already marked attendance at {existing.check_in_time.strftime('%H:%M:%S')}",
                    "attendance": existing.to_dict()
                }), 200
            
            # Create attendance record
            attendance = TBTAttendance(
                session_id=tbt_session.id,
                worker_id=worker.id,
                worker_name=worker.full_name,
                worker_code=worker.worker_code,
                worker_company=worker.company_name,
                worker_trade=worker.trade,
                check_in_method='qr',
                check_in_time=datetime.utcnow(),
                qr_code_scanned=f"WORKER-{worker_code}",
                device_info=data.get("device_info", "Unknown device")
            )
            
            session.add(attendance)
            session.flush()
            
            logger.info(f"Worker {worker.full_name} ({worker_code}) marked attendance via QR scan")
            
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
        logger.error(f"Error scanning worker QR: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/sessions/<int:session_id>/attendance-manual', methods=['POST'])
def add_manual_attendance(session_id):
    """
    Conductor manually adds worker attendance (fallback if QR not working)
    
    Body:
    {
        "worker_code": "W12345" OR "worker_name": "John Doe"
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            tbt_session = session.query(TBTSession).filter_by(id=session_id).first()
            
            if not tbt_session:
                return jsonify({"error": "Session not found"}), 404
            
            # Only conductor can add attendance
            if tbt_session.conductor_id != user_id:
                return jsonify({"error": "Only conductor can add attendance"}), 403
            
            worker_code = data.get("worker_code")
            worker_name = data.get("worker_name")
            worker = None
            
            if worker_code:
                # Look up worker
                worker = session.query(Worker).filter_by(
                    worker_code=worker_code,
                    project_id=tbt_session.project_id
                ).first()
                
                if worker:
                    worker_name = worker.full_name
            
            if not worker_name:
                return jsonify({"error": "Worker name or code required"}), 400
            
            # Create manual attendance
            attendance = TBTAttendance(
                session_id=session_id,
                worker_id=worker.id if worker else None,
                worker_name=worker_name,
                worker_code=worker_code,
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
            
            logger.info(f"Manual attendance added: {worker_name} for TBT {session_id}")
            
            return jsonify({
                "success": True,
                "attendance": attendance.to_dict()
            }), 201
            
    except Exception as e:
        logger.error(f"Error adding manual attendance: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/sessions/<int:session_id>/attendance', methods=['GET'])
def get_session_attendance(session_id):
    """Get all attendance records for a TBT session"""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            tbt_session = session.query(TBTSession).filter_by(id=session_id).first()
            
            if not tbt_session:
                return jsonify({"error": "Session not found"}), 404
            
            # Verify access
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=tbt_session.project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "No access"}), 403
            
            attendances = session.query(TBTAttendance).filter_by(
                session_id=session_id
            ).order_by(TBTAttendance.check_in_time).all()
            
            return jsonify({
                "success": True,
                "attendances": [a.to_dict() for a in attendances],
                "count": len(attendances)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching attendance: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TBT TOPIC LIBRARY
# ============================================================================

@tbt_bp.route('/api/tbt/topics', methods=['GET'])
def list_tbt_topics():
    """List all TBT topics (global + company-specific)"""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            
            # Get global topics + company topics
            query = session.query(TBTTopic).filter(
                (TBTTopic.company_id == None) | 
                (TBTTopic.company_id == user.company_id)
            ).filter(TBTTopic.is_active == True)
            
            # Filter by category if provided
            if request.args.get('category'):
                query = query.filter(TBTTopic.category == request.args['category'])
            
            topics = query.order_by(TBTTopic.usage_count.desc()).all()
            
            return jsonify({
                "success": True,
                "topics": [t.to_dict() for t in topics],
                "count": len(topics)
            }), 200
            
    except Exception as e:
        logger.error(f"Error listing topics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/topics', methods=['POST'])
def create_tbt_topic():
    """
    Create custom TBT topic
    
    Body:
    {
        "topic_name": "Concrete Pouring Safety",
        "category": "Activity-Specific",
        "description": "Safety briefing for concrete pouring",
        "key_points_template": ["Check formwork", "Verify pump"],
        "hazards_template": ["Falls", "Concrete burns"],
        "ppe_template": ["Helmet", "Boots", "Gloves"]
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            
            topic = TBTTopic(
                company_id=user.company_id,
                topic_name=data["topic_name"],
                category=data["category"],
                description=data.get("description"),
                key_points_template=json.dumps(data.get("key_points_template", [])),
                hazards_template=json.dumps(data.get("hazards_template", [])),
                ppe_template=json.dumps(data.get("ppe_template", []))
            )
            
            session.add(topic)
            
            logger.info(f"TBT topic created: {topic.topic_name}")
            
            return jsonify({
                "success": True,
                "topic": topic.to_dict()
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating topic: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# REPORTING & ANALYTICS
# ============================================================================

@tbt_bp.route('/api/tbt/dashboard', methods=['GET'])
def tbt_dashboard():
    """
    Get TBT compliance dashboard data
    
    Query params:
    - project_id (required)
    - date_from (optional, default: start of month)
    - date_to (optional, default: today)
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id')
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        # Date range
        date_from = request.args.get('date_from')
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        else:
            date_from = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        
        date_to = request.args.get('date_to')
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        else:
            date_to = datetime.utcnow()
        
        with session_scope() as session:
            # Verify access
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "No access"}), 403
            
            # Get sessions in date range
            sessions = session.query(TBTSession).filter(
                TBTSession.project_id == project_id,
                TBTSession.session_date >= date_from,
                TBTSession.session_date <= date_to
            ).all()
            
            # Calculate stats
            total_sessions = len(sessions)
            total_attendance = sum(len(s.attendances) for s in sessions)
            avg_attendance = total_attendance / total_sessions if total_sessions > 0 else 0
            
            # Top topics
            topic_counts = {}
            for s in sessions:
                topic_counts[s.topic] = topic_counts.get(s.topic, 0) + 1
            
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Activity breakdown
            activity_counts = {}
            for s in sessions:
                activity_counts[s.activity] = activity_counts.get(s.activity, 0) + 1
            
            # Recent sessions
            recent_sessions = sorted(sessions, key=lambda x: x.session_date, reverse=True)[:5]
            
            return jsonify({
                "success": True,
                "stats": {
                    "totalSessions": total_sessions,
                    "totalAttendance": total_attendance,
                    "avgAttendancePerSession": round(avg_attendance, 1),
                    "dateFrom": date_from.isoformat(),
                    "dateTo": date_to.isoformat()
                },
                "topTopics": [{"topic": t[0], "count": t[1]} for t in top_topics],
                "activityBreakdown": [{"activity": k, "count": v} for k, v in activity_counts.items()],
                "recentSessions": [s.to_dict() for s in recent_sessions]
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tbt_bp.route('/api/tbt/reports/monthly', methods=['GET'])
def monthly_tbt_report():
    """
    Generate monthly TBT compliance report
    
    Query params:
    - project_id (required)
    - month (required, format: YYYY-MM)
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id')
        month_str = request.args.get('month')
        
        if not project_id or not month_str:
            return jsonify({"error": "project_id and month are required"}), 400
        
        # Parse month
        year, month = map(int, month_str.split('-'))
        date_from = datetime(year, month, 1)
        
        # Last day of month
        if month == 12:
            date_to = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            date_to = datetime(year, month + 1, 1) - timedelta(days=1)
        
        with session_scope() as session:
            # Get sessions
            sessions = session.query(TBTSession).filter(
                TBTSession.project_id == project_id,
                TBTSession.session_date >= date_from,
                TBTSession.session_date <= date_to
            ).all()
            
            # Calculate compliance
            working_days = (date_to - date_from).days + 1
            days_with_tbt = len(set(s.session_date.date() for s in sessions))
            compliance_rate = (days_with_tbt / working_days) * 100 if working_days > 0 else 0
            
            # Conductor stats
            conductor_stats = {}
            for s in sessions:
                conductor_stats[s.conductor_name] = conductor_stats.get(s.conductor_name, 0) + 1
            
            top_conductors = sorted(conductor_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return jsonify({
                "success": True,
                "report": {
                    "month": month_str,
                    "totalSessions": len(sessions),
                    "totalAttendance": sum(len(s.attendances) for s in sessions),
                    "workingDays": working_days,
                    "daysWithTBT": days_with_tbt,
                    "complianceRate": round(compliance_rate, 1),
                    "topConductors": [{"name": c[0], "sessions": c[1]} for c in top_conductors]
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": str(e)}), 500
