"""
Handover Register API

Manages work completion handovers between contractors with:
- Multi-party signatures (Contractor 1, Contractor 2, Building Engineer)
- Defects/snag list tracking
- Work completion certificates
- Inspection checklist
- Photo documentation
- Approval workflow
- PDF generation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import json

try:
    from .db import Base, session_scope
except ImportError:
    from db import Base, session_scope

handover_bp = Blueprint('handover', __name__)


def get_current_user_id():
    """Extract user_id from JWT identity."""
    return int(get_jwt_identity())


class HandoverRegister(Base):
    """
    Work Handover Register Model
    
    Tracks completion and handover of construction work between contractors
    """
    __tablename__ = "handover_register"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    handover_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Work Details
    work_description = Column(Text, nullable=False)
    work_location = Column(String(255), nullable=False)
    work_category = Column(String(100), nullable=False)  # Structural, MEP, Finishing, etc.
    floor_level = Column(String(50), nullable=True)
    zone_area = Column(String(100), nullable=True)
    
    # Contractor Information (no foreign keys - contractors are separate entities from RMC vendors)
    outgoing_contractor_name = Column(String(255), nullable=False)
    outgoing_contractor_company = Column(String(255), nullable=True)
    outgoing_supervisor_name = Column(String(255), nullable=False)
    outgoing_supervisor_phone = Column(String(20), nullable=True)
    outgoing_supervisor_signature = Column(Text, nullable=True)  # Base64 or URL
    outgoing_signed_date = Column(DateTime, nullable=True)
    
    incoming_contractor_name = Column(String(255), nullable=True)
    incoming_contractor_company = Column(String(255), nullable=True)
    incoming_supervisor_name = Column(String(255), nullable=True)
    incoming_supervisor_phone = Column(String(20), nullable=True)
    incoming_supervisor_signature = Column(Text, nullable=True)
    incoming_signed_date = Column(DateTime, nullable=True)
    
    # Engineer/Project Manager
    engineer_name = Column(String(255), nullable=False)
    engineer_designation = Column(String(100), nullable=True)
    engineer_signature = Column(Text, nullable=True)
    engineer_signed_date = Column(DateTime, nullable=True)
    engineer_remarks = Column(Text, nullable=True)
    
    # Dates
    work_start_date = Column(DateTime, nullable=True)
    work_completion_date = Column(DateTime, nullable=False)
    handover_date = Column(DateTime, nullable=False)
    target_rectification_date = Column(DateTime, nullable=True)
    
    # Status & Workflow
    status = Column(String(50), default='draft')  # draft, pending_approval, approved, rejected, completed
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    
    # Quality & Inspection
    quality_standard_met = Column(Boolean, default=True)
    inspection_completed = Column(Boolean, default=False)
    inspection_date = Column(DateTime, nullable=True)
    inspection_checklist = Column(Text, nullable=True)  # JSON string
    
    # Defects/Snag List
    has_defects = Column(Boolean, default=False)
    defects_list = Column(Text, nullable=True)  # JSON array of defects
    defects_count = Column(Integer, default=0)
    critical_defects_count = Column(Integer, default=0)
    
    # Work Scope & Deliverables
    work_scope = Column(Text, nullable=True)
    deliverables = Column(Text, nullable=True)  # JSON array
    materials_used = Column(Text, nullable=True)  # JSON array
    
    # Documentation
    photos = Column(Text, nullable=True)  # JSON array of photo URLs
    attachments = Column(Text, nullable=True)  # JSON array of document URLs
    test_certificates = Column(Text, nullable=True)  # JSON array
    
    # Warranty & Maintenance
    warranty_period_months = Column(Integer, default=12)
    warranty_start_date = Column(DateTime, nullable=True)
    warranty_end_date = Column(DateTime, nullable=True)
    maintenance_instructions = Column(Text, nullable=True)
    
    # Remarks & Notes
    general_remarks = Column(Text, nullable=True)
    safety_notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Audit Trail
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    def to_dict(self):
        """Convert handover record to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'handover_number': self.handover_number,
            
            # Work Details
            'work_description': self.work_description,
            'work_location': self.work_location,
            'work_category': self.work_category,
            'floor_level': self.floor_level,
            'zone_area': self.zone_area,
            
            # Contractor Info
            'outgoing_contractor_name': self.outgoing_contractor_name,
            'outgoing_contractor_id': self.outgoing_contractor_id,
            'outgoing_supervisor_name': self.outgoing_supervisor_name,
            'outgoing_supervisor_phone': self.outgoing_supervisor_phone,
            'outgoing_supervisor_signature': self.outgoing_supervisor_signature,
            'outgoing_signed_date': self.outgoing_signed_date.isoformat() if self.outgoing_signed_date else None,
            
            'incoming_contractor_name': self.incoming_contractor_name,
            'incoming_contractor_id': self.incoming_contractor_id,
            'incoming_supervisor_name': self.incoming_supervisor_name,
            'incoming_supervisor_phone': self.incoming_supervisor_phone,
            'incoming_supervisor_signature': self.incoming_supervisor_signature,
            'incoming_signed_date': self.incoming_signed_date.isoformat() if self.incoming_signed_date else None,
            
            # Engineer
            'engineer_name': self.engineer_name,
            'engineer_designation': self.engineer_designation,
            'engineer_signature': self.engineer_signature,
            'engineer_signed_date': self.engineer_signed_date.isoformat() if self.engineer_signed_date else None,
            'engineer_remarks': self.engineer_remarks,
            
            # Dates
            'work_start_date': self.work_start_date.isoformat() if self.work_start_date else None,
            'work_completion_date': self.work_completion_date.isoformat() if self.work_completion_date else None,
            'handover_date': self.handover_date.isoformat() if self.handover_date else None,
            'target_rectification_date': self.target_rectification_date.isoformat() if self.target_rectification_date else None,
            
            # Status
            'status': self.status,
            'approval_status': self.approval_status,
            
            # Quality
            'quality_standard_met': self.quality_standard_met,
            'inspection_completed': self.inspection_completed,
            'inspection_date': self.inspection_date.isoformat() if self.inspection_date else None,
            'inspection_checklist': json.loads(self.inspection_checklist) if self.inspection_checklist else [],
            
            # Defects
            'has_defects': self.has_defects,
            'defects_list': json.loads(self.defects_list) if self.defects_list else [],
            'defects_count': self.defects_count,
            'critical_defects_count': self.critical_defects_count,
            
            # Work Scope
            'work_scope': self.work_scope,
            'deliverables': json.loads(self.deliverables) if self.deliverables else [],
            'materials_used': json.loads(self.materials_used) if self.materials_used else [],
            
            # Documentation
            'photos': json.loads(self.photos) if self.photos else [],
            'attachments': json.loads(self.attachments) if self.attachments else [],
            'test_certificates': json.loads(self.test_certificates) if self.test_certificates else [],
            
            # Warranty
            'warranty_period_months': self.warranty_period_months,
            'warranty_start_date': self.warranty_start_date.isoformat() if self.warranty_start_date else None,
            'warranty_end_date': self.warranty_end_date.isoformat() if self.warranty_end_date else None,
            'maintenance_instructions': self.maintenance_instructions,
            
            # Remarks
            'general_remarks': self.general_remarks,
            'safety_notes': self.safety_notes,
            'special_instructions': self.special_instructions,
            
            # Audit
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
        }


