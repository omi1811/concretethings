"""
Concrete NC (Non-Conformance) API endpoints for ConcreteTHings.
Handles NC raising, contractor response, verification, transfer, and scoring.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from contextlib import contextmanager
import os
from werkzeug.utils import secure_filename
import json

from .models import User, Company, Project, RMCVendor
from .concrete_nc_models import (
    ConcreteNCTag, ConcreteNCIssue, ConcreteNCNotification, 
    ConcreteNCScoreReport, NCIssueSeverity, NCIssueStatus
)
from .db import SessionLocal
from .notifications import send_whatsapp_alert
from .email_notifications import send_email
from .module_access import require_module

concrete_nc_bp = Blueprint('concrete_nc', __name__, url_prefix='/api/concrete/nc')

UPLOAD_FOLDER = 'uploads/nc_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_nc_notification(nc_issue, event_type, recipient_user_id, session):
    """
    Send multi-channel notification for NC events.
    
    Args:
        nc_issue: ConcreteNCIssue instance
        event_type: Type of event (raised, acknowledged, responded, resolved, verified, closed, transferred, rejected)
        recipient_user_id: User ID to send notification to
        session: Database session
    """
    try:
        user = session.query(User).filter_by(id=recipient_user_id).first()
        if not user:
            return
        
        # Create notification message based on event type
        messages = {
            'raised': f'New NC raised: {nc_issue.nc_number} - {nc_issue.title}',
            'acknowledged': f'NC acknowledged: {nc_issue.nc_number}',
            'responded': f'Contractor responded to NC: {nc_issue.nc_number}',
            'resolved': f'NC marked as resolved: {nc_issue.nc_number}',
            'verified': f'NC verification completed: {nc_issue.nc_number}',
            'closed': f'NC closed: {nc_issue.nc_number}',
            'transferred': f'NC transferred to you: {nc_issue.nc_number}',
            'rejected': f'NC rejected: {nc_issue.nc_number}'
        }
        
        message = messages.get(event_type, f'NC Update: {nc_issue.nc_number}')
        
        # Send WhatsApp if phone number available
        whatsapp_sent = False
        if user.phone:
            try:
                send_whatsapp_alert(user.phone, message)
                whatsapp_sent = True
            except:
                pass
        
        # Send Email if email available
        email_sent = False
        if user.email:
            try:
                send_email(user.email, f'NC Update: {nc_issue.nc_number}', message)
                email_sent = True
            except:
                pass
        
        # Log notification
        notification = ConcreteNCNotification(
            issue_id=nc_issue.id,
            recipient_user_id=recipient_user_id,
            notification_type=event_type,
            channel='whatsapp' if whatsapp_sent else ('email' if email_sent else 'in_app'),
            sent_at=datetime.utcnow(),
            delivered=whatsapp_sent or email_sent
        )
        session.add(notification)
        
    except Exception as e:
        print(f"Notification error: {str(e)}")

@concrete_nc_bp.route('/tags', methods=['GET'])
@jwt_required()
@require_module("concrete_nc")
def get_tags():
    """Get all NC tags in hierarchical structure."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Get all tags for the company
            tags = session.query(ConcreteNCTag).filter_by(
                company_id=user.company_id,
                is_active=True
            ).order_by(ConcreteNCTag.level, ConcreteNCTag.display_order).all()
            
            return jsonify({'tags': [tag.to_dict() for tag in tags]}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/tags', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def create_tag():
    """Create a new NC tag (Admin/System Admin only)."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user or user.role not in ['System Admin', 'Admin']:
                return jsonify({'error': 'Unauthorized'}), 403
            
            data = request.json
            
            # Validate required fields
            if not data.get('name') or not data.get('level'):
                return jsonify({'error': 'Name and level are required'}), 400
            
            # Validate level
            level = int(data['level'])
            if level < 1 or level > 4:
                return jsonify({'error': 'Level must be between 1 and 4'}), 400
            
            # If parent_tag_id provided, validate it exists and is correct level
            parent_tag_id = data.get('parent_tag_id')
            if parent_tag_id:
                parent = session.query(ConcreteNCTag).filter_by(id=parent_tag_id).first()
                if not parent:
                    return jsonify({'error': 'Parent tag not found'}), 404
                if parent.level != level - 1:
                    return jsonify({'error': 'Parent tag must be one level above'}), 400
            
            tag = ConcreteNCTag(
                company_id=user.company_id,
                name=data['name'],
                level=level,
                parent_tag_id=parent_tag_id,
                color_code=data.get('color_code', '#666666'),
                description=data.get('description'),
                display_order=data.get('display_order', 0)
            )
            
            session.add(tag)
            session.flush()
            
            return jsonify({'message': 'Tag created successfully', 'tag': tag.to_dict()}), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def raise_nc():
    """Raise a new NC issue with photo uploads."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Handle multipart form data
            data = request.form
            files = request.files
            
            # Validate required fields
            if not data.get('project_id') or not data.get('title') or not data.get('severity'):
                return jsonify({'error': 'project_id, title, and severity are required'}), 400
            
            project = session.query(Project).filter_by(id=data['project_id']).first()
            if not project or project.company_id != user.company_id:
                return jsonify({'error': 'Project not found'}), 404
            
            # Validate contractor if provided
            contractor_id = data.get('contractor_id')
            if contractor_id:
                contractor = session.query(RMCVendor).filter_by(id=contractor_id).first()
                if not contractor:
                    return jsonify({'error': 'Contractor not found'}), 404
            
            # Handle photo uploads
            photo_urls = []
            if 'photos' in files:
                photo_files = files.getlist('photos')
                for photo in photo_files:
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        photo.save(filepath)
                        photo_urls.append(filepath)
            
            # Generate NC number: NC-PROJ-YYYY-NNNN
            year = datetime.utcnow().year
            count = session.query(func.count(ConcreteNCIssue.id)).filter(
                ConcreteNCIssue.project_id == data['project_id'],
                func.strftime('%Y', ConcreteNCIssue.created_at) == str(year)
            ).scalar()
            nc_number = f"NC-{project.project_id}-{year}-{str(count + 1).zfill(4)}"
            
            # Parse tag_ids if provided as JSON string
            tag_ids = []
            if data.get('tag_ids'):
                try:
                    tag_ids = json.loads(data['tag_ids'])
                except:
                    pass
            
            # Calculate severity score
            severity_scores = {
                'HIGH': 1.0,
                'MODERATE': 0.5,
                'LOW': 0.25
            }
            severity = data['severity'].upper()
            severity_score = severity_scores.get(severity, 0.25)
            
            # Create NC issue
            nc_issue = ConcreteNCIssue(
                company_id=user.company_id,
                project_id=data['project_id'],
                nc_number=nc_number,
                title=data['title'],
                description=data.get('description'),
                photo_urls=photo_urls,
                location_text=data.get('location_text'),
                location_latitude=float(data['location_latitude']) if data.get('location_latitude') else None,
                location_longitude=float(data['location_longitude']) if data.get('location_longitude') else None,
                tag_ids=tag_ids,
                severity=severity,
                severity_score=severity_score,
                raised_by_user_id=user_id,
                contractor_id=contractor_id,
                oversight_engineer_id=data.get('oversight_engineer_id'),
                status='raised',
                raised_at=datetime.utcnow(),
                score_month=datetime.utcnow().strftime('%Y-%m'),
                score_year=datetime.utcnow().year,
                score_week=datetime.utcnow().strftime('%Y-W%U')
            )
            
            session.add(nc_issue)
            session.flush()
            
            # Send notifications to contractor and oversight engineer
            if contractor_id:
                # Get contractor supervisor (assumed to be in vendor record)
                send_nc_notification(nc_issue, 'raised', contractor_id, session)
            
            if data.get('oversight_engineer_id'):
                send_nc_notification(nc_issue, 'raised', data['oversight_engineer_id'], session)
            
            return jsonify({
                'message': 'NC raised successfully',
                'nc': nc_issue.to_dict()
            }), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/', methods=['GET'])
@jwt_required()
@require_module("concrete_nc")
def list_ncs():
    """List NC issues with filters."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Base query
            query = session.query(ConcreteNCIssue).filter_by(company_id=user.company_id)
            
            # Apply filters
            project_id = request.args.get('project_id')
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            contractor_id = request.args.get('contractor_id')
            if contractor_id:
                query = query.filter_by(contractor_id=contractor_id)
            
            status = request.args.get('status')
            if status:
                query = query.filter_by(status=status)
            
            severity = request.args.get('severity')
            if severity:
                query = query.filter_by(severity=severity.upper())
            
            # Date range filters
            start_date = request.args.get('start_date')
            if start_date:
                query = query.filter(ConcreteNCIssue.raised_at >= datetime.fromisoformat(start_date))
            
            end_date = request.args.get('end_date')
            if end_date:
                query = query.filter(ConcreteNCIssue.raised_at <= datetime.fromisoformat(end_date))
            
            # Pagination
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # Order by most recent
            query = query.order_by(desc(ConcreteNCIssue.created_at))
            
            # Execute query with pagination
            total = query.count()
            ncs = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return jsonify({
                'ncs': [nc.to_dict() for nc in ncs],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>', methods=['GET'])
@jwt_required()
@require_module("concrete_nc")
def get_nc(nc_id):
    """Get NC issue details."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            return jsonify({'nc': nc.to_dict()}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/acknowledge', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def acknowledge_nc(nc_id):
    """Contractor acknowledges NC."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status != 'raised':
                return jsonify({'error': 'NC can only be acknowledged when in raised status'}), 400
            
            data = request.json or {}
            
            nc.status = 'acknowledged'
            nc.acknowledged_at = datetime.utcnow()
            nc.acknowledged_by_user_id = user_id
            nc.contractor_remarks = data.get('remarks')
            
            session.flush()
            
            # Notify raiser and oversight engineer
            send_nc_notification(nc, 'acknowledged', nc.raised_by_user_id, session)
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'acknowledged', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'NC acknowledged successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/respond', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def respond_nc(nc_id):
    """Contractor responds to NC with action plan."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status not in ['raised', 'acknowledged']:
                return jsonify({'error': 'Cannot respond to NC in current status'}), 400
            
            data = request.json
            
            if not data.get('response'):
                return jsonify({'error': 'Response is required'}), 400
            
            nc.status = 'in_progress'
            nc.contractor_response = data['response']
            nc.proposed_deadline = datetime.fromisoformat(data['proposed_deadline']) if data.get('proposed_deadline') else None
            nc.responded_at = datetime.utcnow()
            
            session.flush()
            
            # Notify raiser and oversight engineer
            send_nc_notification(nc, 'responded', nc.raised_by_user_id, session)
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'responded', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'Response submitted successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/resolve', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def resolve_nc(nc_id):
    """Contractor marks NC as resolved with resolution photos."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status != 'in_progress':
                return jsonify({'error': 'NC must be in progress to resolve'}), 400
            
            # Handle resolution photo uploads
            files = request.files
            resolution_photos = []
            if 'resolution_photos' in files:
                photo_files = files.getlist('resolution_photos')
                for photo in photo_files:
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        filename = f"resolution_{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        photo.save(filepath)
                        resolution_photos.append(filepath)
            
            data = request.form
            
            nc.status = 'resolved'
            nc.resolution_description = data.get('resolution_description')
            nc.resolution_photo_urls = resolution_photos
            nc.resolved_at = datetime.utcnow()
            nc.resolved_by_user_id = user_id
            
            session.flush()
            
            # Notify raiser and oversight engineer for verification
            send_nc_notification(nc, 'resolved', nc.raised_by_user_id, session)
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'resolved', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'NC marked as resolved, awaiting verification',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/verify', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def verify_nc(nc_id):
    """Raiser/QAQC verifies NC resolution."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status != 'resolved':
                return jsonify({'error': 'NC must be resolved before verification'}), 400
            
            # Only raiser or oversight engineer can verify
            if user_id not in [nc.raised_by_user_id, nc.oversight_engineer_id]:
                return jsonify({'error': 'Only raiser or oversight engineer can verify'}), 403
            
            data = request.json or {}
            
            nc.status = 'verified'
            nc.verified_at = datetime.utcnow()
            nc.verified_by_user_id = user_id
            nc.verification_remarks = data.get('remarks')
            
            session.flush()
            
            # Notify contractor
            if nc.contractor_id:
                send_nc_notification(nc, 'verified', nc.contractor_id, session)
            
            return jsonify({
                'message': 'NC verified successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/close', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def close_nc(nc_id):
    """Close verified NC."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status != 'verified':
                return jsonify({'error': 'NC must be verified before closing'}), 400
            
            data = request.json or {}
            
            nc.status = 'closed'
            nc.closed_at = datetime.utcnow()
            nc.closed_by_user_id = user_id
            nc.closure_remarks = data.get('remarks')
            
            # Calculate resolution time
            if nc.resolved_at:
                resolution_time = (nc.closed_at - nc.raised_at).days
                nc.actual_resolution_days = resolution_time
            
            # Reset severity score since issue is closed
            nc.severity_score = 0.0
            
            session.flush()
            
            # Notify all stakeholders
            if nc.contractor_id:
                send_nc_notification(nc, 'closed', nc.contractor_id, session)
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'closed', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'NC closed successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/reject', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def reject_nc(nc_id):
    """Contractor rejects NC."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            if nc.status not in ['raised', 'acknowledged']:
                return jsonify({'error': 'Cannot reject NC in current status'}), 400
            
            data = request.json
            
            if not data.get('rejection_reason'):
                return jsonify({'error': 'Rejection reason is required'}), 400
            
            nc.status = 'rejected'
            nc.rejection_reason = data['rejection_reason']
            nc.rejected_at = datetime.utcnow()
            nc.rejected_by_user_id = user_id
            
            session.flush()
            
            # Notify raiser and oversight engineer
            send_nc_notification(nc, 'rejected', nc.raised_by_user_id, session)
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'rejected', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'NC rejected',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/transfer', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def transfer_nc(nc_id):
    """Transfer NC to different contractor."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            data = request.json
            
            if not data.get('new_contractor_id'):
                return jsonify({'error': 'new_contractor_id is required'}), 400
            
            # Validate new contractor
            new_contractor = session.query(RMCVendor).filter_by(id=data['new_contractor_id']).first()
            if not new_contractor:
                return jsonify({'error': 'New contractor not found'}), 404
            
            # Log transfer in history
            transfer_entry = {
                'from_contractor_id': nc.contractor_id,
                'to_contractor_id': data['new_contractor_id'],
                'transferred_at': datetime.utcnow().isoformat(),
                'transferred_by_user_id': user_id,
                'reason': data.get('reason')
            }
            
            transfer_history = nc.transfer_history or []
            transfer_history.append(transfer_entry)
            nc.transfer_history = transfer_history
            
            # Update contractor
            old_contractor_id = nc.contractor_id
            nc.contractor_id = data['new_contractor_id']
            nc.status = 'transferred'
            
            session.flush()
            
            # Notify both contractors
            if old_contractor_id:
                send_nc_notification(nc, 'transferred', old_contractor_id, session)
            send_nc_notification(nc, 'transferred', data['new_contractor_id'], session)
            
            # Notify oversight engineer
            if nc.oversight_engineer_id:
                send_nc_notification(nc, 'transferred', nc.oversight_engineer_id, session)
            
            return jsonify({
                'message': 'NC transferred successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_module("concrete_nc")
def get_dashboard():
    """Get NC dashboard statistics."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            project_id = request.args.get('project_id')
            
            # Base query
            base_query = session.query(ConcreteNCIssue).filter_by(company_id=user.company_id)
            if project_id:
                base_query = base_query.filter_by(project_id=project_id)
            
            # Total counts by status
            status_counts = {}
            for status in ['raised', 'acknowledged', 'in_progress', 'resolved', 'verified', 'closed', 'rejected', 'transferred']:
                count = base_query.filter_by(status=status).count()
                status_counts[status] = count
            
            # Counts by severity
            severity_counts = {}
            for severity in ['HIGH', 'MODERATE', 'LOW']:
                count = base_query.filter_by(severity=severity).count()
                severity_counts[severity] = count
            
            # Open issues (not closed)
            open_count = base_query.filter(
                ConcreteNCIssue.status.in_(['raised', 'acknowledged', 'in_progress', 'resolved', 'verified', 'transferred'])
            ).count()
            
            # Overdue issues (past proposed deadline and not closed)
            overdue_count = base_query.filter(
                and_(
                    ConcreteNCIssue.proposed_deadline < datetime.utcnow(),
                    ConcreteNCIssue.status != 'closed'
                )
            ).count()
            
            # Average resolution time for closed issues
            closed_issues = base_query.filter_by(status='closed').all()
            avg_resolution_days = 0
            if closed_issues:
                total_days = sum([nc.actual_resolution_days or 0 for nc in closed_issues])
                avg_resolution_days = total_days / len(closed_issues)
            
            # Calculate weighted score based on severity
            all_issues = base_query.all()
            total_count = len(all_issues)
            closed_count = status_counts['closed']
            
            # Severity weights: HIGH=1.0, MODERATE=0.5, LOW=0.25
            severity_map = {'HIGH': 1.0, 'MODERATE': 0.5, 'LOW': 0.25}
            
            total_severity_points = sum(
                severity_map.get(nc.severity, 0.5) for nc in all_issues
            )
            
            closed_severity_points = sum(
                severity_map.get(nc.severity, 0.5) 
                for nc in all_issues if nc.status == 'closed'
            )
            
            # Score calculation: (closed severity points / total severity points) * 10
            score_out_of_10 = (closed_severity_points / total_severity_points * 10) if total_severity_points > 0 else 10.0
            
            # Count open issues by severity
            open_high = len([nc for nc in all_issues if nc.severity == 'HIGH' and nc.status != 'closed'])
            open_moderate = len([nc for nc in all_issues if nc.severity == 'MODERATE' and nc.status != 'closed'])
            open_low = len([nc for nc in all_issues if nc.severity == 'LOW' and nc.status != 'closed'])
            
            # Calculate performance grade
            if score_out_of_10 >= 9.0:
                grade = 'A'
            elif score_out_of_10 >= 7.0:
                grade = 'B'
            elif score_out_of_10 >= 5.0:
                grade = 'C'
            elif score_out_of_10 >= 3.0:
                grade = 'D'
            else:
                grade = 'F'
            
            return jsonify({
                'status_counts': status_counts,
                'severity_counts': severity_counts,
                'open_by_severity': {
                    'HIGH': open_high,
                    'MODERATE': open_moderate,
                    'LOW': open_low
                },
                'total': total_count,
                'open': open_count,
                'closed': closed_count,
                'overdue': overdue_count,
                'avg_resolution_days': round(avg_resolution_days, 1),
                'score': round(score_out_of_10, 1),
                'total_severity_points': round(total_severity_points, 2),
                'closed_severity_points': round(closed_severity_points, 2),
                'performance_grade': grade
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/reports/<report_type>', methods=['GET'])
@jwt_required()
@require_module("concrete_nc")
def generate_report(report_type):
    """
    Generate NC score reports.
    report_type: 'monthly' or 'weekly'
    """
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            project_id = request.args.get('project_id')
            contractor_id = request.args.get('contractor_id')
            
            if not project_id or not contractor_id:
                return jsonify({'error': 'project_id and contractor_id are required'}), 400
            
            # Determine period
            if report_type == 'monthly':
                period = request.args.get('period', datetime.utcnow().strftime('%Y-%m'))
                period_filter = ConcreteNCIssue.score_month == period
            elif report_type == 'weekly':
                period = request.args.get('period', datetime.utcnow().strftime('%Y-W%U'))
                period_filter = ConcreteNCIssue.score_week == period
            else:
                return jsonify({'error': 'Invalid report_type. Use monthly or weekly'}), 400
            
            # Get all issues for this contractor and period
            issues = session.query(ConcreteNCIssue).filter(
                and_(
                    ConcreteNCIssue.company_id == user.company_id,
                    ConcreteNCIssue.project_id == project_id,
                    ConcreteNCIssue.contractor_id == contractor_id,
                    period_filter
                )
            ).all()
            
            # Calculate scores with severity weighting
            severity_map = {'HIGH': 1.0, 'MODERATE': 0.5, 'LOW': 0.25}
            
            high_count = sum(1 for nc in issues if nc.severity == 'HIGH' and nc.status != 'closed')
            moderate_count = sum(1 for nc in issues if nc.severity == 'MODERATE' and nc.status != 'closed')
            low_count = sum(1 for nc in issues if nc.severity == 'LOW' and nc.status != 'closed')
            
            closed_count = sum(1 for nc in issues if nc.status == 'closed')
            total_count = len(issues)
            
            # Calculate weighted score
            total_severity_points = sum(severity_map.get(nc.severity, 0.5) for nc in issues)
            closed_severity_points = sum(
                severity_map.get(nc.severity, 0.5) 
                for nc in issues if nc.status == 'closed'
            )
            
            total_score = (closed_severity_points / total_severity_points * 10) if total_severity_points > 0 else 10.0
            
            # Calculate closure rate
            closure_rate = (closed_count / total_count * 100) if total_count > 0 else 0
            
            # Calculate avg resolution time
            closed_issues = [nc for nc in issues if nc.status == 'closed' and nc.actual_resolution_days]
            avg_resolution_days = sum(nc.actual_resolution_days for nc in closed_issues) / len(closed_issues) if closed_issues else 0
            
            # Determine performance grade
            if total_score >= 9.0:
                grade = 'A'
            elif total_score >= 7.0:
                grade = 'B'
            elif total_score >= 5.0:
                grade = 'C'
            elif total_score >= 3.0:
                grade = 'D'
            else:
                grade = 'F'
            
            # Check if report already exists
            existing_report = session.query(ConcreteNCScoreReport).filter(
                and_(
                    ConcreteNCScoreReport.company_id == user.company_id,
                    ConcreteNCScoreReport.project_id == project_id,
                    ConcreteNCScoreReport.contractor_id == contractor_id,
                    ConcreteNCScoreReport.report_type == report_type,
                    ConcreteNCScoreReport.period == period
                )
            ).first()
            
            if existing_report:
                # Update existing report
                existing_report.high_severity_count = high_count
                existing_report.moderate_severity_count = moderate_count
                existing_report.low_severity_count = low_count
                existing_report.total_issues_count = total_count
                existing_report.closed_issues_count = closed_count
                existing_report.open_issues_count = total_count - closed_count
                existing_report.total_score = total_score
                existing_report.closure_rate = closure_rate
                existing_report.avg_resolution_days = avg_resolution_days
                existing_report.performance_grade = grade
                existing_report.generated_at = datetime.utcnow()
                
                report = existing_report
            else:
                # Create new report
                report = ConcreteNCScoreReport(
                    company_id=user.company_id,
                    project_id=project_id,
                    contractor_id=contractor_id,
                    report_type=report_type,
                    period=period,
                    high_severity_count=high_count,
                    moderate_severity_count=moderate_count,
                    low_severity_count=low_count,
                    total_issues_count=total_count,
                    closed_issues_count=closed_count,
                    open_issues_count=total_count - closed_count,
                    total_score=total_score,
                    closure_rate=closure_rate,
                    avg_resolution_days=avg_resolution_days,
                    performance_grade=grade,
                    generated_by_user_id=user_id,
                    generated_at=datetime.utcnow()
                )
                session.add(report)
            
            session.flush()
            
            return jsonify({
                'report': report.to_dict(),
                'issues': [nc.to_dict() for nc in issues]
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@concrete_nc_bp.route('/<int:nc_id>/photos', methods=['POST'])
@jwt_required()
@require_module("concrete_nc")
def add_photos(nc_id):
    """Add additional photos to existing NC."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            nc = session.query(ConcreteNCIssue).filter_by(
                id=nc_id,
                company_id=user.company_id
            ).first()
            
            if not nc:
                return jsonify({'error': 'NC not found'}), 404
            
            # Handle photo uploads
            files = request.files
            new_photos = []
            if 'photos' in files:
                photo_files = files.getlist('photos')
                for photo in photo_files:
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        photo.save(filepath)
                        new_photos.append(filepath)
            
            if not new_photos:
                return jsonify({'error': 'No valid photos uploaded'}), 400
            
            # Append to existing photos
            current_photos = nc.photo_urls or []
            nc.photo_urls = current_photos + new_photos
            
            session.flush()
            
            return jsonify({
                'message': f'{len(new_photos)} photos added successfully',
                'nc': nc.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
