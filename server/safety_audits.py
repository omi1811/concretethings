"""
Safety Audits API
Endpoints for scheduling, conducting, and closing safety audits
ISO 45001:2018 Clause 9.2 (Internal Audit)
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_, or_
from server.db import db
from server.models import User, Company, Project
from server.safety_audit_models import SafetyAudit, AuditChecklist, AuditType, AuditStatus, FindingSeverity, AuditGrade, seed_standard_checklists
from flask_jwt_extended import jwt_required, get_jwt_identity

audit_bp = Blueprint('safety_audits', __name__)

def get_current_user_id():
    """Extract user ID from JWT token"""
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

def generate_audit_number(project_id):
    """Generate unique audit number: AUDIT-{project_id}-{year}-{seq}"""
    year = datetime.now().year
    existing = SafetyAudit.query.filter(
        SafetyAudit.project_id == project_id,
        extract('year', SafetyAudit.scheduled_date) == year,
        SafetyAudit.is_deleted == False
    ).count()
    seq = existing + 1
    return f"AUDIT-{project_id}-{year}-{seq:04d}"

# ========================================
# 1. CREATE/SCHEDULE AUDIT
# ========================================

@audit_bp.route('/api/safety-audits', methods=['POST'])
@safety_officer_required
def create_audit():
    """
    Schedule a new safety audit
    Body: {
        project_id, audit_type, audit_title, audit_description,
        scheduled_date, lead_auditor_id, audit_team: [{user_id, name, role}],
        audit_location, audit_scope, areas_covered: [],
        checklist_id (optional - will use default if not provided)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        required = ['project_id', 'audit_type', 'audit_title', 'scheduled_date', 'lead_auditor_id']
        if not all(field in data for field in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400
        
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get or create default checklist
        checklist_id = data.get('checklist_id')
        if not checklist_id:
            checklist = AuditChecklist.query.filter_by(
                company_id=project.company_id,
                audit_type=AuditType[data['audit_type']],
                is_default=True,
                is_deleted=False
            ).first()
            
            if not checklist:
                # Seed standard checklists if not exists
                seed_standard_checklists(project.company_id, user_id)
                checklist = AuditChecklist.query.filter_by(
                    company_id=project.company_id,
                    is_default=True,
                    is_deleted=False
                ).first()
            
            checklist_id = checklist.id if checklist else None
        
        # Generate audit number
        audit_number = generate_audit_number(data['project_id'])
        
        # Create audit
        audit = SafetyAudit(
            company_id=project.company_id,
            project_id=data['project_id'],
            audit_number=audit_number,
            audit_type=AuditType[data['audit_type']],
            audit_title=data['audit_title'],
            audit_description=data.get('audit_description'),
            scheduled_date=datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00')),
            scheduled_by_id=user_id,
            lead_auditor_id=data['lead_auditor_id'],
            audit_team=data.get('audit_team', []),
            audit_location=data.get('audit_location'),
            audit_scope=data.get('audit_scope'),
            areas_covered=data.get('areas_covered', []),
            checklist_id=checklist_id,
            status=AuditStatus.SCHEDULED,
            created_by=user_id
        )
        
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'message': 'Audit scheduled successfully',
            'audit': audit.to_dict(),
            'audit_number': audit_number
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 2. LIST AUDITS
# ========================================

@audit_bp.route('/api/safety-audits', methods=['GET'])
@jwt_required()
def list_audits():
    """
    List audits with filters
    Query params: project_id, audit_type, status, start_date, end_date, lead_auditor_id
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = SafetyAudit.query.filter(
            SafetyAudit.company_id == user.company_id,
            SafetyAudit.is_deleted == False
        )
        
        if request.args.get('project_id'):
            query = query.filter(SafetyAudit.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('audit_type'):
            query = query.filter(SafetyAudit.audit_type == AuditType[request.args.get('audit_type')])
        
        if request.args.get('status'):
            query = query.filter(SafetyAudit.status == AuditStatus[request.args.get('status')])
        
        if request.args.get('lead_auditor_id'):
            query = query.filter(SafetyAudit.lead_auditor_id == request.args.get('lead_auditor_id', type=int))
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(SafetyAudit.scheduled_date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(SafetyAudit.scheduled_date <= end_date)
        
        query = query.order_by(SafetyAudit.scheduled_date.desc())
        audits = query.all()
        
        return jsonify({
            'audits': [audit.to_dict() for audit in audits],
            'count': len(audits)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 3. GET AUDIT DETAILS
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>', methods=['GET'])
@jwt_required()
def get_audit(audit_id):
    """Get detailed audit information"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        audit = SafetyAudit.query.filter(
            SafetyAudit.id == audit_id,
            SafetyAudit.company_id == user.company_id,
            SafetyAudit.is_deleted == False
        ).first()
        
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        return jsonify({'audit': audit.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 4. START AUDIT
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/start', methods=['POST'])
@jwt_required()
def start_audit(audit_id):
    """
    Start audit execution (loads checklist snapshot)
    Body: {
        actual_start_time (optional - defaults to now)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        if audit.status != AuditStatus.SCHEDULED:
            return jsonify({'error': f'Audit already started. Current status: {audit.status.value}'}), 400
        
        # Load checklist snapshot
        if audit.checklist_id:
            checklist = AuditChecklist.query.get(audit.checklist_id)
            if checklist:
                # Create editable snapshot
                audit.checklist_items = [
                    {**item, 'compliant': None, 'evidence_photo': None, 'remarks': '', 'corrective_action_required': False}
                    for item in checklist.items
                ]
                audit.total_items = len(checklist.items)
        
        audit.actual_start_time = datetime.fromisoformat(data['actual_start_time']) if data.get('actual_start_time') else datetime.utcnow()
        audit.status = AuditStatus.IN_PROGRESS
        audit.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Audit started successfully',
            'audit': audit.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 5. UPDATE CHECKLIST ITEM
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/checklist/<int:item_index>', methods=['PUT'])
@jwt_required()
def update_checklist_item(audit_id, item_index):
    """
    Update a specific checklist item
    Body: {
        compliant: true/false/null (null = N/A),
        evidence_photo: "S3 URL",
        remarks: "text",
        corrective_action_required: true/false
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        if not audit.checklist_items or item_index >= len(audit.checklist_items):
            return jsonify({'error': 'Checklist item not found'}), 404
        
        # Update item
        audit.checklist_items[item_index].update({
            'compliant': data.get('compliant'),
            'evidence_photo': data.get('evidence_photo'),
            'remarks': data.get('remarks', ''),
            'corrective_action_required': data.get('corrective_action_required', False),
            'updated_by': user_id,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Recalculate scoring
        audit.compliant_items = sum(1 for item in audit.checklist_items if item.get('compliant') is True)
        audit.non_compliant_items = sum(1 for item in audit.checklist_items if item.get('compliant') is False)
        audit.not_applicable_items = sum(1 for item in audit.checklist_items if item.get('compliant') is None)
        audit.calculate_score()
        
        audit.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Checklist item updated successfully',
            'item': audit.checklist_items[item_index],
            'scoring': {
                'compliance_percentage': float(audit.compliance_percentage) if audit.compliance_percentage else 0.0,
                'audit_grade': audit.audit_grade.value if audit.audit_grade else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 6. ADD FINDING
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/findings', methods=['POST'])
@jwt_required()
def add_finding(audit_id):
    """
    Add a new finding
    Body: {
        severity: "OBSERVATION|MINOR_NC|MAJOR_NC|CRITICAL",
        category, finding, evidence_photos: [],
        location, corrective_action,
        responsible_user_id, deadline
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        # Create finding
        finding = {
            'severity': data.get('severity', 'OBSERVATION'),
            'category': data.get('category'),
            'finding': data['finding'],
            'evidence_photos': data.get('evidence_photos', []),
            'location': data.get('location'),
            'corrective_action': data.get('corrective_action'),
            'responsible_user_id': data.get('responsible_user_id'),
            'deadline': data.get('deadline'),
            'status': 'pending',
            'added_by': user_id,
            'added_date': datetime.utcnow().isoformat()
        }
        
        findings = audit.findings_details or []
        findings.append(finding)
        audit.findings_details = findings
        
        # Update counts
        audit.count_findings()
        audit.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Finding added successfully',
            'finding': finding,
            'total_findings': audit.total_findings
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 7. UPLOAD EVIDENCE
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/evidence', methods=['POST'])
@jwt_required()
def upload_evidence(audit_id):
    """
    Upload photos or documents
    Body: {
        photos: [{url, description, category}],
        documents: [{url, type, description}]
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        current_time = datetime.utcnow().isoformat()
        
        if data.get('photos'):
            existing_photos = audit.photos or []
            for photo in data['photos']:
                photo['uploaded_by'] = user_id
                photo['timestamp'] = current_time
            audit.photos = existing_photos + data['photos']
        
        if data.get('documents'):
            existing_docs = audit.documents or []
            for doc in data['documents']:
                doc['uploaded_by'] = user_id
                doc['timestamp'] = current_time
            audit.documents = existing_docs + data['documents']
        
        audit.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Evidence uploaded successfully',
            'photos_count': len(audit.photos or []),
            'documents_count': len(audit.documents or [])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 8. COMPLETE AUDIT
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/complete', methods=['POST'])
@safety_officer_required
def complete_audit(audit_id):
    """
    Complete audit (calculate final scores)
    Body: {
        actual_end_time (optional),
        positive_observations, areas_of_concern,
        immediate_actions_required, long_term_improvements,
        training_recommendations: [{topic, target_audience, priority}],
        iso_clauses_checked: [], osha_standards_checked: []
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        if audit.status not in [AuditStatus.IN_PROGRESS, AuditStatus.SCHEDULED]:
            return jsonify({'error': f'Cannot complete audit. Current status: {audit.status.value}'}), 400
        
        # Set end time and duration
        audit.actual_end_time = datetime.fromisoformat(data['actual_end_time']) if data.get('actual_end_time') else datetime.utcnow()
        if audit.actual_start_time:
            delta = audit.actual_end_time - audit.actual_start_time
            audit.audit_duration_minutes = int(delta.total_seconds() / 60)
        
        # Update analysis fields
        audit.positive_observations = data.get('positive_observations')
        audit.areas_of_concern = data.get('areas_of_concern')
        audit.immediate_actions_required = data.get('immediate_actions_required')
        audit.long_term_improvements = data.get('long_term_improvements')
        audit.training_recommendations = data.get('training_recommendations', [])
        audit.iso_clauses_checked = data.get('iso_clauses_checked', [])
        audit.osha_standards_checked = data.get('osha_standards_checked', [])
        
        # Final score calculation
        audit.calculate_score()
        audit.count_findings()
        
        # Update status
        if audit.total_findings > 0:
            audit.status = AuditStatus.FINDINGS_PENDING
        else:
            audit.status = AuditStatus.COMPLETED
        
        audit.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Audit completed successfully',
            'audit': audit.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 9. UPDATE FINDING STATUS
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/findings/<int:finding_index>', methods=['PUT'])
@jwt_required()
def update_finding_status(audit_id, finding_index):
    """
    Update finding status
    Body: {
        status: "pending|in_progress|completed",
        completion_date (optional),
        completion_remarks (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        findings = audit.findings_details or []
        if finding_index >= len(findings):
            return jsonify({'error': 'Finding not found'}), 404
        
        findings[finding_index]['status'] = data.get('status', 'pending')
        if data.get('completion_date'):
            findings[finding_index]['completion_date'] = data['completion_date']
        if data.get('completion_remarks'):
            findings[finding_index]['completion_remarks'] = data['completion_remarks']
        
        audit.findings_details = findings
        
        # Update action counts
        audit.actions_assigned = len(findings)
        audit.actions_completed = sum(1 for f in findings if f.get('status') == 'completed')
        
        # Check if overdue
        audit.actions_overdue = 0
        for f in findings:
            if f.get('status') != 'completed' and f.get('deadline'):
                deadline = datetime.fromisoformat(f['deadline'])
                if deadline < datetime.utcnow():
                    audit.actions_overdue += 1
        
        # Update status
        if audit.actions_completed == audit.actions_assigned and audit.actions_assigned > 0:
            audit.status = AuditStatus.COMPLETED
        elif audit.actions_assigned > 0:
            audit.status = AuditStatus.ACTIONS_PENDING
        
        audit.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': 'Finding status updated successfully',
            'finding': findings[finding_index],
            'actions_completed': audit.actions_completed,
            'actions_pending': audit.actions_assigned - audit.actions_completed
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 10. CLOSE AUDIT
# ========================================

@audit_bp.route('/api/safety-audits/<int:audit_id>/close', methods=['POST'])
@safety_officer_required
def close_audit(audit_id):
    """
    Close audit (all findings resolved)
    Body: {
        closure_remarks
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        audit = SafetyAudit.query.get(audit_id)
        if not audit or audit.is_deleted:
            return jsonify({'error': 'Audit not found'}), 404
        
        # Validate all findings completed
        if audit.actions_assigned > audit.actions_completed:
            return jsonify({
                'error': f'Cannot close audit. {audit.actions_assigned - audit.actions_completed} findings still pending.'
            }), 400
        
        audit.status = AuditStatus.CLOSED
        audit.closed_by_id = user_id
        audit.closed_date = datetime.utcnow()
        audit.closure_remarks = data.get('closure_remarks')
        audit.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Audit closed successfully',
            'audit': audit.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 11. AUDIT DASHBOARD/STATISTICS
# ========================================

@audit_bp.route('/api/safety-audits/dashboard', methods=['GET'])
@jwt_required()
def audit_dashboard():
    """
    Get audit statistics
    Query params: project_id, start_date, end_date
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = SafetyAudit.query.filter(
            SafetyAudit.company_id == user.company_id,
            SafetyAudit.is_deleted == False
        )
        
        if request.args.get('project_id'):
            query = query.filter(SafetyAudit.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(SafetyAudit.scheduled_date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(SafetyAudit.scheduled_date <= end_date)
        
        audits = query.all()
        
        # Calculate statistics
        total_audits = len(audits)
        completed = sum(1 for a in audits if a.status == AuditStatus.COMPLETED or a.status == AuditStatus.CLOSED)
        in_progress = sum(1 for a in audits if a.status == AuditStatus.IN_PROGRESS)
        scheduled = sum(1 for a in audits if a.status == AuditStatus.SCHEDULED)
        
        # Average compliance score
        completed_audits = [a for a in audits if a.compliance_percentage is not None]
        avg_compliance = sum(float(a.compliance_percentage) for a in completed_audits) / len(completed_audits) if completed_audits else 0
        
        # Grade distribution
        grade_counts = {grade.value: 0 for grade in AuditGrade}
        for audit in audits:
            if audit.audit_grade:
                grade_counts[audit.audit_grade.value] += 1
        
        # Findings summary
        total_findings = sum(a.total_findings for a in audits)
        total_critical = sum(a.critical_findings for a in audits)
        total_major_ncs = sum(a.major_ncs for a in audits)
        total_minor_ncs = sum(a.minor_ncs for a in audits)
        
        # Monthly trend
        monthly_data = db.session.query(
            extract('year', SafetyAudit.scheduled_date).label('year'),
            extract('month', SafetyAudit.scheduled_date).label('month'),
            func.count(SafetyAudit.id).label('count'),
            func.avg(SafetyAudit.compliance_percentage).label('avg_compliance')
        ).filter(
            SafetyAudit.company_id == user.company_id,
            SafetyAudit.scheduled_date >= datetime.now() - timedelta(days=365),
            SafetyAudit.is_deleted == False
        ).group_by('year', 'month').all()
        
        return jsonify({
            'total_audits': total_audits,
            'completed': completed,
            'in_progress': in_progress,
            'scheduled': scheduled,
            'average_compliance_percentage': round(avg_compliance, 2),
            'grade_distribution': grade_counts,
            'findings_summary': {
                'total': total_findings,
                'critical': total_critical,
                'major_ncs': total_major_ncs,
                'minor_ncs': total_minor_ncs
            },
            'monthly_trend': [
                {
                    'year': int(row.year),
                    'month': int(row.month),
                    'count': row.count,
                    'avg_compliance': round(float(row.avg_compliance), 2) if row.avg_compliance else 0
                }
                for row in monthly_data
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 12. CHECKLIST TEMPLATES
# ========================================

@audit_bp.route('/api/audit-checklists', methods=['GET'])
@jwt_required()
def list_checklists():
    """Get all active checklist templates"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        checklists = AuditChecklist.query.filter(
            AuditChecklist.company_id == user.company_id,
            AuditChecklist.is_active == True,
            AuditChecklist.is_deleted == False
        ).order_by(AuditChecklist.audit_type, AuditChecklist.checklist_name).all()
        
        return jsonify({
            'checklists': [c.to_dict() for c in checklists],
            'count': len(checklists)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audit_bp.route('/api/audit-checklists/<int:checklist_id>', methods=['GET'])
@jwt_required()
def get_checklist(checklist_id):
    """Get checklist details"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        checklist = AuditChecklist.query.filter(
            AuditChecklist.id == checklist_id,
            AuditChecklist.company_id == user.company_id,
            AuditChecklist.is_deleted == False
        ).first()
        
        if not checklist:
            return jsonify({'error': 'Checklist not found'}), 404
        
        return jsonify({'checklist': checklist.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audit_bp.route('/api/audit-checklists/seed', methods=['POST'])
@safety_officer_required
def seed_checklists():
    """Seed standard checklist templates for company"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        result = seed_standard_checklists(user.company_id, user_id)
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
