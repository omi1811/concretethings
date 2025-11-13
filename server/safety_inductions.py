"""
Safety Induction API

Worker onboarding and induction management with:
- Aadhar card verification
- Safety video playback tracking
- Quiz assessment (10 questions, passing score 70%)
- Terms & conditions acceptance
- Digital signatures (worker + safety officer)
- Certificate issuance

Compliance: ISO 45001:2018 Clause 7.2 (Competence)

Endpoints:
- POST   /api/safety-inductions                    - Create new induction
- GET    /api/safety-inductions                    - List all inductions
- GET    /api/safety-inductions/:id                - Get induction details
- POST   /api/safety-inductions/:id/video-progress - Update video watch progress
- POST   /api/safety-inductions/:id/quiz           - Submit quiz answers
- POST   /api/safety-inductions/:id/aadhar         - Upload Aadhar photos
- POST   /api/safety-inductions/:id/terms          - Accept terms & conditions
- POST   /api/safety-inductions/:id/sign           - Add digital signatures
- POST   /api/safety-inductions/:id/complete       - Complete induction & issue certificate
- GET    /api/safety-inductions/:id/certificate    - Download certificate PDF
- GET    /api/safety-inductions/worker/:worker_id  - Worker's induction history
- GET    /api/safety-inductions/expiring           - Inductions expiring in 30 days
- GET    /api/induction-topics                     - Get available induction topics
- POST   /api/induction-topics                     - Create custom topic (Admin only)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
import traceback
import os
from werkzeug.utils import secure_filename

try:
    from .db import session_scope
    from .safety_induction_models import SafetyInduction, InductionTopic, STANDARD_INDUCTION_TOPICS
    from .safety_models import Worker
    from .models import User, Project, Company
except ImportError:
    from db import session_scope
    from safety_induction_models import SafetyInduction, InductionTopic, STANDARD_INDUCTION_TOPICS
    from safety_models import Worker
    from models import User, Project, Company


# Create Blueprint
safety_induction_bp = Blueprint('safety_induction', __name__, url_prefix='/api/safety-inductions')
induction_topics_bp = Blueprint('induction_topics', __name__, url_prefix='/api/induction-topics')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Extract user_id from JWT identity."""
    identity = get_jwt_identity()
    return identity.get("user_id") if isinstance(identity, dict) else int(identity)


def generate_induction_number(project_id: int) -> str:
    """Generate unique induction number: IND-{project}-{year}-{seq}"""
    year = datetime.now().year
    with session_scope() as session:
        # Count existing inductions for this project this year
        count = session.query(SafetyInduction).filter(
            SafetyInduction.project_id == project_id,
            SafetyInduction.induction_number.like(f'IND-{project_id}-{year}-%')
        ).count()
        seq = count + 1
        return f'IND-{project_id}-{year}-{seq:04d}'


def generate_certificate_number(worker_id: int, induction_id: int) -> str:
    """Generate certificate number: IND-CERT-{worker_id}-{induction_id}-{date}"""
    date_str = datetime.now().strftime('%Y%m%d')
    return f'IND-CERT-{worker_id}-{induction_id}-{date_str}'


# ============================================================================
# DECORATORS
# ============================================================================

def safety_officer_required(f):
    """Decorator to check if user is Safety Officer or Admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user or user.role not in ['admin', 'safety_officer']:
                return jsonify({"error": "Access denied. Safety Officer role required."}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# INDUCTION ENDPOINTS
# ============================================================================

@safety_induction_bp.route('', methods=['POST'])
@jwt_required()
@safety_officer_required
def create_induction():
    """
    Create new safety induction session.
    
    Request Body:
    {
        "project_id": 1,
        "worker_id": 123,
        "induction_topics": [1, 2, 3, 4, 5],  // Topic IDs
        "video_url": "https://youtube.com/watch?v=...",
        "video_duration_seconds": 1800,
        "is_reinduction": false,
        "reinduction_reason": "Annual renewal"
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['project_id', 'worker_id', 'induction_topics']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        with session_scope() as session:
            # Verify worker exists
            worker = session.query(Worker).filter_by(
                id=data['worker_id'],
                is_deleted=False
            ).first()
            if not worker:
                return jsonify({"error": "Worker not found"}), 404
            
            # Get company_id from worker
            company_id = worker.company_id
            
            # Generate induction number
            induction_number = generate_induction_number(data['project_id'])
            
            # Fetch topic details
            topic_ids = data['induction_topics']
            topics = session.query(InductionTopic).filter(
                InductionTopic.id.in_(topic_ids),
                InductionTopic.is_active == True
            ).all()
            
            topic_details = [{'id': t.id, 'name': t.topic_name, 'category': t.topic_category} for t in topics]
            
            # Calculate validity (1 year)
            valid_from = datetime.now().date()
            valid_until = valid_from + timedelta(days=365)
            
            # Create induction
            induction = SafetyInduction(
                company_id=company_id,
                project_id=data['project_id'],
                worker_id=data['worker_id'],
                conducted_by=user_id,
                induction_number=induction_number,
                induction_date=datetime.now(),
                induction_topics=topic_details,
                video_url=data.get('video_url'),
                video_duration_seconds=data.get('video_duration_seconds', 1800),  # Default 30 min
                is_reinduction=data.get('is_reinduction', False),
                reinduction_reason=data.get('reinduction_reason'),
                previous_induction_id=data.get('previous_induction_id'),
                terms_version='v1.0',  # Current T&C version
                quiz_passing_score=7,  # Out of 10
                valid_from=valid_from,
                valid_until=valid_until,
                status='in_progress',
                created_by=user_id,
                updated_by=user_id
            )
            
            session.add(induction)
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Safety induction created successfully",
                "induction": induction.to_dict()
            }), 201
    
    except Exception as e:
        print(f"Error creating induction: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create induction: {str(e)}"}), 500


