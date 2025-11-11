"""
Third-Party Lab API Blueprint

This module provides API endpoints for managing third-party testing laboratories.
Implements NABL accreditation tracking and quality approval workflow per ISO/IEC 17025:2017.

Endpoints:
- GET    /api/third-party-labs              - List approved labs
- GET    /api/third-party-labs/pending      - List pending approval labs (QM only)
- GET    /api/third-party-labs/:id          - Get lab details
- POST   /api/third-party-labs              - Create new lab (Quality team only)
- PUT    /api/third-party-labs/:id          - Update lab details
- PUT    /api/third-party-labs/:id/approve  - Approve/reject lab (QM only)
- DELETE /api/third-party-labs/:id          - Soft delete lab

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps
import traceback

try:
    from .db import session_scope
    from .models import ThirdPartyLab, Project, ProjectMembership, User
except ImportError:
    from db import session_scope
    from models import ThirdPartyLab, Project, ProjectMembership, User


# Create Blueprint
third_party_labs_bp = Blueprint('third_party_labs', __name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Extract user_id from JWT identity (converts string to int)."""
    return int(get_jwt_identity())





# ============================================================================
# DECORATORS
# ============================================================================

def project_access_required(f):
    """Decorator to check if user has access to the project."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
        else:
            data = request.get_json()
            project_id = data.get('project_id') if data else None
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "Access denied. You are not a member of this project"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def quality_team_required(f):
    """Decorator to check if user is part of quality team."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
        else:
            data = request.get_json()
            project_id = data.get('project_id') if data else None
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if not membership:
                return jsonify({"error": "Access denied"}), 403
            
            allowed_roles = ['Quality Manager', 'Quality Engineer']
            if membership.role not in allowed_roles:
                return jsonify({
                    "error": f"Access denied. Only {', '.join(allowed_roles)} can perform this action"
                }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# API ENDPOINTS
# ============================================================================

@third_party_labs_bp.route('/api/third-party-labs', methods=['GET'])
@jwt_required()
def get_labs():
    """
    Get list of third-party labs for a company.
    
    Query Parameters:
    - company_id (required): Filter by company
    - approved_only (optional): If true, return only approved labs (default: true)
    
    Returns:
    - List of lab objects
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
            
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        
        with session_scope() as session:
            query = session.query(ThirdPartyLab).filter_by(
                company_id=company_id,
                is_deleted=False
            )
            
            if approved_only:
                query = query.filter_by(is_approved=True)
            
            labs = query.order_by(ThirdPartyLab.lab_name).all()
            
            return jsonify({
                "success": True,
                "count": len(labs),
                "labs": [lab.to_dict() for lab in labs]
            }), 200
    
    except Exception as e:
        print(f"Error fetching labs: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch labs: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs/pending', methods=['GET'])
@jwt_required()
@quality_team_required
def get_pending_labs():
    """Get list of labs pending approval (QM only)."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            labs = session.query(ThirdPartyLab).filter_by(
                project_id=project_id,
                is_approved=False,
                is_deleted=False
            ).order_by(ThirdPartyLab.created_at.desc()).all()
            
            return jsonify({
                "success": True,
                "count": len(labs),
                "labs": [lab.to_dict() for lab in labs]
            }), 200
    
    except Exception as e:
        print(f"Error fetching pending labs: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch pending labs: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs/<int:lab_id>', methods=['GET'])
@jwt_required()
@project_access_required
def get_lab(lab_id):
    """Get details of a specific lab."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            lab = session.query(ThirdPartyLab).filter_by(
                id=lab_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not lab:
                return jsonify({"error": "Lab not found"}), 404
            
            lab_dict = lab.to_dict()
            
            # Add user names
            if lab.created_by:
                creator = session.query(User).filter_by(id=lab.created_by).first()
                lab_dict['created_by_name'] = creator.name if creator else None
            
            if lab.approved_by:
                approver = session.query(User).filter_by(id=lab.approved_by).first()
                lab_dict['approved_by_name'] = approver.name if approver else None
            
            return jsonify({
                "success": True,
                "lab": lab_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching lab: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch lab: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs', methods=['POST'])
@jwt_required()
@quality_team_required
def create_lab():
    """
    Create a new third-party lab.
    Only accessible to Quality team members.
    
    Request Body:
    {
        "project_id": int (required),
        "lab_name": str (required),
        "lab_code": str (optional),
        "contact_person": str (optional),
        "phone": str (optional),
        "email": str (optional),
        "address": str (optional),
        "city": str (optional),
        "state": str (optional),
        "pincode": str (optional),
        "nabl_accreditation_number": str (optional),
        "nabl_accreditation_valid_till": str (ISO date, optional),
        "scope_of_accreditation": str (optional)
    }
    
    Returns:
    - Created lab object
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('lab_name'):
            return jsonify({"error": "lab_name is required"}), 400
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        # Check if project exists
        with session_scope() as session:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
        
        # Parse NABL validity date
        nabl_valid_till = None
        if data.get('nabl_accreditation_valid_till'):
            try:
                nabl_valid_till = datetime.fromisoformat(data['nabl_accreditation_valid_till'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid nabl_accreditation_valid_till format. Use ISO 8601 format"}), 400
        
        # Create lab
        with session_scope() as session:
            lab = ThirdPartyLab(
                project_id=project_id,
                lab_name=data['lab_name'],
                lab_code=data.get('lab_code'),
                contact_person=data.get('contact_person'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                nabl_accreditation_number=data.get('nabl_accreditation_number'),
                nabl_accreditation_valid_till=nabl_valid_till,
                scope_of_accreditation=data.get('scope_of_accreditation'),
                is_approved=False,
                created_by=user_id
            )
            
            session.add(lab)
            session.flush()
            
            lab_dict = lab.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Lab created successfully. Pending approval.",
            "lab": lab_dict
        }), 201
    
    except Exception as e:
        print(f"Error creating lab: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create lab: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs/<int:lab_id>', methods=['PUT'])
@jwt_required()
@quality_team_required
def update_lab(lab_id):
    """
    Update lab details.
    Only accessible to Quality team members.
    """
    try:
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            lab = session.query(ThirdPartyLab).filter_by(
                id=lab_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not lab:
                return jsonify({"error": "Lab not found"}), 404
            
            # Update fields
            if 'lab_name' in data:
                lab.lab_name = data['lab_name']
            if 'lab_code' in data:
                lab.lab_code = data['lab_code']
            if 'contact_person' in data:
                lab.contact_person = data['contact_person']
            if 'phone' in data:
                lab.phone = data['phone']
            if 'email' in data:
                lab.email = data['email']
            if 'address' in data:
                lab.address = data['address']
            if 'city' in data:
                lab.city = data['city']
            if 'state' in data:
                lab.state = data['state']
            if 'pincode' in data:
                lab.pincode = data['pincode']
            if 'nabl_accreditation_number' in data:
                lab.nabl_accreditation_number = data['nabl_accreditation_number']
            if 'nabl_accreditation_valid_till' in data:
                try:
                    lab.nabl_accreditation_valid_till = datetime.fromisoformat(
                        data['nabl_accreditation_valid_till'].replace('Z', '+00:00')
                    )
                except ValueError:
                    return jsonify({"error": "Invalid nabl_accreditation_valid_till format"}), 400
            if 'scope_of_accreditation' in data:
                lab.scope_of_accreditation = data['scope_of_accreditation']
            
            lab.updated_at = datetime.utcnow()
            
            session.flush()
            lab_dict = lab.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Lab updated successfully",
            "lab": lab_dict
        }), 200
    
    except Exception as e:
        print(f"Error updating lab: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update lab: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs/<int:lab_id>/approve', methods=['PUT'])
@jwt_required()
@quality_team_required
def approve_lab(lab_id):
    """
    Approve or reject a lab.
    Only accessible to Quality Managers and Quality Engineers.
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        if 'approved' not in data:
            return jsonify({"error": "approved field is required"}), 400
        
        approved = data['approved']
        remarks = data.get('remarks', '')
        
        with session_scope() as session:
            lab = session.query(ThirdPartyLab).filter_by(
                id=lab_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not lab:
                return jsonify({"error": "Lab not found"}), 404
            
            # Update approval status
            lab.is_approved = approved
            lab.approved_by = user_id
            lab.approved_at = datetime.utcnow()
            lab.approval_remarks = remarks
            lab.updated_at = datetime.utcnow()
            
            session.flush()
            lab_dict = lab.to_dict()
        
        status_text = "approved" if approved else "rejected"
        return jsonify({
            "success": True,
            "message": f"Lab {status_text} successfully",
            "lab": lab_dict
        }), 200
    
    except Exception as e:
        print(f"Error approving lab: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to approve lab: {str(e)}"}), 500


@third_party_labs_bp.route('/api/third-party-labs/<int:lab_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required
def delete_lab(lab_id):
    """
    Soft delete a lab.
    Only accessible to Quality team members.
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            lab = session.query(ThirdPartyLab).filter_by(
                id=lab_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not lab:
                return jsonify({"error": "Lab not found"}), 404
            
            # Soft delete
            lab.is_deleted = True
            lab.deleted_at = datetime.utcnow()
            lab.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Lab deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting lab: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete lab: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@third_party_labs_bp.route('/api/third-party-labs/health', methods=['GET'])
def health_check():
    """Health check endpoint for third-party lab API."""
    return jsonify({
        "status": "ok",
        "service": "Third-Party Lab API",
        "version": "1.0.0",
        "compliance": "ISO/IEC 17025:2017"
    }), 200
