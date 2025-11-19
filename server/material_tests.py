"""
Material Test Register API Blueprint

This module provides API endpoints for managing material testing records.
Supports flexible JSON-based test parameters for any material type (steel, glass, railing, etc.).

Endpoints:
- GET    /api/material-tests              - List material tests
- GET    /api/material-tests/:id          - Get test details
- GET    /api/material-tests/:id/certificate - Get test certificate photo
- POST   /api/material-tests              - Create test with certificate
- PUT    /api/material-tests/:id          - Update test details
- PUT    /api/material-tests/:id/verify   - Verify test (QM only)
- DELETE /api/material-tests/:id          - Soft delete test

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps
from io import BytesIO
import json
import traceback

try:
    from .db import session_scope
    from .models import (MaterialTestRegister, MaterialCategory, ApprovedBrand, 
                        Project, ProjectMembership, User)
    from .email_notifications import EmailService
except ImportError:
    from db import session_scope
    from models import (MaterialTestRegister, MaterialCategory, ApprovedBrand, 
                       Project, ProjectMembership, User)
    from email_notifications import EmailService


# Create Blueprint
material_tests_bp = Blueprint('material_tests', __name__)

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
            if request.content_type and 'multipart/form-data' in request.content_type:
                project_id = int(request.form.get('project_id')) if request.form.get('project_id') else None
            else:
                data = request.get_json() if request.is_json else None
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
            data = request.get_json() if request.is_json else None
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
# HELPER FUNCTIONS
# ============================================================================

def generate_ncr_number(project_id: int, test_id: int) -> str:
    """Generate NCR number for material test."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"NCR-P{project_id}-MT{test_id}-{timestamp}"


