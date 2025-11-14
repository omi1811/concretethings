"""
RMC Vendor Management API Blueprint

This module provides API endpoints for managing Ready Mix Concrete (RMC) vendors.
Implements quality approval workflow and vendor master data management.

Endpoints:
- GET    /api/vendors                - List approved vendors
- GET    /api/vendors/pending        - List pending approval vendors (QM only)
- GET    /api/vendors/:id            - Get vendor details
- POST   /api/vendors                - Create new vendor (requires quality team role)
- PUT    /api/vendors/:id            - Update vendor details
- PUT    /api/vendors/:id/approve    - Approve vendor (QM only)
- DELETE /api/vendors/:id            - Soft delete vendor (Admin only)

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps
import traceback

try:
    from .db import session_scope
    from .models import RMCVendor, User, Project, ProjectMembership
except ImportError:
    from db import session_scope
    from models import RMCVendor, User, Project, ProjectMembership


# Create Blueprint
vendors_bp = Blueprint('vendors', __name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Extract user_id from JWT identity (converts string to int)."""
    return int(get_jwt_identity())


# ============================================================================
# DECORATORS
# ============================================================================

def project_access_required(optional=False):
    """
    Decorator to check if user has access to the project.
    Expects 'project_id' in request JSON or query params.
    
    Args:
        optional: If True, allows requests without project_id (for listing all)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_current_user_id()
            
            # Get project_id from request
            if request.method == 'GET':
                project_id = request.args.get('project_id', type=int)
            else:
                data = request.get_json()
                project_id = data.get('project_id') if data else None
            
            # If optional and no project_id provided, allow through
            if optional and not project_id:
                return f(*args, **kwargs)
            
            if not project_id:
                return jsonify({"error": "project_id is required"}), 400
            
            # Check if user has access to this project
            with session_scope() as session:
                membership = session.query(ProjectMembership).filter_by(
                    user_id=user_id,
                    project_id=project_id
                ).first()
                
                if not membership:
                    return jsonify({"error": "Access denied. You are not a member of this project"}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def quality_team_required():
    """
    Decorator to check if user is part of quality team (QM or Quality Engineer).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_current_user_id()
            
            # Get project_id
            if request.method == 'GET':
                project_id = request.args.get('project_id', type=int)
            else:
                data = request.get_json()
                project_id = data.get('project_id') if data else None
            
            if not project_id:
                return jsonify({"error": "project_id is required"}), 400
            
            # Check user role
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
    return decorator


# ============================================================================
# API ENDPOINTS
# ============================================================================

@vendors_bp.route('/api/vendors', methods=['GET'])
@jwt_required()
@project_access_required(optional=True)
def get_vendors():
    """
    Get list of RMC vendors for a project or all projects.
    
    Query Parameters:
    - project_id (optional): Filter by project (if not provided, returns all vendors for user's company)
    - approved_only (optional): If true, return only approved vendors (default: true)
    
    Returns:
    - List of vendor objects
    """
    try:
        project_id = request.args.get('project_id', type=int)
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        user_id = get_current_user_id()
        
        with session_scope() as session:
            # Get user's company
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Base query - exclude soft deleted
            if project_id:
                # Filter by specific project
                query = session.query(RMCVendor).filter_by(
                    project_id=project_id,
                    is_deleted=False
                )
            else:
                # Get all vendors for user's company projects
                query = session.query(RMCVendor).join(Project).filter(
                    Project.company_id == user.company_id,
                    RMCVendor.is_deleted == False
                )
            
            # Filter by approval status
            if approved_only:
                query = query.filter_by(is_approved=True)
            
            vendors = query.order_by(RMCVendor.vendor_name).all()
            
            return jsonify({
                "success": True,
                "count": len(vendors),
                "vendors": [vendor.to_dict() for vendor in vendors]
            }), 200
    
    except Exception as e:
        print(f"Error fetching vendors: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch vendors: {str(e)}"}), 500


