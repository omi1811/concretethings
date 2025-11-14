"""
Batch Register API Blueprint

This module provides API endpoints for managing concrete batch registers.
Each batch represents a concrete delivery from an RMC vendor with mandatory photo documentation.

Endpoints:
- GET    /api/batches                - List batches for a project
- GET    /api/batches/:id            - Get batch details
- GET    /api/batches/:id/photo      - Get batch sheet photo
- POST   /api/batches                - Create new batch with photo upload
- PUT    /api/batches/:id            - Update batch details
- PUT    /api/batches/:id/verify     - Verify/reject batch (QM only)
- DELETE /api/batches/:id            - Soft delete batch

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps
from io import BytesIO
import traceback

try:
    from .db import session_scope
    from .models import BatchRegister, RMCVendor, Project, ProjectMembership, MixDesign, User
    from .email_notifications import notify_batch_rejection_email
except ImportError:
    from db import session_scope
    from models import BatchRegister, RMCVendor, Project, ProjectMembership, MixDesign, User
    from email_notifications import notify_batch_rejection_email


# Create Blueprint
batches_bp = Blueprint('batches', __name__)


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
                data = request.get_json() if request.is_json else None
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


def quality_team_required(f):
    """
    Decorator to check if user is part of quality team (QM or Quality Engineer).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        # Get project_id
        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
        else:
            data = request.get_json() if request.is_json else None
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


# ============================================================================
# API ENDPOINTS
# ============================================================================