def send_material_test_failure_email(test_data: dict) -> bool:
    """Send email notification for material test failure."""
    try:
        email_service = EmailService()
        if not email_service.enabled:
            return False
        
        subject = f"⚠️ Material Test Failed - {test_data.get('material_description')} | {test_data.get('project_name')}"
        
        # HTML body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: white; padding: 30px; }}
                .test-info {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .failure-info {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; }}
                .label {{ font-weight: bold; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ Material Test Failed</h2>
                </div>
                <div class="content">
                    <div class="test-info">
                        <div><span class="label">Material:</span> {test_data.get('material_description')}</div>
                        <div><span class="label">Brand:</span> {test_data.get('brand_name')}</div>
                        <div><span class="label">Grade:</span> {test_data.get('grade_specification')}</div>
                        <div><span class="label">Supplier:</span> {test_data.get('supplier_name')}</div>
                        <div><span class="label">Project:</span> {test_data.get('project_name')}</div>
                        <div><span class="label">NCR Number:</span> {test_data.get('ncr_number')}</div>
                    </div>
                    
                    <div class="failure-info">
                        <div class="label">Test Status: FAILED</div>
                        <p>The material has failed quality testing and cannot be used in construction.</p>
                    </div>
                    
                    <h3>Required Actions:</h3>
                    <ol>
                        <li>Quarantine the failed material immediately</li>
                        <li>Notify the supplier about the non-conformance</li>
                        <li>Arrange for replacement material</li>
                        <li>Update NCR register and track corrective actions</li>
                    </ol>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        ⚠️ MATERIAL TEST FAILED
        
        Material: {test_data.get('material_description')}
        Brand: {test_data.get('brand_name')}
        Grade: {test_data.get('grade_specification')}
        Supplier: {test_data.get('supplier_name')}
        Project: {test_data.get('project_name')}
        NCR Number: {test_data.get('ncr_number')}
        
        Test Status: FAILED
        
        Required Actions:
        1. Quarantine the failed material immediately
        2. Notify the supplier about the non-conformance
        3. Arrange for replacement material
        4. Update NCR register and track corrective actions
        """
        
        # Send to supplier if email provided
        if test_data.get('supplier_email'):
            return email_service.send_email(
                test_data['supplier_email'],
                subject,
                html_body,
                text_body
            )
        
        return False
    
    except Exception as e:
        print(f"Error sending material test failure email: {str(e)}")
        return False


# ============================================================================
# API ENDPOINTS
# ============================================================================

@material_tests_bp.route('/api/material-tests', methods=['GET'])
@jwt_required()
@project_access_required
def get_material_tests():
    """
    Get list of material tests.
    
    Query Parameters:
    - project_id (required): Filter by project
    - category_id (optional): Filter by material category
    - brand_id (optional): Filter by approved brand
    - status (optional): Filter by pass/fail status
    """
    try:
        project_id = request.args.get('project_id', type=int)
        category_id = request.args.get('category_id', type=int)
        brand_id = request.args.get('brand_id', type=int)
        status = request.args.get('status')
        
        with session_scope() as session:
            query = session.query(MaterialTestRegister).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            if category_id:
                query = query.filter_by(material_category_id=category_id)
            if brand_id:
                query = query.filter_by(approved_brand_id=brand_id)
            if status:
                query = query.filter_by(pass_fail_status=status)
            
            tests = query.order_by(MaterialTestRegister.created_at.desc()).all()
            
            # Enrich with related data
            result = []
            for test in tests:
                test_dict = test.to_dict()
                
                # Parse JSON fields
                if test.test_parameters:
                    test_dict['test_parameters'] = json.loads(test.test_parameters) if isinstance(test.test_parameters, str) else test.test_parameters
                if test.test_results:
                    test_dict['test_results'] = json.loads(test.test_results) if isinstance(test.test_results, str) else test.test_results
                
                # Add category name
                if test.material_category_id:
                    category = session.query(MaterialCategory).filter_by(id=test.material_category_id).first()
                    test_dict['category_name'] = category.category_name if category else None
                
                # Add brand name
                if test.approved_brand_id:
                    brand = session.query(ApprovedBrand).filter_by(id=test.approved_brand_id).first()
                    test_dict['brand_name'] = brand.brand_name if brand else None
                
                result.append(test_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "tests": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching material tests: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch tests: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests/<int:test_id>', methods=['GET'])
@jwt_required()
@project_access_required
def get_material_test(test_id):
    """Get details of a specific material test."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            test = session.query(MaterialTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            test_dict = test.to_dict()
            
            # Parse JSON fields
            if test.test_parameters:
                test_dict['test_parameters'] = json.loads(test.test_parameters) if isinstance(test.test_parameters, str) else test.test_parameters
            if test.test_results:
                test_dict['test_results'] = json.loads(test.test_results) if isinstance(test.test_results, str) else test.test_results
            
            # Add category details
            if test.material_category_id:
                category = session.query(MaterialCategory).filter_by(id=test.material_category_id).first()
                if category:
                    test_dict['category'] = {
                        'id': category.id,
                        'name': category.category_name,
                        'standards': category.applicable_standards
                    }
            
            # Add brand details
            if test.approved_brand_id:
                brand = session.query(ApprovedBrand).filter_by(id=test.approved_brand_id).first()
                if brand:
                    test_dict['brand'] = {
                        'id': brand.id,
                        'name': brand.brand_name,
                        'manufacturer': brand.manufacturer_name
                    }
            
            # Add user names
            if test.entered_by:
                enterer = session.query(User).filter_by(id=test.entered_by).first()
                test_dict['entered_by_name'] = enterer.full_name if enterer else None
            
            if test.verified_by:
                verifier = session.query(User).filter_by(id=test.verified_by).first()
                test_dict['verified_by_name'] = verifier.full_name if verifier else None
            
            return jsonify({
                "success": True,
                "test": test_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching material test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch test: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests/<int:test_id>/certificate', methods=['GET'])
@jwt_required()
@project_access_required
def get_test_certificate(test_id):
    """Get test certificate photo."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            test = session.query(MaterialTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            if not test.certificate_photo_data:
                return jsonify({"error": "No certificate available"}), 404
            
            return send_file(
                BytesIO(test.certificate_photo_data),
                mimetype=test.certificate_photo_mimetype or 'image/jpeg',
                as_attachment=False,
                download_name=test.certificate_photo_name or f'certificate_{test_id}.jpg'
            )
    
    except Exception as e:
        print(f"Error fetching certificate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch certificate: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests', methods=['POST'])
@jwt_required()
@project_access_required
def create_material_test():
    """
    Create new material test with certificate.
    Supports flexible JSON test parameters for any material type.
    
    Request: multipart/form-data
    - project_id (required): int
    - material_category_id (required): int
    - approved_brand_id (required): int
    - material_description (required): string
    - grade_specification (optional): string
    - quantity (required): float
    - quantity_unit (required): string (e.g., "kg", "m", "nos")
    - supplier_name (required): string
    - supplier_email (optional): string
    - manufacturer_name (optional): string
    - batch_lot_number (optional): string
    - invoice_number (optional): string
    - invoice_date (optional): ISO date
    - location_description (required): string (where material is used)
    - lab_test_report_number (optional): string
    - test_parameters (required): JSON string
    - test_results (required): JSON string
    - pass_fail_status (required): "pass" | "fail"
    - remarks (optional): string
    - certificate_photo (required): file upload
    
    Returns:
    - Created test object
    """
    try:
        user_id = get_current_user_id()
        
        # Validate certificate photo
        if 'certificate_photo' not in request.files:
            return jsonify({"error": "certificate_photo is required"}), 400
        
        photo_file = request.files['certificate_photo']
        if photo_file.filename == '':
            return jsonify({"error": "No certificate photo selected"}), 400
        
        # Validate required fields
        required_fields = ['project_id', 'material_category_id', 'approved_brand_id',
                          'material_description', 'quantity', 'quantity_unit',
                          'supplier_name', 'location_description', 'test_parameters',
                          'test_results', 'pass_fail_status']
        
        for field in required_fields:
            if field not in request.form:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Parse form data
        project_id = int(request.form['project_id'])
        material_category_id = int(request.form['material_category_id'])
        approved_brand_id = int(request.form['approved_brand_id'])
        material_description = request.form['material_description']
        grade_specification = request.form.get('grade_specification')
        quantity = float(request.form['quantity'])
        quantity_unit = request.form['quantity_unit']
        supplier_name = request.form['supplier_name']
        supplier_email = request.form.get('supplier_email')
        manufacturer_name = request.form.get('manufacturer_name')
        batch_lot_number = request.form.get('batch_lot_number')
        invoice_number = request.form.get('invoice_number')
        location_description = request.form['location_description']
        lab_test_report_number = request.form.get('lab_test_report_number')
        pass_fail_status = request.form['pass_fail_status']
        remarks = request.form.get('remarks')
        
        # Parse JSON fields
        try:
            test_parameters = json.loads(request.form['test_parameters'])
            test_results = json.loads(request.form['test_results'])
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for test_parameters or test_results"}), 400
        
        # Validate pass_fail_status
        if pass_fail_status not in ['pass', 'fail']:
            return jsonify({"error": "pass_fail_status must be 'pass' or 'fail'"}), 400
        
        # Parse invoice date
        invoice_date = None
        if request.form.get('invoice_date'):
            try:
                invoice_date = datetime.fromisoformat(request.form['invoice_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid invoice_date format"}), 400
        
        # Validate related records
        with session_scope() as session:
            # Check category exists
            category = session.query(MaterialCategory).filter_by(
                id=material_category_id
            ).first()
            if not category:
                return jsonify({"error": "Material category not found"}), 404
            
            # Check brand exists and is approved
            brand = session.query(ApprovedBrand).filter_by(
                id=approved_brand_id,
                is_deleted=False
            ).first()
            if not brand:
                return jsonify({"error": "Approved brand not found"}), 404
            if not brand.is_approved:
                return jsonify({"error": "Brand is not approved. Only approved brands can be used."}), 400
            
            # Read certificate photo
            photo_data = photo_file.read()
            photo_name = photo_file.filename
            photo_mimetype = photo_file.mimetype or 'image/jpeg'
            
            if len(photo_data) > 10 * 1024 * 1024:
                return jsonify({"error": "Certificate photo exceeds 10MB limit"}), 400
            
            # Create test
            test = MaterialTestRegister(
                project_id=project_id,
                material_category_id=material_category_id,
                approved_brand_id=approved_brand_id,
                material_description=material_description,
                grade_specification=grade_specification,
                quantity=quantity,
                quantity_unit=quantity_unit,
                supplier_name=supplier_name,
                supplier_email=supplier_email,
                manufacturer_name=manufacturer_name,
                batch_lot_number=batch_lot_number,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                location_description=location_description,
                lab_test_report_number=lab_test_report_number,
                test_parameters=json.dumps(test_parameters),
                test_results=json.dumps(test_results),
                pass_fail_status=pass_fail_status,
                certificate_photo_name=photo_name,
                certificate_photo_data=photo_data,
                certificate_photo_mimetype=photo_mimetype,
                verification_status='pending',
                remarks=remarks,
                entered_by=user_id
            )
            
            # Generate NCR on failure
            if pass_fail_status == 'fail':
                session.add(test)
                session.flush()
                test.ncr_generated = True
                test.ncr_number = generate_ncr_number(project_id, test.id)
            else:
                session.add(test)
                session.flush()
            
            test_dict = test.to_dict()
            test_dict['test_parameters'] = test_parameters
            test_dict['test_results'] = test_results
            test_dict['category_name'] = category.category_name
            test_dict['brand_name'] = brand.brand_name
            
            # Get project name for email
            project = session.query(Project).filter_by(id=project_id).first()
        
        # Send email notification on failure
        if pass_fail_status == 'fail':
            try:
                email_data = {
                    'material_description': material_description,
                    'brand_name': brand.brand_name,
                    'grade_specification': grade_specification,
                    'supplier_name': supplier_name,
                    'supplier_email': supplier_email,
                    'project_name': project.name if project else "Unknown",
                    'ncr_number': test.ncr_number
                }
                send_material_test_failure_email(email_data)
            except Exception as email_error:
                print(f"Warning: Email notification failed: {str(email_error)}")
        
        return jsonify({
            "success": True,
            "message": f"Material test created successfully. Status: {pass_fail_status}",
            "test": test_dict
        }), 201
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating material test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create test: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests/<int:test_id>', methods=['PUT'])
@jwt_required()
@project_access_required
def update_material_test(test_id):
    """Update material test details (only if not verified)."""
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            project_id = int(request.form.get('project_id'))
            data = request.form
        else:
            data = request.get_json()
            project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            test = session.query(MaterialTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            if test.verification_status in ['verified', 'rejected']:
                return jsonify({"error": "Cannot update verified/rejected test"}), 400
            
            # Update fields
            if 'remarks' in data:
                test.remarks = data['remarks']
            
            # Update certificate photo if provided
            if 'certificate_photo' in request.files:
                photo_file = request.files['certificate_photo']
                if photo_file.filename != '':
                    photo_data = photo_file.read()
                    if len(photo_data) > 10 * 1024 * 1024:
                        return jsonify({"error": "Certificate photo exceeds 10MB limit"}), 400
                    
                    test.certificate_photo_name = photo_file.filename
                    test.certificate_photo_data = photo_data
                    test.certificate_photo_mimetype = photo_file.mimetype or 'image/jpeg'
            
            test.updated_at = datetime.utcnow()
            session.flush()
            
            test_dict = test.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Test updated successfully",
            "test": test_dict
        }), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error updating test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update test: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests/<int:test_id>/verify', methods=['PUT'])
@jwt_required()
@quality_team_required
def verify_material_test(test_id):
    """
    Verify or reject material test.
    Only accessible to Quality team.
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        if 'verification_status' not in data:
            return jsonify({"error": "verification_status is required"}), 400
        
        verification_status = data['verification_status']
        if verification_status not in ['verified', 'rejected']:
            return jsonify({"error": "verification_status must be 'verified' or 'rejected'"}), 400
        
        verification_remarks = data.get('verification_remarks', '')
        
        with session_scope() as session:
            test = session.query(MaterialTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            test.verification_status = verification_status
            test.verified_by = user_id
            test.verified_at = datetime.utcnow()
            test.verification_remarks = verification_remarks
            test.updated_at = datetime.utcnow()
            
            session.flush()
            test_dict = test.to_dict()
        
        return jsonify({
            "success": True,
            "message": f"Test {verification_status} successfully",
            "test": test_dict
        }), 200
    
    except Exception as e:
        print(f"Error verifying test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to verify test: {str(e)}"}), 500


@material_tests_bp.route('/api/material-tests/<int:test_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required
def delete_material_test(test_id):
    """Soft delete material test."""
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            test = session.query(MaterialTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            test.is_deleted = True
            test.deleted_at = datetime.utcnow()
            test.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Test deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete test: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@material_tests_bp.route('/api/material-tests/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Material Test Register API",
        "version": "1.0.0",
        "features": "Flexible JSON parameters for any material type"
    }), 200