@vendors_bp.route('/api/vendors/pending', methods=['GET'])
@jwt_required()
@quality_team_required()
def get_pending_vendors():
    """
    Get list of vendors pending approval.
    Only accessible to Quality Managers and Quality Engineers.
    
    Query Parameters:
    - project_id (required): Filter by project
    
    Returns:
    - List of pending vendor objects
    """
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            vendors = session.query(RMCVendor).filter_by(
                project_id=project_id,
                is_approved=False,
                is_deleted=False
            ).order_by(RMCVendor.created_at.desc()).all()
            
            return jsonify({
                "success": True,
                "count": len(vendors),
                "vendors": [vendor.to_dict() for vendor in vendors]
            }), 200
    
    except Exception as e:
        print(f"Error fetching pending vendors: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch pending vendors: {str(e)}"}), 500


@vendors_bp.route('/api/vendors/<int:vendor_id>', methods=['GET'])
@jwt_required()
@project_access_required()
def get_vendor(vendor_id):
    """
    Get details of a specific vendor.
    
    Parameters:
    - vendor_id: Vendor ID
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Vendor object
    """
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            vendor = session.query(RMCVendor).filter_by(
                id=vendor_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            
            return jsonify({
                "success": True,
                "vendor": vendor.to_dict()
            }), 200
    
    except Exception as e:
        print(f"Error fetching vendor: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch vendor: {str(e)}"}), 500


@vendors_bp.route('/api/vendors', methods=['POST'])
@jwt_required()
@quality_team_required()
def create_vendor():
    """
    Create a new RMC vendor.
    Only accessible to Quality team members.
    
    Request Body:
    {
        "project_id": int (required),
        "vendor_name": str (required),
        "vendor_code": str (optional),
        "contact_person": str (optional),
        "phone": str (optional),
        "email": str (optional),
        "address": str (optional),
        "city": str (optional),
        "state": str (optional),
        "pincode": str (optional),
        "plant_location": str (optional),
        "iso_certification": str (optional),
        "quality_certificate_number": str (optional),
        "quality_certificate_valid_till": str (ISO date, optional)
    }
    
    Returns:
    - Created vendor object
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('vendor_name'):
            return jsonify({"error": "vendor_name is required"}), 400
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        # Check if project exists
        with session_scope() as session:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
        
        # Parse quality certificate validity date
        cert_valid_till = None
        if data.get('quality_certificate_valid_till'):
            try:
                cert_valid_till = datetime.fromisoformat(data['quality_certificate_valid_till'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format for quality_certificate_valid_till. Use ISO 8601 format"}), 400
        
        # Create vendor
        with session_scope() as session:
            vendor = RMCVendor(
                project_id=project_id,
                vendor_name=data['vendor_name'],
                vendor_code=data.get('vendor_code'),
                contact_person=data.get('contact_person'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                plant_location=data.get('plant_location'),
                iso_certification=data.get('iso_certification'),
                quality_certificate_number=data.get('quality_certificate_number'),
                quality_certificate_valid_till=cert_valid_till,
                is_approved=False,  # Requires approval
                created_by=user_id
            )
            
            session.add(vendor)
            session.flush()  # Get vendor ID
            
            vendor_dict = vendor.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Vendor created successfully. Pending approval.",
            "vendor": vendor_dict
        }), 201
    
    except Exception as e:
        print(f"Error creating vendor: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create vendor: {str(e)}"}), 500


@vendors_bp.route('/api/vendors/<int:vendor_id>', methods=['PUT'])
@jwt_required()
@quality_team_required()
def update_vendor(vendor_id):
    """
    Update vendor details.
    Only accessible to Quality team members.
    
    Parameters:
    - vendor_id: Vendor ID
    
    Request Body: Same as create_vendor (all fields optional)
    
    Returns:
    - Updated vendor object
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            vendor = session.query(RMCVendor).filter_by(
                id=vendor_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            
            # Update fields
            if 'vendor_name' in data:
                vendor.vendor_name = data['vendor_name']
            if 'vendor_code' in data:
                vendor.vendor_code = data['vendor_code']
            if 'contact_person' in data:
                vendor.contact_person = data['contact_person']
            if 'phone' in data:
                vendor.phone = data['phone']
            if 'email' in data:
                vendor.email = data['email']
            if 'address' in data:
                vendor.address = data['address']
            if 'city' in data:
                vendor.city = data['city']
            if 'state' in data:
                vendor.state = data['state']
            if 'pincode' in data:
                vendor.pincode = data['pincode']
            if 'plant_location' in data:
                vendor.plant_location = data['plant_location']
            if 'iso_certification' in data:
                vendor.iso_certification = data['iso_certification']
            if 'quality_certificate_number' in data:
                vendor.quality_certificate_number = data['quality_certificate_number']
            if 'quality_certificate_valid_till' in data:
                try:
                    vendor.quality_certificate_valid_till = datetime.fromisoformat(
                        data['quality_certificate_valid_till'].replace('Z', '+00:00')
                    )
                except ValueError:
                    return jsonify({"error": "Invalid date format for quality_certificate_valid_till"}), 400
            
            vendor.updated_at = datetime.utcnow()
            
            session.flush()
            vendor_dict = vendor.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Vendor updated successfully",
            "vendor": vendor_dict
        }), 200
    
    except Exception as e:
        print(f"Error updating vendor: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update vendor: {str(e)}"}), 500