@safety_induction_bp.route('', methods=['GET'])
@jwt_required()
def get_inductions():
    """
    Get list of safety inductions with filters.
    
    Query Params:
    - project_id: Filter by project
    - worker_id: Filter by worker
    - status: pending, in_progress, quiz_pending, completed, expired, failed
    - expiring_soon: true (inductions expiring in 30 days)
    """
    try:
        project_id = request.args.get('project_id', type=int)
        worker_id = request.args.get('worker_id', type=int)
        status = request.args.get('status')
        expiring_soon = request.args.get('expiring_soon', 'false').lower() == 'true'
        
        with session_scope() as session:
            query = session.query(SafetyInduction).filter_by(is_deleted=False)
            
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            if worker_id:
                query = query.filter_by(worker_id=worker_id)
            
            if status:
                query = query.filter_by(status=status)
            
            if expiring_soon:
                expiry_threshold = datetime.now().date() + timedelta(days=30)
                query = query.filter(
                    SafetyInduction.valid_until <= expiry_threshold,
                    SafetyInduction.is_expired == False
                )
            
            inductions = query.order_by(SafetyInduction.induction_date.desc()).all()
            
            return jsonify({
                "success": True,
                "count": len(inductions),
                "inductions": [ind.to_dict() for ind in inductions]
            }), 200
    
    except Exception as e:
        print(f"Error fetching inductions: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch inductions: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>', methods=['GET'])
@jwt_required()
def get_induction(induction_id):
    """Get details of a specific induction."""
    try:
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            return jsonify({
                "success": True,
                "induction": induction.to_dict()
            }), 200
    
    except Exception as e:
        print(f"Error fetching induction: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch induction: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/video-progress', methods=['POST'])
@jwt_required()
def update_video_progress(induction_id):
    """
    Update video watch progress.
    
    Request Body:
    {
        "watched_seconds": 900,  // How many seconds watched
        "completed": false       // true if video fully watched
    }
    """
    try:
        data = request.get_json()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Update progress
            induction.video_watched_seconds = data.get('watched_seconds', 0)
            
            if data.get('completed', False):
                induction.video_watched = True
                induction.video_completed_at = datetime.now()
                induction.video_watched_seconds = induction.video_duration_seconds
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Video progress updated",
                "progress": {
                    "watched_seconds": induction.video_watched_seconds,
                    "total_seconds": induction.video_duration_seconds,
                    "percentage": round((induction.video_watched_seconds / induction.video_duration_seconds * 100), 2),
                    "completed": induction.video_watched
                }
            }), 200
    
    except Exception as e:
        print(f"Error updating video progress: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update video progress: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/quiz', methods=['POST'])
@jwt_required()
def submit_quiz(induction_id):
    """
    Submit quiz answers and calculate score.
    
    Request Body:
    {
        "questions": [
            {
                "question_id": 1,
                "question": "What is mandatory PPE?",
                "answer": "Helmet, boots, vest"
            },
            ...10 questions
        ],
        "answers": [
            {"question_id": 1, "answer": "A"},
            {"question_id": 2, "answer": "B"},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Check video watched
            if not induction.video_watched:
                return jsonify({"error": "Please watch the safety video first"}), 400
            
            # Store questions and answers
            induction.quiz_questions = data.get('questions', [])
            induction.quiz_answers = data.get('answers', [])
            induction.quiz_attempts += 1
            induction.quiz_taken = True
            induction.quiz_completed_at = datetime.now()
            
            # Calculate score (simplified - in production, validate against correct answers)
            # Here we assume 'correct_count' is sent from frontend after validation
            score = data.get('score', 0)  # Out of 10
            induction.quiz_score = score
            induction.quiz_passed = score >= induction.quiz_passing_score
            
            # Update status
            if induction.quiz_passed:
                induction.status = 'quiz_completed'
            else:
                if induction.quiz_attempts >= 3:
                    induction.status = 'failed'
                else:
                    induction.status = 'quiz_pending'
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Quiz submitted successfully",
                "quiz": {
                    "score": induction.quiz_score,
                    "passing_score": induction.quiz_passing_score,
                    "passed": induction.quiz_passed,
                    "attempts": induction.quiz_attempts,
                    "attempts_remaining": max(0, 3 - induction.quiz_attempts)
                }
            }), 200
    
    except Exception as e:
        print(f"Error submitting quiz: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to submit quiz: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/aadhar', methods=['POST'])
@jwt_required()
def upload_aadhar(induction_id):
    """
    Upload Aadhar card photos (front + back) and Aadhar number.
    
    Request Body (multipart/form-data):
    - aadhar_number: 12 digits
    - aadhar_front: File
    - aadhar_back: File
    """
    try:
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Get Aadhar number
            aadhar_number = request.form.get('aadhar_number', '').strip()
            if not aadhar_number or len(aadhar_number) != 12:
                return jsonify({"error": "Invalid Aadhar number (must be 12 digits)"}), 400
            
            # Update induction
            induction.aadhar_number = aadhar_number
            
            # Save photos (simplified - in production, upload to S3)
            # Here we just acknowledge the upload
            if 'aadhar_front' in request.files and 'aadhar_back' in request.files:
                # In production: upload to S3 and store paths
                # For now, just mark as uploaded
                pass
            
            # Update worker record with Aadhar details
            worker = induction.worker
            worker.aadhar_number = aadhar_number
            # worker.aadhar_photo_front = front_path
            # worker.aadhar_photo_back = back_path
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Aadhar details uploaded successfully",
                "aadhar": {
                    "number": aadhar_number[-4:],  # Show last 4 digits only
                    "verified": False  # Safety Officer will verify
                }
            }), 200
    
    except Exception as e:
        print(f"Error uploading Aadhar: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to upload Aadhar: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/aadhar/verify', methods=['POST'])
@jwt_required()
@safety_officer_required
def verify_aadhar(induction_id):
    """
    Verify Aadhar card by Safety Officer.
    
    Request Body:
    {
        "verified": true,
        "notes": "Aadhar verified, name matches"
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Update verification
            induction.aadhar_verified = data.get('verified', False)
            induction.aadhar_verified_by = user_id
            induction.aadhar_verified_at = datetime.now()
            induction.aadhar_verification_notes = data.get('notes', '')
            
            # Update worker record
            worker = induction.worker
            worker.aadhar_verified = data.get('verified', False)
            worker.verified_by_id = user_id
            worker.verification_date = datetime.now()
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Aadhar verification updated",
                "aadhar": {
                    "verified": induction.aadhar_verified,
                    "verified_at": induction.aadhar_verified_at.isoformat() if induction.aadhar_verified_at else None
                }
            }), 200
    
    except Exception as e:
        print(f"Error verifying Aadhar: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to verify Aadhar: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/terms', methods=['POST'])
@jwt_required()
def accept_terms(induction_id):
    """
    Accept terms & conditions.
    
    Request Body:
    {
        "accepted": true,
        "ip_address": "192.168.1.100"
    }
    """
    try:
        data = request.get_json()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Check prerequisites
            if not induction.quiz_passed:
                return jsonify({"error": "Please pass the quiz first"}), 400
            
            if not induction.aadhar_verified:
                return jsonify({"error": "Aadhar verification pending"}), 400
            
            # Accept terms
            induction.terms_accepted = data.get('accepted', False)
            induction.terms_accepted_at = datetime.now()
            # induction.terms_pdf_path = generate_terms_pdf()  # TODO
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Terms accepted successfully",
                "terms": {
                    "version": induction.terms_version,
                    "accepted": induction.terms_accepted,
                    "accepted_at": induction.terms_accepted_at.isoformat()
                }
            }), 200
    
    except Exception as e:
        print(f"Error accepting terms: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to accept terms: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/sign', methods=['POST'])
@jwt_required()
def add_signatures(induction_id):
    """
    Add digital signatures (worker + safety officer).
    
    Request Body:
    {
        "worker_signature": "data:image/png;base64,...",
        "worker_ip": "192.168.1.100",
        "safety_officer_signature": "data:image/png;base64,...",
        "witness_name": "John Doe",
        "witness_signature": "data:image/png;base64,..."
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Check prerequisites
            if not induction.terms_accepted:
                return jsonify({"error": "Please accept terms & conditions first"}), 400
            
            # Add worker signature
            if 'worker_signature' in data:
                induction.worker_signature = data['worker_signature']
                induction.worker_signature_ip = data.get('worker_ip', request.remote_addr)
                induction.worker_signed_at = datetime.now()
            
            # Add safety officer signature
            if 'safety_officer_signature' in data:
                induction.safety_officer_signature = data['safety_officer_signature']
                induction.safety_officer_signed_at = datetime.now()
            
            # Add witness signature (optional)
            if 'witness_signature' in data:
                induction.witness_name = data.get('witness_name')
                induction.witness_signature = data['witness_signature']
                induction.witness_signed_at = datetime.now()
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Signatures added successfully",
                "signatures": {
                    "worker": bool(induction.worker_signature),
                    "safety_officer": bool(induction.safety_officer_signature),
                    "witness": induction.witness_name if induction.witness_name else None
                }
            }), 200
    
    except Exception as e:
        print(f"Error adding signatures: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to add signatures: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/complete', methods=['POST'])
@jwt_required()
@safety_officer_required
def complete_induction(induction_id):
    """
    Complete induction and issue certificate.
    
    All prerequisites must be met:
    - Video watched
    - Quiz passed
    - Aadhar verified
    - Terms accepted
    - Signatures collected
    """
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False
            ).first()
            
            if not induction:
                return jsonify({"error": "Induction not found"}), 404
            
            # Validate prerequisites
            errors = []
            if not induction.video_watched:
                errors.append("Video not watched")
            if not induction.quiz_passed:
                errors.append("Quiz not passed")
            if not induction.aadhar_verified:
                errors.append("Aadhar not verified")
            if not induction.terms_accepted:
                errors.append("Terms not accepted")
            if not induction.worker_signature:
                errors.append("Worker signature missing")
            if not induction.safety_officer_signature:
                errors.append("Safety officer signature missing")
            
            if errors:
                return jsonify({
                    "error": "Cannot complete induction. Missing steps:",
                    "missing": errors
                }), 400
            
            # Generate certificate
            certificate_number = generate_certificate_number(induction.worker_id, induction.id)
            
            induction.certificate_issued = True
            induction.certificate_number = certificate_number
            induction.certificate_issued_at = datetime.now()
            # induction.certificate_pdf_path = generate_certificate_pdf(induction)  # TODO
            induction.status = 'completed'
            induction.updated_by = user_id
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Induction completed successfully! Certificate issued.",
                "certificate": {
                    "number": certificate_number,
                    "issued_at": induction.certificate_issued_at.isoformat(),
                    "valid_until": induction.valid_until.isoformat(),
                    "pdf_url": f"/api/safety-inductions/{induction.id}/certificate"
                },
                "induction": induction.to_dict()
            }), 200
    
    except Exception as e:
        print(f"Error completing induction: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to complete induction: {str(e)}"}), 500


@safety_induction_bp.route('/<int:induction_id>/certificate', methods=['GET'])
@jwt_required()
def download_certificate(induction_id):
    """Download induction certificate PDF."""
    try:
        with session_scope() as session:
            induction = session.query(SafetyInduction).filter_by(
                id=induction_id,
                is_deleted=False,
                certificate_issued=True
            ).first()
            
            if not induction:
                return jsonify({"error": "Certificate not found"}), 404
            
            # TODO: Generate/fetch actual PDF
            # For now, return JSON with certificate details
            return jsonify({
                "success": True,
                "certificate": {
                    "number": induction.certificate_number,
                    "worker_name": induction.worker.worker_name,
                    "worker_code": induction.worker.worker_code,
                    "company": induction.worker.worker_company,
                    "issued_date": induction.certificate_issued_at.isoformat(),
                    "valid_from": induction.valid_from.isoformat(),
                    "valid_until": induction.valid_until.isoformat(),
                    "topics_covered": induction.induction_topics,
                    "quiz_score": induction.quiz_score,
                    "conducted_by": induction.conductor.full_name
                }
            }), 200
    
    except Exception as e:
        print(f"Error downloading certificate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to download certificate: {str(e)}"}), 500


@safety_induction_bp.route('/worker/<int:worker_id>', methods=['GET'])
@jwt_required()
def get_worker_induction_history(worker_id):
    """Get all inductions for a worker."""
    try:
        with session_scope() as session:
            inductions = session.query(SafetyInduction).filter_by(
                worker_id=worker_id,
                is_deleted=False
            ).order_by(SafetyInduction.induction_date.desc()).all()
            
            return jsonify({
                "success": True,
                "worker_id": worker_id,
                "count": len(inductions),
                "inductions": [ind.to_dict() for ind in inductions]
            }), 200
    
    except Exception as e:
        print(f"Error fetching worker inductions: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch worker inductions: {str(e)}"}), 500


@safety_induction_bp.route('/expiring', methods=['GET'])
@jwt_required()
def get_expiring_inductions():
    """Get inductions expiring in next 30 days."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            expiry_threshold = datetime.now().date() + timedelta(days=30)
            
            query = session.query(SafetyInduction).filter(
                SafetyInduction.valid_until <= expiry_threshold,
                SafetyInduction.is_expired == False,
                SafetyInduction.is_deleted == False,
                SafetyInduction.status == 'completed'
            )
            
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            inductions = query.order_by(SafetyInduction.valid_until).all()
            
            return jsonify({
                "success": True,
                "count": len(inductions),
                "inductions": [ind.to_dict() for ind in inductions]
            }), 200
    
    except Exception as e:
        print(f"Error fetching expiring inductions: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch expiring inductions: {str(e)}"}), 500