@batches_bp.route('/api/batches', methods=['GET'])
@jwt_required()
@project_access_required(optional=True)
def get_batches():
    """
    Get list of batches for a project or all projects.
    
    Query Parameters:
    - project_id (optional): Filter by project (if not provided, returns all batches for user's company)
    - vendor_id (optional): Filter by vendor
    - mix_design_id (optional): Filter by mix design
    - status (optional): Filter by verification status (pending/approved/rejected)
    - date_from (optional): Filter by date range (ISO format)
    - date_to (optional): Filter by date range (ISO format)
    
    Returns:
    - List of batch objects
    """
    try:
        project_id = request.args.get('project_id', type=int)
        vendor_id = request.args.get('vendor_id', type=int)
        mix_design_id = request.args.get('mix_design_id', type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        user_id = get_current_user_id()
        
        with session_scope() as session:
            # Get user's company
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Base query - exclude soft deleted
            if project_id:
                # Filter by specific project
                query = session.query(BatchRegister).filter_by(
                    project_id=project_id,
                    is_deleted=False
                )
            else:
                # Get all batches for user's company projects
                query = session.query(BatchRegister).join(Project).filter(
                    Project.company_id == user.company_id,
                    BatchRegister.is_deleted == False
                )
            
            # Apply filters
            if vendor_id:
                query = query.filter_by(vendor_id=vendor_id)
            if mix_design_id:
                query = query.filter_by(mix_design_id=mix_design_id)
            if status:
                query = query.filter_by(verification_status=status)
            
            # Date range filter
            if date_from:
                try:
                    date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(BatchRegister.delivery_date >= date_from_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_from format. Use ISO 8601 format"}), 400
            
            if date_to:
                try:
                    date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(BatchRegister.delivery_date <= date_to_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_to format. Use ISO 8601 format"}), 400
            
            batches = query.order_by(BatchRegister.delivery_date.desc()).all()
            
            # Enrich with vendor and mix design names
            result = []
            for batch in batches:
                batch_dict = batch.to_dict()
                
                # Add vendor name
                if batch.vendor_id:
                    vendor = session.query(RMCVendor).filter_by(id=batch.vendor_id).first()
                    batch_dict['vendor_name'] = vendor.vendor_name if vendor else None
                
                # Add mix design name
                if batch.mix_design_id:
                    mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                    batch_dict['mix_design_name'] = mix.name if mix else None
                
                result.append(batch_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "batches": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching batches: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch batches: {str(e)}"}), 500


@batches_bp.route('/api/batches/<int:batch_id>', methods=['GET'])
@jwt_required()
@project_access_required()
def get_batch(batch_id):
    """
    Get details of a specific batch.
    
    Parameters:
    - batch_id: Batch ID
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Batch object with enriched data
    """
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            batch_dict = batch.to_dict()
            
            # Add vendor details
            if batch.vendor_id:
                vendor = session.query(RMCVendor).filter_by(id=batch.vendor_id).first()
                if vendor:
                    batch_dict['vendor'] = {
                        'id': vendor.id,
                        'name': vendor.vendor_name,
                        'plant_location': vendor.plant_location
                    }
            
            # Add mix design details
            if batch.mix_design_id:
                mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                if mix:
                    batch_dict['mix_design'] = {
                        'id': mix.id,
                        'name': mix.name,
                        'grade': mix.grade,
                        'type': mix.type
                    }
            
            # Add created/verified by user names
            if batch.created_by:
                creator = session.query(User).filter_by(id=batch.created_by).first()
                batch_dict['created_by_name'] = creator.name if creator else None
            
            if batch.verified_by:
                verifier = session.query(User).filter_by(id=batch.verified_by).first()
                batch_dict['verified_by_name'] = verifier.name if verifier else None
            
            return jsonify({
                "success": True,
                "batch": batch_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch batch: {str(e)}"}), 500


@batches_bp.route('/api/batches/<int:batch_id>/photo', methods=['GET'])
@jwt_required()
@project_access_required()
def get_batch_photo(batch_id):
    """
    Get batch sheet photo.
    
    Parameters:
    - batch_id: Batch ID
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Image file
    """
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            if not batch.batch_sheet_photo_data:
                return jsonify({"error": "No photo available for this batch"}), 404
            
            # Send photo as file
            return send_file(
                BytesIO(batch.batch_sheet_photo_data),
                mimetype=batch.batch_sheet_photo_mimetype or 'image/jpeg',
                as_attachment=False,
                download_name=batch.batch_sheet_photo_name or f'batch_{batch_id}.jpg'
            )
    
    except Exception as e:
        print(f"Error fetching batch photo: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch batch photo: {str(e)}"}), 500


@batches_bp.route('/api/batches', methods=['POST'])
@jwt_required()
@project_access_required()
def create_batch():
    """
    Create a new batch with mandatory photo upload.
    
    Request: multipart/form-data
    - project_id (required): int
    - vendor_id (required): int
    - mix_design_id (required): int
    - batch_number (required): string (unique per project)
    - delivery_date (required): ISO date
    - delivery_time (optional): string (HH:MM)
    - quantity_delivered (required): float (cubic meters)
    - vehicle_number (required): string
    - driver_name (optional): string
    - driver_phone (optional): string
    - location_description (required): string (where concrete is poured)
    - floor_level (optional): string
    - structural_element (optional): string (e.g., "Column", "Beam", "Slab")
    - element_id (optional): string (e.g., "C1", "B12", "S3")
    - weather_condition (optional): string
    - ambient_temperature (optional): float
    - slump_value (optional): float
    - batch_sheet_photo (required): file upload
    
    Returns:
    - Created batch object
    """
    try:
        user_id = get_current_user_id()
        
        # Validate multipart/form-data
        if 'batch_sheet_photo' not in request.files:
            return jsonify({"error": "batch_sheet_photo is required"}), 400
        
        photo_file = request.files['batch_sheet_photo']
        if photo_file.filename == '':
            return jsonify({"error": "No photo file selected"}), 400
        
        # Validate required fields
        required_fields = ['project_id', 'vendor_id', 'mix_design_id', 'batch_number', 
                          'delivery_date', 'quantity_delivered', 'vehicle_number', 'location_description']
        
        for field in required_fields:
            if field not in request.form:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Parse form data
        project_id = int(request.form['project_id'])
        vendor_id = int(request.form['vendor_id'])
        mix_design_id = int(request.form['mix_design_id'])
        batch_number = request.form['batch_number']
        quantity_delivered = float(request.form['quantity_delivered'])
        vehicle_number = request.form['vehicle_number']
        location_description = request.form['location_description']
        
        # Parse delivery date
        try:
            delivery_date = datetime.fromisoformat(request.form['delivery_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid delivery_date format. Use ISO 8601 format"}), 400
        
        # Optional fields
        delivery_time = request.form.get('delivery_time')
        driver_name = request.form.get('driver_name')
        driver_phone = request.form.get('driver_phone')
        floor_level = request.form.get('floor_level')
        structural_element = request.form.get('structural_element')
        element_id = request.form.get('element_id')
        weather_condition = request.form.get('weather_condition')
        ambient_temperature = float(request.form['ambient_temperature']) if request.form.get('ambient_temperature') else None
        slump_value = float(request.form['slump_value']) if request.form.get('slump_value') else None
        
        # Validate vendor and mix design exist and are approved
        with session_scope() as session:
            # Check project exists
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
            
            # Check vendor exists and is approved
            vendor = session.query(RMCVendor).filter_by(
                id=vendor_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            if not vendor.is_approved:
                return jsonify({"error": "Vendor is not approved. Cannot create batch."}), 400
            
            # Check mix design exists
            mix = session.query(MixDesign).filter_by(id=mix_design_id).first()
            if not mix:
                return jsonify({"error": "Mix design not found"}), 404
            
            # Check batch number uniqueness
            existing = session.query(BatchRegister).filter_by(
                project_id=project_id,
                batch_number=batch_number,
                is_deleted=False
            ).first()
            if existing:
                return jsonify({"error": f"Batch number '{batch_number}' already exists for this project"}), 400
            
            # Read photo data
            photo_data = photo_file.read()
            photo_name = photo_file.filename
            photo_mimetype = photo_file.mimetype or 'image/jpeg'
            
            # Validate photo size (max 10MB)
            if len(photo_data) > 10 * 1024 * 1024:
                return jsonify({"error": "Photo size exceeds 10MB limit"}), 400
            
            # Create batch
            batch = BatchRegister(
                project_id=project_id,
                vendor_id=vendor_id,
                mix_design_id=mix_design_id,
                batch_number=batch_number,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                quantity_delivered=quantity_delivered,
                vehicle_number=vehicle_number,
                driver_name=driver_name,
                driver_phone=driver_phone,
                location_description=location_description,
                floor_level=floor_level,
                structural_element=structural_element,
                element_id=element_id,
                weather_condition=weather_condition,
                ambient_temperature=ambient_temperature,
                slump_value=slump_value,
                batch_sheet_photo_name=photo_name,
                batch_sheet_photo_data=photo_data,
                batch_sheet_photo_mimetype=photo_mimetype,
                verification_status='pending',
                created_by=user_id
            )
            
            session.add(batch)
            session.flush()
            
            batch_dict = batch.to_dict()
            batch_dict['vendor_name'] = vendor.vendor_name
            batch_dict['mix_design_name'] = mix.name
        
        return jsonify({
            "success": True,
            "message": "Batch created successfully. Pending verification.",
            "batch": batch_dict
        }), 201
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create batch: {str(e)}"}), 500


@batches_bp.route('/api/batches/<int:batch_id>', methods=['PUT'])
@jwt_required()
@project_access_required()
def update_batch(batch_id):
    """
    Update batch details.
    Can only update if status is 'pending'.
    
    Parameters:
    - batch_id: Batch ID
    
    Request: multipart/form-data (same as create, all fields optional)
    
    Returns:
    - Updated batch object
    """
    try:
        user_id = get_current_user_id()
        project_id = int(request.form.get('project_id')) if request.form.get('project_id') else None
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Check if batch can be updated
            if batch.verification_status in ['approved', 'rejected']:
                return jsonify({"error": f"Cannot update batch with status '{batch.verification_status}'"}), 400
            
            # Update fields if provided
            if request.form.get('vendor_id'):
                vendor_id = int(request.form['vendor_id'])
                vendor = session.query(RMCVendor).filter_by(
                    id=vendor_id,
                    project_id=project_id,
                    is_deleted=False,
                    is_approved=True
                ).first()
                if not vendor:
                    return jsonify({"error": "Vendor not found or not approved"}), 404
                batch.vendor_id = vendor_id
            
            if request.form.get('mix_design_id'):
                mix_design_id = int(request.form['mix_design_id'])
                mix = session.query(MixDesign).filter_by(id=mix_design_id).first()
                if not mix:
                    return jsonify({"error": "Mix design not found"}), 404
                batch.mix_design_id = mix_design_id
            
            if request.form.get('batch_number'):
                batch_number = request.form['batch_number']
                # Check uniqueness
                existing = session.query(BatchRegister).filter(
                    BatchRegister.project_id == project_id,
                    BatchRegister.batch_number == batch_number,
                    BatchRegister.id != batch_id,
                    BatchRegister.is_deleted == False
                ).first()
                if existing:
                    return jsonify({"error": f"Batch number '{batch_number}' already exists"}), 400
                batch.batch_number = batch_number
            
            if request.form.get('delivery_date'):
                try:
                    batch.delivery_date = datetime.fromisoformat(request.form['delivery_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid delivery_date format"}), 400
            
            if request.form.get('delivery_time'):
                batch.delivery_time = request.form['delivery_time']
            
            if request.form.get('quantity_delivered'):
                batch.quantity_delivered = float(request.form['quantity_delivered'])
            
            if request.form.get('vehicle_number'):
                batch.vehicle_number = request.form['vehicle_number']
            
            if request.form.get('driver_name'):
                batch.driver_name = request.form['driver_name']
            
            if request.form.get('driver_phone'):
                batch.driver_phone = request.form['driver_phone']
            
            if request.form.get('location_description'):
                batch.location_description = request.form['location_description']
            
            if request.form.get('floor_level'):
                batch.floor_level = request.form['floor_level']
            
            if request.form.get('structural_element'):
                batch.structural_element = request.form['structural_element']
            
            if request.form.get('element_id'):
                batch.element_id = request.form['element_id']
            
            if request.form.get('weather_condition'):
                batch.weather_condition = request.form['weather_condition']
            
            if request.form.get('ambient_temperature'):
                batch.ambient_temperature = float(request.form['ambient_temperature'])
            
            if request.form.get('slump_value'):
                batch.slump_value = float(request.form['slump_value'])
            
            # Update photo if provided
            if 'batch_sheet_photo' in request.files:
                photo_file = request.files['batch_sheet_photo']
                if photo_file.filename != '':
                    photo_data = photo_file.read()
                    if len(photo_data) > 10 * 1024 * 1024:
                        return jsonify({"error": "Photo size exceeds 10MB limit"}), 400
                    
                    batch.batch_sheet_photo_name = photo_file.filename
                    batch.batch_sheet_photo_data = photo_data
                    batch.batch_sheet_photo_mimetype = photo_file.mimetype or 'image/jpeg'
            
            batch.updated_at = datetime.utcnow()
            session.flush()
            
            batch_dict = batch.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Batch updated successfully",
            "batch": batch_dict
        }), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error updating batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update batch: {str(e)}"}), 500


@batches_bp.route('/api/batches/<int:batch_id>/verify', methods=['PUT'])
@jwt_required()
@quality_team_required
def verify_batch(batch_id):
    """
    Verify or reject a batch.
    Only accessible to Quality Managers and Quality Engineers.
    Sends email notification on rejection.
    
    Parameters:
    - batch_id: Batch ID
    
    Request Body:
    {
        "project_id": int (required),
        "status": "approved" | "rejected" (required),
        "remarks": str (optional)
    }
    
    Returns:
    - Updated batch object
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        if 'status' not in data:
            return jsonify({"error": "status field is required"}), 400
        
        status = data['status']
        if status not in ['approved', 'rejected']:
            return jsonify({"error": "status must be 'approved' or 'rejected'"}), 400
        
        remarks = data.get('remarks', '')
        
        with session_scope() as session:
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Update verification status
            batch.verification_status = status
            batch.verified_by = user_id
            batch.verified_at = datetime.utcnow()
            batch.verification_remarks = remarks
            batch.updated_at = datetime.utcnow()
            
            session.flush()
            
            # Get enriched data for email
            vendor = session.query(RMCVendor).filter_by(id=batch.vendor_id).first()
            mix_design = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
            project = session.query(Project).filter_by(id=project_id).first()
            verifier = session.query(User).filter_by(id=user_id).first()
            
            batch_dict = batch.to_dict()
            batch_dict['vendor_name'] = vendor.vendor_name if vendor else None
            batch_dict['mix_design_name'] = mix_design.name if mix_design else None
        
        # Send email notification on rejection
        if status == 'rejected':
            try:
                notify_batch_rejection_email(
                    batch_id=batch_id,
                    batch_number=batch.batch_number,
                    vendor_email=vendor.email if vendor and vendor.email else None,
                    vendor_name=vendor.vendor_name if vendor else "Unknown Vendor",
                    project_name=project.name if project else "Unknown Project",
                    delivery_date=batch.delivery_date.strftime("%Y-%m-%d"),
                    rejection_reason=remarks,
                    verifier_name=verifier.name if verifier else "Quality Team"
                )
            except Exception as email_error:
                print(f"Warning: Failed to send rejection email: {str(email_error)}")
                # Don't fail the verification if email fails
        
        return jsonify({
            "success": True,
            "message": f"Batch {status} successfully",
            "batch": batch_dict
        }), 200
    
    except Exception as e:
        print(f"Error verifying batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to verify batch: {str(e)}"}), 500


@batches_bp.route('/api/batches/<int:batch_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required
def delete_batch(batch_id):
    """
    Soft delete a batch.
    Only accessible to Quality team members.
    
    Parameters:
    - batch_id: Batch ID
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Success message
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Soft delete
            batch.is_deleted = True
            batch.deleted_at = datetime.utcnow()
            batch.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Batch deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete batch: {str(e)}"}), 500


# ============================================================================
# BATCH COMPLETION & CUBE CASTING WORKFLOW
# ============================================================================

@batches_bp.route('/api/batches/<int:batch_id>/complete', methods=['POST'])
@jwt_required()
@project_access_required()
def complete_batch(batch_id):
    """
    Mark batch as complete and return summary for cube casting workflow.
    
    This endpoint:
    - Returns batch summary with vehicle count, location details
    - Provides recommendations for cube sets based on volume
    - Used to trigger cube casting modal on frontend
    
    Query Parameters:
    - project_id (required): For access control
    
    Returns:
    - Batch summary with recommendations for cube sets
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            # Get batch with related data
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Get mix design for strength requirements
            mix_design = session.query(MixDesign).filter_by(
                id=batch.mix_design_id
            ).first()
            
            # Get RMC vendor details
            vendor = session.query(RMCVendor).filter_by(
                id=batch.rmc_vendor_id
            ).first()
            
            # Calculate recommended number of cube sets based on volume
            # IS 456:2000 recommends:
            # - 1 set for every 5 m³ or part thereof
            # - Minimum 1 set per day
            quantity = batch.quantity_received or batch.quantity_ordered
            recommended_sets = max(1, int((quantity / 5.0) + 0.9))  # Round up
            
            # Prepare batch summary
            summary = {
                "batchId": batch.id,
                "batchNumber": batch.batch_number,
                "deliveryDate": batch.delivery_date.isoformat(),
                "quantityOrdered": batch.quantity_ordered,
                "quantityReceived": batch.quantity_received,
                "vehicleNumber": batch.vehicle_number,
                "location": {
                    "buildingName": batch.building_name,
                    "floorLevel": batch.floor_level,
                    "zone": batch.zone,
                    "structuralElementType": batch.structural_element_type,
                    "elementId": batch.element_id,
                    "description": batch.pour_location_description
                },
                "mixDesign": {
                    "id": mix_design.id if mix_design else None,
                    "mixDesignId": mix_design.mix_design_id if mix_design else None,
                    "specifiedStrengthPsi": mix_design.specified_strength_psi if mix_design else None,
                    "specifiedStrengthMpa": round(mix_design.specified_strength_psi * 0.00689476, 2) if mix_design and mix_design.specified_strength_psi else None
                },
                "vendor": {
                    "id": vendor.id if vendor else None,
                    "name": vendor.vendor_name if vendor else None
                },
                "recommendations": {
                    "recommendedSets": recommended_sets,
                    "reason": f"Based on {quantity} m³ volume (IS 456:2000: 1 set per 5 m³)",
                    "standardTestAges": [3, 7, 28, 56],
                    "cubesPerSet": 3,
                    "cubeNames": ["A", "B", "C"]
                }
            }
            
            return jsonify({
                "success": True,
                "batch": summary
            }), 200
    
    except Exception as e:
        print(f"Error completing batch: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to complete batch: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@batches_bp.route('/api/batches/health', methods=['GET'])
def health_check():
    """Health check endpoint for batch management API."""
    return jsonify({
        "status": "ok",
        "service": "Batch Register API",
        "version": "1.0.0"
    }), 200
