"""
Incident Investigation API
Endpoints for incident reporting, investigation, root cause analysis, and regulatory compliance
ISO 45001:2018 Clause 10.2 (Incident Investigation)
OSHA 29 CFR 1904 Compliance
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_, or_
from server.db import session_scope
from server.models import User, Company, Project
from server.safety_models import Worker
from server.incident_investigation_models import IncidentReport, IncidentType, IncidentStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

incident_bp = Blueprint('incidents', __name__)

def get_current_user_id():
    """Extract user ID from JWT token (handles both dict and int)"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('id')
    return identity

def safety_officer_required(f):
    """Decorator to ensure user is Safety Officer or Admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        if not user or user.role not in ['admin', 'safety_officer']:
            return jsonify({'error': 'Unauthorized. Safety Officer or Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_incident_number(project_id):
    """Generate unique incident number: INC-{project_id}-{year}-{seq}"""
    year = datetime.now().year
    
    # Count existing incidents for this project and year
    existing = IncidentReport.query.filter(
        IncidentReport.project_id == project_id,
        extract('year', IncidentReport.incident_date) == year,
        IncidentReport.is_deleted == False
    ).count()
    
    seq = existing + 1
    return f"INC-{project_id}-{year}-{seq:04d}"

def calculate_incident_statistics(company_id, project_id=None, start_date=None, end_date=None):
    """Calculate OSHA incident rates and statistics"""
    query = IncidentReport.query.filter(
        IncidentReport.company_id == company_id,
        IncidentReport.is_deleted == False
    )
    
    if project_id:
        query = query.filter(IncidentReport.project_id == project_id)
    
    if start_date and end_date:
        query = query.filter(
            IncidentReport.incident_date >= start_date,
            IncidentReport.incident_date <= end_date
        )
    
    incidents = query.all()
    
    # Count by type
    type_counts = {}
    for inc_type in IncidentType:
        type_counts[inc_type.value] = sum(1 for inc in incidents if inc.incident_type == inc_type)
    
    # Count by severity
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for inc in incidents:
        if inc.severity:
            severity_counts[inc.severity] = severity_counts.get(inc.severity, 0) + 1
    
    # Total lost time
    total_lost_days = sum(inc.lost_time_days or 0 for inc in incidents)
    total_lost_hours = sum(inc.lost_time_hours or 0 for inc in incidents)
    
    # Total costs
    total_medical_cost = sum(inc.medical_cost or 0 for inc in incidents)
    total_property_cost = sum(inc.property_damage_cost or 0 for inc in incidents)
    total_cost = sum(inc.total_cost or 0 for inc in incidents)
    
    # Reportable incidents
    reportable_count = sum(1 for inc in incidents if inc.reportable_to_authority)
    
    return {
        'total_incidents': len(incidents),
        'by_type': type_counts,
        'by_severity': severity_counts,
        'fatalities': type_counts.get('FATALITY', 0),
        'major_injuries': type_counts.get('MAJOR_INJURY', 0),
        'minor_injuries': type_counts.get('MINOR_INJURY', 0),
        'near_misses': type_counts.get('NEAR_MISS', 0),
        'total_lost_days': total_lost_days,
        'total_lost_hours': total_lost_hours,
        'total_medical_cost': float(total_medical_cost),
        'total_property_cost': float(total_property_cost),
        'total_cost': float(total_cost),
        'reportable_count': reportable_count,
        'incident_frequency': len(incidents)  # Will calculate rate if hours_worked provided
    }


# ========================================
# 1. CREATE INCIDENT REPORT
# ========================================

@incident_bp.route('/api/incidents', methods=['POST'])
@jwt_required()
def create_incident():
    """
    Create new incident report
    Body: {
        project_id, incident_type, incident_date, incident_time,
        location, location_latitude, location_longitude,
        severity, incident_description, immediate_action_taken,
        injured_persons: [{name, age, company, injury_type, body_part, hospital, status}],
        witnesses: [{name, company, contact}],
        property_damage_description, damaged_equipment: [{equipment, extent, estimated_cost}],
        reportable_to_authority
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        required = ['project_id', 'incident_type', 'incident_date', 'location', 'severity', 'incident_description']
        if not all(field in data for field in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400
        
        # Verify project exists
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Verify user belongs to company
        user = User.query.get(user_id)
        if user.company_id != project.company_id:
            return jsonify({'error': 'Unauthorized. You do not belong to this project company.'}), 403
        
        # Parse dates
        incident_date = datetime.fromisoformat(data['incident_date'].replace('Z', '+00:00'))
        incident_time = data.get('incident_time')  # Optional HH:MM:SS format
        
        # Generate incident number
        incident_number = generate_incident_number(data['project_id'])
        
        # Create incident
        incident = IncidentReport(
            company_id=project.company_id,
            project_id=data['project_id'],
            incident_number=incident_number,
            incident_type=IncidentType[data['incident_type']],
            incident_date=incident_date,
            incident_time=incident_time,
            location=data['location'],
            location_latitude=data.get('location_latitude'),
            location_longitude=data.get('location_longitude'),
            severity=data['severity'],
            incident_description=data['incident_description'],
            immediate_action_taken=data.get('immediate_action_taken'),
            injured_persons=data.get('injured_persons', []),
            witnesses=data.get('witnesses', []),
            property_damage_description=data.get('property_damage_description'),
            damaged_equipment=data.get('damaged_equipment', []),
            reportable_to_authority=data.get('reportable_to_authority', False),
            authority_name=data.get('authority_name'),
            status=IncidentStatus.REPORTED,
            reported_by_id=user_id,
            created_by=user_id
        )
        
        # Set investigation_required based on severity
        incident.investigation_required = incident.severity >= 3 or incident.incident_type in [
            IncidentType.FATALITY, IncidentType.MAJOR_INJURY
        ]
        
        db.session.add(incident)
        db.session.commit()
        
        return jsonify({
            'message': 'Incident reported successfully',
            'incident': incident.to_dict(),
            'incident_number': incident_number,
            'investigation_required': incident.investigation_required
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 2. LIST INCIDENTS
# ========================================

@incident_bp.route('/api/incidents', methods=['GET'])
@jwt_required()
def list_incidents():
    """
    List incidents with filters
    Query params: project_id, incident_type, status, severity_min, start_date, end_date, reportable_only
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        # Base query
        query = IncidentReport.query.filter(
            IncidentReport.company_id == user.company_id,
            IncidentReport.is_deleted == False
        )
        
        # Filters
        if request.args.get('project_id'):
            query = query.filter(IncidentReport.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('incident_type'):
            query = query.filter(IncidentReport.incident_type == IncidentType[request.args.get('incident_type')])
        
        if request.args.get('status'):
            query = query.filter(IncidentReport.status == IncidentStatus[request.args.get('status')])
        
        if request.args.get('severity_min'):
            query = query.filter(IncidentReport.severity >= request.args.get('severity_min', type=int))
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(IncidentReport.incident_date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(IncidentReport.incident_date <= end_date)
        
        if request.args.get('reportable_only') == 'true':
            query = query.filter(IncidentReport.reportable_to_authority == True)
        
        # Order by date descending
        query = query.order_by(IncidentReport.incident_date.desc())
        
        incidents = query.all()
        
        return jsonify({
            'incidents': [inc.to_dict() for inc in incidents],
            'count': len(incidents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 3. GET INCIDENT DETAILS
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>', methods=['GET'])
@jwt_required()
def get_incident(incident_id):
    """Get detailed incident information"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        incident = IncidentReport.query.filter(
            IncidentReport.id == incident_id,
            IncidentReport.company_id == user.company_id,
            IncidentReport.is_deleted == False
        ).first()
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify({'incident': incident.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 4. ASSIGN INVESTIGATION TEAM
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/investigation', methods=['POST'])
@safety_officer_required
def assign_investigation_team(incident_id):
    """
    Assign investigation team and set investigation lead
    Body: {
        investigation_lead_id,
        investigation_team: [{user_id, name, role, assignment_date}],
        investigation_start_date
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Verify investigation lead exists
        lead_user = User.query.get(data['investigation_lead_id'])
        if not lead_user:
            return jsonify({'error': 'Investigation lead user not found'}), 404
        
        # Update incident
        incident.investigation_lead_id = data['investigation_lead_id']
        incident.investigation_team = data.get('investigation_team', [])
        incident.investigation_start_date = datetime.fromisoformat(data['investigation_start_date']) if data.get('investigation_start_date') else datetime.utcnow()
        incident.status = IncidentStatus.UNDER_INVESTIGATION
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Investigation team assigned successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 5. ADD WITNESS STATEMENTS
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/witnesses', methods=['POST'])
@jwt_required()
def add_witness_statements(incident_id):
    """
    Add or update witness statements
    Body: {
        witnesses: [{name, company, contact, statement, statement_date}]
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Merge new witnesses with existing
        existing_witnesses = incident.witnesses or []
        new_witnesses = data.get('witnesses', [])
        
        # Add statement_date to new witnesses if not provided
        for witness in new_witnesses:
            if 'statement_date' not in witness:
                witness['statement_date'] = datetime.utcnow().isoformat()
        
        incident.witnesses = existing_witnesses + new_witnesses
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Witness statements added successfully',
            'witnesses': incident.witnesses
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 6. UPLOAD EVIDENCE (PHOTOS/DOCUMENTS)
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/evidence', methods=['POST'])
@jwt_required()
def upload_evidence(incident_id):
    """
    Upload photos or documents
    Body: {
        photos: [{url, description}],
        documents: [{url, type, description}]
    }
    Note: Actual file upload should be handled separately (S3, etc.)
    This endpoint just records the URLs
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Add timestamp and uploader info
        current_time = datetime.utcnow().isoformat()
        
        # Photos
        if data.get('photos'):
            existing_photos = incident.photos or []
            for photo in data['photos']:
                photo['uploaded_by'] = user_id
                photo['uploaded_at'] = current_time
            incident.photos = existing_photos + data['photos']
        
        # Documents
        if data.get('documents'):
            existing_docs = incident.documents or []
            for doc in data['documents']:
                doc['uploaded_by'] = user_id
                doc['uploaded_at'] = current_time
            incident.documents = existing_docs + data['documents']
        
        incident.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Evidence uploaded successfully',
            'photos_count': len(incident.photos or []),
            'documents_count': len(incident.documents or [])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 7. SUBMIT ROOT CAUSE ANALYSIS
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/root-cause', methods=['POST'])
@safety_officer_required
def submit_root_cause(incident_id):
    """
    Submit root cause analysis findings
    Body: {
        immediate_causes: [{cause}],
        underlying_causes: [{cause}],
        root_cause_analysis: "5 Whys or Fishbone findings (text)",
        contributing_factors: [{factor}]
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Update RCA fields
        incident.immediate_causes = data.get('immediate_causes', [])
        incident.underlying_causes = data.get('underlying_causes', [])
        incident.root_cause_analysis = data.get('root_cause_analysis')
        incident.contributing_factors = data.get('contributing_factors', [])
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Root cause analysis submitted successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 8. ADD CORRECTIVE/PREVENTIVE ACTIONS
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/actions', methods=['POST'])
@safety_officer_required
def add_actions(incident_id):
    """
    Add corrective or preventive actions
    Body: {
        action_type: "corrective" | "preventive",
        actions: [{action, responsible_user_id, deadline, status}]
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        action_type = data.get('action_type')
        if action_type not in ['corrective', 'preventive']:
            return jsonify({'error': 'Invalid action_type. Must be "corrective" or "preventive"'}), 400
        
        # Add action_added_date
        for action in data.get('actions', []):
            action['added_by'] = user_id
            action['added_date'] = datetime.utcnow().isoformat()
            if 'status' not in action:
                action['status'] = 'pending'
        
        if action_type == 'corrective':
            existing = incident.corrective_actions or []
            incident.corrective_actions = existing + data.get('actions', [])
        else:
            existing = incident.preventive_actions or []
            incident.preventive_actions = existing + data.get('actions', [])
        
        # Update status
        if incident.status == IncidentStatus.UNDER_INVESTIGATION:
            incident.status = IncidentStatus.ACTIONS_PENDING
        
        incident.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': f'{action_type.capitalize()} actions added successfully',
            'corrective_actions_count': len(incident.corrective_actions or []),
            'preventive_actions_count': len(incident.preventive_actions or [])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 9. UPDATE ACTION STATUS
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/actions/<int:action_index>', methods=['PUT'])
@jwt_required()
def update_action_status(incident_id, action_index):
    """
    Update status of a specific action
    Body: {
        action_type: "corrective" | "preventive",
        status: "pending" | "in_progress" | "completed",
        completion_date (optional),
        remarks (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        action_type = data.get('action_type')
        actions = incident.corrective_actions if action_type == 'corrective' else incident.preventive_actions
        
        if not actions or action_index >= len(actions):
            return jsonify({'error': 'Action not found'}), 404
        
        # Update action
        actions[action_index]['status'] = data.get('status', 'pending')
        if data.get('completion_date'):
            actions[action_index]['completion_date'] = data['completion_date']
        if data.get('remarks'):
            actions[action_index]['remarks'] = data['remarks']
        
        # Save back
        if action_type == 'corrective':
            incident.corrective_actions = actions
        else:
            incident.preventive_actions = actions
        
        # Check if all actions completed
        corrective_done = all(act.get('status') == 'completed' for act in (incident.corrective_actions or []))
        preventive_done = all(act.get('status') == 'completed' for act in (incident.preventive_actions or []))
        
        if corrective_done and preventive_done:
            incident.status = IncidentStatus.ACTIONS_IN_PROGRESS
        
        incident.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Action status updated successfully',
            'action': actions[action_index]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 10. CLOSE INCIDENT
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/close', methods=['POST'])
@safety_officer_required
def close_incident(incident_id):
    """
    Close incident investigation
    Body: {
        closure_remarks,
        lessons_learned (optional),
        recommendations (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Validate all actions completed
        corrective_done = all(act.get('status') == 'completed' for act in (incident.corrective_actions or []))
        preventive_done = all(act.get('status') == 'completed' for act in (incident.preventive_actions or []))
        
        if not (corrective_done and preventive_done):
            return jsonify({'error': 'Cannot close incident. Some actions are still pending.'}), 400
        
        # Close incident
        incident.status = IncidentStatus.CLOSED
        incident.closed_by_id = user_id
        incident.closed_date = datetime.utcnow()
        incident.closure_remarks = data.get('closure_remarks')
        incident.lessons_learned = data.get('lessons_learned')
        incident.recommendations = data.get('recommendations')
        incident.investigation_end_date = datetime.utcnow()
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Incident closed successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 11. INCIDENT DASHBOARD/STATISTICS
# ========================================

@incident_bp.route('/api/incidents/dashboard', methods=['GET'])
@jwt_required()
def incident_dashboard():
    """
    Get incident statistics and dashboard data
    Query params: project_id, start_date, end_date, total_hours_worked
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        total_hours_worked = request.args.get('total_hours_worked', type=float)
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=365)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        # Get statistics
        stats = calculate_incident_statistics(
            user.company_id,
            project_id=project_id,
            start_date=start,
            end_date=end
        )
        
        # Calculate rates if hours worked provided
        if total_hours_worked and total_hours_worked > 0:
            # OSHA Incident Rate = (Number of injuries × 200,000) / Total hours worked
            stats['incident_rate'] = round((stats['total_incidents'] * 200000) / total_hours_worked, 2)
            
            # Severity Rate = (Total lost days × 200,000) / Total hours worked
            stats['severity_rate'] = round((stats['total_lost_days'] * 200000) / total_hours_worked, 2)
        
        # Monthly trend (last 12 months)
        monthly_query = IncidentReport.query.filter(
            IncidentReport.company_id == user.company_id,
            IncidentReport.incident_date >= datetime.now() - timedelta(days=365),
            IncidentReport.is_deleted == False
        )
        
        if project_id:
            monthly_query = monthly_query.filter(IncidentReport.project_id == project_id)
        
        monthly_data = db.session.query(
            extract('year', IncidentReport.incident_date).label('year'),
            extract('month', IncidentReport.incident_date).label('month'),
            func.count(IncidentReport.id).label('count')
        ).filter(
            IncidentReport.company_id == user.company_id,
            IncidentReport.incident_date >= datetime.now() - timedelta(days=365),
            IncidentReport.is_deleted == False
        ).group_by('year', 'month').all()
        
        stats['monthly_trend'] = [
            {'year': int(row.year), 'month': int(row.month), 'count': row.count}
            for row in monthly_data
        ]
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 12. REGULATORY REPORTS
# ========================================

@incident_bp.route('/api/incidents/reports/regulatory', methods=['GET'])
@safety_officer_required
def regulatory_reports():
    """
    Get all incidents reportable to authorities
    Query params: project_id, start_date, end_date, notified_only
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = IncidentReport.query.filter(
            IncidentReport.company_id == user.company_id,
            IncidentReport.reportable_to_authority == True,
            IncidentReport.is_deleted == False
        )
        
        # Filters
        if request.args.get('project_id'):
            query = query.filter(IncidentReport.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(IncidentReport.incident_date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(IncidentReport.incident_date <= end_date)
        
        if request.args.get('notified_only') == 'true':
            query = query.filter(IncidentReport.authority_notified == True)
        
        incidents = query.order_by(IncidentReport.incident_date.desc()).all()
        
        return jsonify({
            'incidents': [inc.to_dict() for inc in incidents],
            'count': len(incidents),
            'notified_count': sum(1 for inc in incidents if inc.authority_notified),
            'pending_notification_count': sum(1 for inc in incidents if not inc.authority_notified)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 13. UPDATE REGULATORY NOTIFICATION
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>/regulatory-notification', methods=['POST'])
@safety_officer_required
def update_regulatory_notification(incident_id):
    """
    Update regulatory authority notification details
    Body: {
        authority_notified: true,
        authority_notification_date,
        authority_reference_number,
        authority_report_pdf (S3 URL)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        if not incident.reportable_to_authority:
            return jsonify({'error': 'This incident is not reportable to authorities'}), 400
        
        # Update notification fields
        incident.authority_notified = data.get('authority_notified', True)
        incident.authority_notification_date = datetime.fromisoformat(data['authority_notification_date']) if data.get('authority_notification_date') else datetime.utcnow()
        incident.authority_reference_number = data.get('authority_reference_number')
        incident.authority_report_pdf = data.get('authority_report_pdf')
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Regulatory notification details updated successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 14. UPDATE INCIDENT (GENERAL)
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>', methods=['PUT'])
@jwt_required()
def update_incident(incident_id):
    """
    Update incident details
    Body: Any incident fields to update (excluding status, which has dedicated endpoints)
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Update allowed fields
        allowed_fields = [
            'incident_description', 'immediate_action_taken',
            'location', 'location_latitude', 'location_longitude',
            'severity', 'injured_persons', 'property_damage_description',
            'damaged_equipment', 'lost_time_hours', 'lost_time_days',
            'medical_cost', 'property_damage_cost', 'total_cost'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(incident, field, data[field])
        
        incident.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Incident updated successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 15. DELETE INCIDENT (SOFT DELETE)
# ========================================

@incident_bp.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
@safety_officer_required
def delete_incident(incident_id):
    """Soft delete incident (Admin/Safety Officer only)"""
    try:
        user_id = get_current_user_id()
        
        incident = IncidentReport.query.get(incident_id)
        if not incident or incident.is_deleted:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Check if already closed
        if incident.status == IncidentStatus.CLOSED:
            return jsonify({'error': 'Cannot delete closed incidents. Contact admin.'}), 400
        
        incident.is_deleted = True
        incident.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({'message': 'Incident deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