def generate_handover_number(project_id, session):
    """Generate unique handover number: HO-PROJ001-001"""
    # Count existing handovers for this project
    count = session.query(HandoverRegister).filter_by(
        project_id=project_id, 
        is_deleted=False
    ).count()
    
    return f"HO-PROJ{project_id:03d}-{count + 1:03d}"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@handover_bp.route('/handover-register', methods=['GET'])
@jwt_required()
def get_handovers():
    """
    Get list of handover records
    
    Query Parameters:
    - project_id (required): Filter by project
    - status: Filter by status (draft, pending_approval, approved, etc.)
    - work_category: Filter by work category
    - has_defects: Filter by defect presence (true/false)
    - date_from: Filter by handover date (ISO format)
    - date_to: Filter by handover date (ISO format)
    """
    try:
        project_id = request.args.get('project_id', type=int)
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        status = request.args.get('status')
        work_category = request.args.get('work_category')
        has_defects = request.args.get('has_defects')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        with session_scope() as session:
            query = session.query(HandoverRegister).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            if status:
                query = query.filter(HandoverRegister.status == status)
            
            if work_category:
                query = query.filter(HandoverRegister.work_category == work_category)
            
            if has_defects is not None:
                has_defects_bool = has_defects.lower() == 'true'
                query = query.filter(HandoverRegister.has_defects == has_defects_bool)
            
            if date_from:
                try:
                    date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(HandoverRegister.handover_date >= date_from_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_from format"}), 400
            
            if date_to:
                try:
                    date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(HandoverRegister.handover_date <= date_to_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_to format"}), 400
            
            handovers = query.order_by(HandoverRegister.handover_date.desc()).all()
            
            return jsonify({
                "success": True,
                "count": len(handovers),
                "handovers": [h.to_dict() for h in handovers]
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>', methods=['GET'])
@jwt_required()
def get_handover( handover_id):
    """Get single handover record by ID"""
    try:
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            return jsonify({
                "success": True,
                "handover": handover.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register', methods=['POST'])
@jwt_required()
def create_handover():
    """Create new handover record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'project_id', 'work_description', 'work_location', 'work_category',
            'outgoing_contractor_name', 'outgoing_supervisor_name',
            'engineer_name', 'work_completion_date', 'handover_date'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        with session_scope() as session:
            # Generate handover number
            handover_number = generate_handover_number(data['project_id'], session)
            
            # Parse dates
            work_completion_date = datetime.fromisoformat(data['work_completion_date'].replace('Z', '+00:00'))
            handover_date = datetime.fromisoformat(data['handover_date'].replace('Z', '+00:00'))
            
            work_start_date = None
            if data.get('work_start_date'):
                work_start_date = datetime.fromisoformat(data['work_start_date'].replace('Z', '+00:00'))
            
            # Calculate warranty dates if warranty period is provided
            warranty_start = None
            warranty_end = None
            warranty_months = data.get('warranty_period_months', 12)
            if data.get('warranty_start_date'):
                warranty_start = datetime.fromisoformat(data['warranty_start_date'].replace('Z', '+00:00'))
                warranty_end = warranty_start + timedelta(days=warranty_months * 30)
            
            # Handle defects list
            defects_list = data.get('defects_list', [])
            defects_count = len(defects_list)
            critical_defects_count = sum(1 for d in defects_list if d.get('severity') == 'critical')
            
            # Create handover record
            handover = HandoverRegister(
                project_id=data['project_id'],
                handover_number=handover_number,
                
                # Work Details
                work_description=data['work_description'],
                work_location=data['work_location'],
                work_category=data['work_category'],
                floor_level=data.get('floor_level'),
                zone_area=data.get('zone_area'),
                
                # Contractor Info
                outgoing_contractor_name=data['outgoing_contractor_name'],
                outgoing_contractor_id=data.get('outgoing_contractor_id'),
                outgoing_supervisor_name=data['outgoing_supervisor_name'],
                outgoing_supervisor_phone=data.get('outgoing_supervisor_phone'),
                
                incoming_contractor_name=data.get('incoming_contractor_name'),
                incoming_contractor_id=data.get('incoming_contractor_id'),
                incoming_supervisor_name=data.get('incoming_supervisor_name'),
                incoming_supervisor_phone=data.get('incoming_supervisor_phone'),
                
                # Engineer
                engineer_name=data['engineer_name'],
                engineer_designation=data.get('engineer_designation'),
                engineer_remarks=data.get('engineer_remarks'),
                
                # Dates
                work_start_date=work_start_date,
                work_completion_date=work_completion_date,
                handover_date=handover_date,
                target_rectification_date=datetime.fromisoformat(data['target_rectification_date'].replace('Z', '+00:00')) if data.get('target_rectification_date') else None,
                
                # Status
                status=data.get('status', 'draft'),
                
                # Quality
                quality_standard_met=data.get('quality_standard_met', True),
                inspection_completed=data.get('inspection_completed', False),
                inspection_date=datetime.fromisoformat(data['inspection_date'].replace('Z', '+00:00')) if data.get('inspection_date') else None,
                inspection_checklist=json.dumps(data.get('inspection_checklist', [])),
                
                # Defects
                has_defects=len(defects_list) > 0,
                defects_list=json.dumps(defects_list),
                defects_count=defects_count,
                critical_defects_count=critical_defects_count,
                
                # Work Scope
                work_scope=data.get('work_scope'),
                deliverables=json.dumps(data.get('deliverables', [])),
                materials_used=json.dumps(data.get('materials_used', [])),
                
                # Documentation
                photos=json.dumps(data.get('photos', [])),
                attachments=json.dumps(data.get('attachments', [])),
                test_certificates=json.dumps(data.get('test_certificates', [])),
                
                # Warranty
                warranty_period_months=warranty_months,
                warranty_start_date=warranty_start,
                warranty_end_date=warranty_end,
                maintenance_instructions=data.get('maintenance_instructions'),
                
                # Remarks
                general_remarks=data.get('general_remarks'),
                safety_notes=data.get('safety_notes'),
                special_instructions=data.get('special_instructions'),
                
                # Audit
                created_by=get_current_user_id()
            )
            
            session.add(handover)
            session.flush()  # Get the ID
            
            # TODO: Send notification if status is pending approval
            # if handover.status == 'pending_approval':
            #     try:
            #         send_handover_notification(handover.id, 'created')
            #     except Exception as e:
            #         print(f"Failed to send notification: {e}")
            
            return jsonify({
                "success": True,
                "message": "Handover record created successfully",
                "handover": handover.to_dict()
            }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>', methods=['PUT'])
@jwt_required()
def update_handover( handover_id):
    """Update handover record"""
    try:
        data = request.get_json()
        
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            # Update fields
            updatable_fields = [
                'work_description', 'work_location', 'work_category', 'floor_level', 'zone_area',
                'outgoing_contractor_name', 'outgoing_supervisor_name', 'outgoing_supervisor_phone',
                'incoming_contractor_name', 'incoming_supervisor_name', 'incoming_supervisor_phone',
                'engineer_name', 'engineer_designation', 'engineer_remarks',
                'status', 'quality_standard_met', 'inspection_completed',
                'work_scope', 'maintenance_instructions', 'general_remarks',
                'safety_notes', 'special_instructions'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(handover, field, data[field])
            
            # Handle date fields
            date_fields = {
                'work_start_date': 'work_start_date',
                'work_completion_date': 'work_completion_date',
                'handover_date': 'handover_date',
                'target_rectification_date': 'target_rectification_date',
                'inspection_date': 'inspection_date',
                'warranty_start_date': 'warranty_start_date'
            }
            
            for field, db_field in date_fields.items():
                if field in data and data[field]:
                    setattr(handover, db_field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
            
            # Handle JSON fields
            if 'defects_list' in data:
                defects_list = data['defects_list']
                handover.defects_list = json.dumps(defects_list)
                handover.defects_count = len(defects_list)
                handover.critical_defects_count = sum(1 for d in defects_list if d.get('severity') == 'critical')
                handover.has_defects = len(defects_list) > 0
            
            if 'inspection_checklist' in data:
                handover.inspection_checklist = json.dumps(data['inspection_checklist'])
            
            if 'deliverables' in data:
                handover.deliverables = json.dumps(data['deliverables'])
            
            if 'materials_used' in data:
                handover.materials_used = json.dumps(data['materials_used'])
            
            if 'photos' in data:
                handover.photos = json.dumps(data['photos'])
            
            if 'attachments' in data:
                handover.attachments = json.dumps(data['attachments'])
            
            if 'test_certificates' in data:
                handover.test_certificates = json.dumps(data['test_certificates'])
            
            handover.updated_at = datetime.utcnow()
            
            return jsonify({
                "success": True,
                "message": "Handover record updated successfully",
                "handover": handover.to_dict()
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>/sign', methods=['POST'])
@jwt_required()
def add_signature( handover_id):
    """Add signature to handover record"""
    try:
        data = request.get_json()
        
        signature_type = data.get('signature_type')  # outgoing, incoming, engineer
        signature_data = data.get('signature')  # Base64 or URL
        
        if not signature_type or not signature_data:
            return jsonify({"error": "signature_type and signature are required"}), 400
        
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            # Add signature
            if signature_type == 'outgoing':
                handover.outgoing_supervisor_signature = signature_data
                handover.outgoing_signed_date = datetime.utcnow()
            elif signature_type == 'incoming':
                handover.incoming_supervisor_signature = signature_data
                handover.incoming_signed_date = datetime.utcnow()
            elif signature_type == 'engineer':
                handover.engineer_signature = signature_data
                handover.engineer_signed_date = datetime.utcnow()
            else:
                return jsonify({"error": "Invalid signature_type"}), 400
            
            return jsonify({
                "success": True,
                "message": f"{signature_type.capitalize()} signature added successfully"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>/approve', methods=['POST'])
@jwt_required()
def approve_handover( handover_id):
    """Approve handover record"""
    try:
        data = request.get_json()
        
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            handover.approval_status = 'approved'
            handover.status = 'approved'
            handover.approved_by = get_current_user_id()
            handover.approved_at = datetime.utcnow()
            
            if data.get('engineer_remarks'):
                handover.engineer_remarks = data['engineer_remarks']
            
            # TODO: Send notification
            # try:
            #     send_handover_notification(handover.id, 'approved')
            # except Exception as e:
            #     print(f"Failed to send notification: {e}")
            
            return jsonify({
                "success": True,
                "message": "Handover record approved successfully"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>/reject', methods=['POST'])
@jwt_required()
def reject_handover( handover_id):
    """Reject handover record"""
    try:
        data = request.get_json()
        rejection_reason = data.get('reason', '')
        
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            handover.approval_status = 'rejected'
            handover.status = 'rejected'
            handover.engineer_remarks = rejection_reason
            
            # TODO: Send notification
            # try:
            #     send_handover_notification(handover.id, 'rejected')
            # except Exception as e:
            #     print(f"Failed to send notification: {e}")
            
            return jsonify({
                "success": True,
                "message": "Handover record rejected"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/<int:handover_id>', methods=['DELETE'])
@jwt_required()
def delete_handover( handover_id):
    """Soft delete handover record"""
    try:
        with session_scope() as session:
            handover = session.query(HandoverRegister).filter_by(
                id=handover_id,
                is_deleted=False
            ).first()
            
            if not handover:
                return jsonify({"error": "Handover record not found"}), 404
            
            handover.is_deleted = True
            handover.updated_at = datetime.utcnow()
            
            return jsonify({
                "success": True,
                "message": "Handover record deleted successfully"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@handover_bp.route('/handover-register/categories', methods=['GET'])
@jwt_required()
def get_work_categories():
    """Get list of work categories"""
    categories = [
        'Structural Works',
        'MEP (Mechanical, Electrical, Plumbing)',
        'Finishing Works',
        'Flooring',
        'False Ceiling',
        'Painting',
        'Tiling',
        'Plastering',
        'Carpentry',
        'Glazing & Facades',
        'HVAC Systems',
        'Fire Fighting Systems',
        'Electrical Installation',
        'Plumbing & Sanitary',
        'Landscaping',
        'External Works',
        'Other'
    ]
    
    return jsonify({
        "success": True,
        "categories": categories
    }), 200