# ============================================================================
# INDUCTION TOPICS ENDPOINTS
# ============================================================================

@induction_topics_bp.route('', methods=['GET'])
@jwt_required()
def get_topics():
    """Get available induction topics."""
    try:
        user_id = get_current_user_id()
        
        with session_scope() as session:
            # Get user's company
            user = session.query(User).filter_by(id=user_id).first()
            company_id = user.company_id if user else None
            
            topics = session.query(InductionTopic).filter_by(
                company_id=company_id,
                is_active=True
            ).order_by(InductionTopic.display_order).all()
            
            return jsonify({
                "success": True,
                "count": len(topics),
                "topics": [topic.to_dict() for topic in topics]
            }), 200
    
    except Exception as e:
        print(f"Error fetching topics: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch topics: {str(e)}"}), 500


@induction_topics_bp.route('', methods=['POST'])
@jwt_required()
@safety_officer_required
def create_topic():
    """Create custom induction topic (Admin/Safety Officer only)."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        required_fields = ['topic_name', 'topic_category']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            
            topic = InductionTopic(
                company_id=user.company_id,
                topic_name=data['topic_name'],
                topic_description=data.get('topic_description'),
                topic_category=data['topic_category'],
                key_points=data.get('key_points', []),
                dos_and_donts=data.get('dos_and_donts', {}),
                reference_standards=data.get('reference_standards', []),
                video_url=data.get('video_url'),
                images=data.get('images', []),
                documents=data.get('documents', []),
                quiz_questions=data.get('quiz_questions', []),
                is_mandatory=data.get('is_mandatory', False),
                display_order=data.get('display_order', 99),
                created_by=user_id
            )
            
            session.add(topic)
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Induction topic created successfully",
                "topic": topic.to_dict()
            }), 201
    
    except Exception as e:
        print(f"Error creating topic: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create topic: {str(e)}"}), 500


# ============================================================================
# SEED FUNCTION (Call this once to populate standard topics)
# ============================================================================

def seed_standard_topics(company_id: int, created_by: int):
    """Seed 18 standard induction topics for a company."""
    with session_scope() as session:
        for topic_data in STANDARD_INDUCTION_TOPICS:
            existing = session.query(InductionTopic).filter_by(
                company_id=company_id,
                topic_name=topic_data['topic_name']
            ).first()
            
            if not existing:
                topic = InductionTopic(
                    company_id=company_id,
                    topic_name=topic_data['topic_name'],
                    topic_category=topic_data['topic_category'],
                    key_points=topic_data['key_points'],
                    is_mandatory=topic_data['is_mandatory'],
                    display_order=topic_data['display_order'],
                    is_active=True,
                    created_by=created_by
                )
                session.add(topic)
        
        session.flush()
        print(f"Seeded {len(STANDARD_INDUCTION_TOPICS)} standard induction topics for company {company_id}")