@vendors_bp.route('/api/vendors/<int:vendor_id>/approve', methods=['PUT'])
@jwt_required()
@quality_team_required()
def approve_vendor(vendor_id):
    """
    Approve or reject a vendor.
    Only accessible to Quality Managers and Quality Engineers.
    
    Parameters:
    - vendor_id: Vendor ID
    
    Request Body:
    {
        "project_id": int (required),
        "approved": bool (required),
        "remarks": str (optional)
    }
    
    Returns:
    - Updated vendor object
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        if 'approved' not in data:
            return jsonify({"error": "approved field is required"}), 400
        
        approved = data['approved']
        remarks = data.get('remarks', '')
        
        with session_scope() as session:
            vendor = session.query(RMCVendor).filter_by(
                id=vendor_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            
            # Update approval status
            vendor.is_approved = approved
            vendor.approved_by = user_id
            vendor.approved_at = datetime.utcnow()
            vendor.approval_remarks = remarks
            vendor.updated_at = datetime.utcnow()
            
            session.flush()
            vendor_dict = vendor.to_dict()
        
        status_text = "approved" if approved else "rejected"
        return jsonify({
            "success": True,
            "message": f"Vendor {status_text} successfully",
            "vendor": vendor_dict
        }), 200
    
    except Exception as e:
        print(f"Error approving vendor: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to approve vendor: {str(e)}"}), 500


@vendors_bp.route('/api/vendors/<int:vendor_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required()
def delete_vendor(vendor_id):
    """
    Soft delete a vendor.
    Only accessible to Quality team members.
    
    Parameters:
    - vendor_id: Vendor ID
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Success message
    """
    try:
        user_id = get_jwt_identity()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            vendor = session.query(RMCVendor).filter_by(
                id=vendor_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            
            # Check if vendor is used in any batches
            # TODO: Add check when BatchRegister API is implemented
            # For now, allow deletion
            
            # Soft delete
            vendor.is_deleted = True
            vendor.deleted_at = datetime.utcnow()
            vendor.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Vendor deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting vendor: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete vendor: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@vendors_bp.route('/api/vendors/health', methods=['GET'])
def health_check():
    """Health check endpoint for vendor management API."""
    return jsonify({
        "status": "ok",
        "service": "RMC Vendor Management API",
        "version": "1.0.0"
    }), 200
