"""
Third-Party Cube Test API Blueprint

This module provides API endpoints for managing cube tests performed by third-party labs.
Features manual data entry with certificate photo upload (OCR deferred to Phase 2).

Endpoints:
- GET    /api/third-party-cube-tests              - List tests for a project
- GET    /api/third-party-cube-tests/:id          - Get test details
- GET    /api/third-party-cube-tests/:id/certificate - Get certificate photo
- POST   /api/third-party-cube-tests              - Create test with certificate photo
- PUT    /api/third-party-cube-tests/:id          - Update test details
- PUT    /api/third-party-cube-tests/:id/verify   - Verify test (QM only)
- DELETE /api/third-party-cube-tests/:id          - Soft delete test

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
    from .models import (ThirdPartyCubeTest, ThirdPartyLab, BatchRegister, 
                        MixDesign, Project, ProjectMembership, User)
    from .email_notifications import notify_test_failure_email
except ImportError:
    from db import session_scope
    from models import (ThirdPartyCubeTest, ThirdPartyLab, BatchRegister, 
                       MixDesign, Project, ProjectMembership, User)
    from email_notifications import notify_test_failure_email


# Create Blueprint
third_party_cube_tests_bp = Blueprint('third_party_cube_tests', __name__)

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
            # For multipart/form-data
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

def calculate_average_strength(cube1: float = None, cube2: float = None, cube3: float = None) -> float:
    """Calculate average strength from cube test results."""
    cubes = [c for c in [cube1, cube2, cube3] if c is not None]
    if not cubes:
        return None
    return round(sum(cubes) / len(cubes), 2)


def determine_pass_fail(average_strength: float, expected_strength: float, test_age_days: int) -> str:
    """Determine pass/fail status based on IS 516:1959 criteria."""
    if average_strength is None or expected_strength is None:
        return "pending"
    
    if test_age_days == 7:
        required_strength = expected_strength * 0.67
    elif test_age_days == 28:
        required_strength = expected_strength
    else:
        if test_age_days < 7:
            required_strength = expected_strength * 0.50
        elif test_age_days < 28:
            required_strength = expected_strength * (0.67 + (test_age_days - 7) * (0.33 / 21))
        else:
            required_strength = expected_strength
    
    return "pass" if average_strength >= required_strength else "fail"


def generate_ncr_number(project_id: int, test_id: int) -> str:
    """Generate NCR number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"NCR-P{project_id}-TPT{test_id}-{timestamp}"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@third_party_cube_tests_bp.route('/api/third-party-cube-tests', methods=['GET'])
@jwt_required()
@project_access_required
def get_third_party_tests():
    """
    Get list of third-party cube tests.
    
    Query Parameters:
    - project_id (required): Filter by project
    - batch_id (optional): Filter by batch
    - lab_id (optional): Filter by lab
    - status (optional): Filter by pass/fail status
    - age (optional): Filter by test age
    
    Returns:
    - List of test objects
    """
    try:
        project_id = request.args.get('project_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        lab_id = request.args.get('lab_id', type=int)
        status = request.args.get('status')
        age = request.args.get('age', type=int)
        
        with session_scope() as session:
            query = session.query(ThirdPartyCubeTest).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            if batch_id:
                query = query.filter_by(batch_id=batch_id)
            if lab_id:
                query = query.filter_by(lab_id=lab_id)
            if status:
                query = query.filter_by(pass_fail_status=status)
            if age:
                query = query.filter_by(test_age_days=age)
            
            tests = query.order_by(ThirdPartyCubeTest.testing_date.desc()).all()
            
            # Enrich with related data
            result = []
            for test in tests:
                test_dict = test.to_dict()
                
                # Add lab name
                if test.lab_id:
                    lab = session.query(ThirdPartyLab).filter_by(id=test.lab_id).first()
                    test_dict['lab_name'] = lab.lab_name if lab else None
                
                # Add batch number
                if test.batch_id:
                    batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
                    test_dict['batch_number'] = batch.batch_number if batch else None
                    
                    if batch and batch.mix_design_id:
                        mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                        test_dict['mix_design_grade'] = mix.grade if mix else None
                
                result.append(test_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "tests": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching third-party tests: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch tests: {str(e)}"}), 500


@third_party_cube_tests_bp.route('/api/third-party-cube-tests/<int:test_id>', methods=['GET'])
@jwt_required()
@project_access_required
def get_third_party_test(test_id):
    """Get details of a specific third-party test."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            test = session.query(ThirdPartyCubeTest).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            test_dict = test.to_dict()
            
            # Add lab details
            if test.lab_id:
                lab = session.query(ThirdPartyLab).filter_by(id=test.lab_id).first()
                if lab:
                    test_dict['lab'] = {
                        'id': lab.id,
                        'name': lab.lab_name,
                        'nabl_number': lab.nabl_accreditation_number
                    }
            
            # Add batch details
            if test.batch_id:
                batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
                if batch:
                    test_dict['batch'] = {
                        'id': batch.id,
                        'batch_number': batch.batch_number,
                        'location': batch.location_description
                    }
                    
                    if batch.mix_design_id:
                        mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                        if mix:
                            test_dict['mix_design'] = {
                                'id': mix.id,
                                'name': mix.name,
                                'grade': mix.grade
                            }
            
            # Add user names
            if test.created_by:
                creator = session.query(User).filter_by(id=test.created_by).first()
                test_dict['created_by_name'] = creator.name if creator else None
            
            if test.verified_by:
                verifier = session.query(User).filter_by(id=test.verified_by).first()
                test_dict['verified_by_name'] = verifier.name if verifier else None
            
            return jsonify({
                "success": True,
                "test": test_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching third-party test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch test: {str(e)}"}), 500


@third_party_cube_tests_bp.route('/api/third-party-cube-tests/<int:test_id>/certificate', methods=['GET'])
@jwt_required()
@project_access_required
def get_certificate(test_id):
    """Get test certificate photo."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            test = session.query(ThirdPartyCubeTest).filter_by(
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


@third_party_cube_tests_bp.route('/api/third-party-cube-tests', methods=['POST'])
@jwt_required()
@project_access_required
def create_third_party_test():
    """
    Create new third-party cube test with certificate photo.
    Manual data entry from lab certificate (OCR in Phase 2).
    
    Request: multipart/form-data
    - project_id (required): int
    - batch_id (required): int
    - lab_id (required): int
    - lab_test_report_number (required): string (unique)
    - test_age_days (required): int (7, 28, etc.)
    - number_of_cubes_tested (required): int (1-3)
    - sample_collection_date (required): ISO date
    - sample_received_at_lab_date (optional): ISO date
    - testing_date (required): ISO date
    - expected_strength_mpa (required): float
    - cube_1_strength_mpa (required): float
    - cube_2_strength_mpa (optional): float
    - cube_3_strength_mpa (optional): float
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
        required_fields = ['project_id', 'batch_id', 'lab_id', 'lab_test_report_number',
                          'test_age_days', 'number_of_cubes_tested', 'sample_collection_date',
                          'testing_date', 'expected_strength_mpa', 'cube_1_strength_mpa']
        
        for field in required_fields:
            if field not in request.form:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Parse form data
        project_id = int(request.form['project_id'])
        batch_id = int(request.form['batch_id'])
        lab_id = int(request.form['lab_id'])
        lab_test_report_number = request.form['lab_test_report_number']
        test_age_days = int(request.form['test_age_days'])
        number_of_cubes_tested = int(request.form['number_of_cubes_tested'])
        expected_strength_mpa = float(request.form['expected_strength_mpa'])
        
        # Validate number of cubes
        if number_of_cubes_tested not in [1, 2, 3]:
            return jsonify({"error": "number_of_cubes_tested must be 1, 2, or 3"}), 400
        
        # Parse cube strengths
        cube_1_strength = float(request.form['cube_1_strength_mpa'])
        cube_2_strength = float(request.form['cube_2_strength_mpa']) if request.form.get('cube_2_strength_mpa') else None
        cube_3_strength = float(request.form['cube_3_strength_mpa']) if request.form.get('cube_3_strength_mpa') else None
        
        # Parse dates
        try:
            sample_collection_date = datetime.fromisoformat(request.form['sample_collection_date'].replace('Z', '+00:00'))
            testing_date = datetime.fromisoformat(request.form['testing_date'].replace('Z', '+00:00'))
            sample_received_date = None
            if request.form.get('sample_received_at_lab_date'):
                sample_received_date = datetime.fromisoformat(request.form['sample_received_at_lab_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO 8601 format"}), 400
        
        remarks = request.form.get('remarks')
        
        # Validate related records
        with session_scope() as session:
            # Check batch exists
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Check lab exists and is approved
            lab = session.query(ThirdPartyLab).filter_by(
                id=lab_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            if not lab:
                return jsonify({"error": "Lab not found"}), 404
            if not lab.is_approved:
                return jsonify({"error": "Lab is not approved"}), 400
            
            # Check report number uniqueness
            existing = session.query(ThirdPartyCubeTest).filter_by(
                project_id=project_id,
                lab_test_report_number=lab_test_report_number,
                is_deleted=False
            ).first()
            if existing:
                return jsonify({"error": f"Report number '{lab_test_report_number}' already exists"}), 400
            
            # Read certificate photo
            photo_data = photo_file.read()
            photo_name = photo_file.filename
            photo_mimetype = photo_file.mimetype or 'image/jpeg'
            
            if len(photo_data) > 10 * 1024 * 1024:
                return jsonify({"error": "Certificate photo exceeds 10MB limit"}), 400
            
            # Calculate average and pass/fail
            average_strength = calculate_average_strength(cube_1_strength, cube_2_strength, cube_3_strength)
            pass_fail_status = determine_pass_fail(average_strength, expected_strength_mpa, test_age_days)
            
            # Create test
            test = ThirdPartyCubeTest(
                project_id=project_id,
                batch_id=batch_id,
                lab_id=lab_id,
                lab_test_report_number=lab_test_report_number,
                test_age_days=test_age_days,
                number_of_cubes_tested=number_of_cubes_tested,
                sample_collection_date=sample_collection_date,
                sample_received_at_lab_date=sample_received_date,
                testing_date=testing_date,
                expected_strength_mpa=expected_strength_mpa,
                cube_1_strength_mpa=cube_1_strength,
                cube_2_strength_mpa=cube_2_strength,
                cube_3_strength_mpa=cube_3_strength,
                average_strength_mpa=average_strength,
                pass_fail_status=pass_fail_status,
                certificate_photo_name=photo_name,
                certificate_photo_data=photo_data,
                certificate_photo_mimetype=photo_mimetype,
                remarks=remarks,
                created_by=user_id
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
            test_dict['lab_name'] = lab.lab_name
            test_dict['batch_number'] = batch.batch_number
            
            # Get additional data for email notification
            mix_design = session.query(MixDesign).filter_by(id=batch.mix_design_id).first() if batch.mix_design_id else None
            project = session.query(Project).filter_by(id=project_id).first()
        
        # Send email notification on failure
        if pass_fail_status == 'fail':
            try:
                notification_data = {
                    'test_id': test.id,
                    'batch_number': batch.batch_number,
                    'mix_design_grade': mix_design.grade if mix_design else "Unknown",
                    'test_age_days': test_age_days,
                    'expected_strength': expected_strength_mpa,
                    'average_strength': average_strength,
                    'cube_1_strength': cube_1_strength,
                    'cube_2_strength': cube_2_strength,
                    'cube_3_strength': cube_3_strength,
                    'ncr_number': test.ncr_number,
                    'project_name': project.name if project else "Unknown",
                    'vendor_name': f"Third-Party Lab: {lab.lab_name}",
                    'vendor_email': lab.email if lab.email else None,
                    'casting_date': sample_collection_date.strftime("%Y-%m-%d"),
                    'testing_date': testing_date.strftime("%Y-%m-%d")
                }
                
                notify_test_failure_email(**notification_data)
                
                # Mark notification as sent
                with session_scope() as session:
                    test_to_update = session.query(ThirdPartyCubeTest).filter_by(id=test.id).first()
                    if test_to_update:
                        test_to_update.notification_sent = True
                
            except Exception as email_error:
                print(f"Warning: Email notification failed: {str(email_error)}")
        
        return jsonify({
            "success": True,
            "message": f"Third-party test created successfully. Status: {pass_fail_status}",
            "test": test_dict
        }), 201
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating third-party test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create test: {str(e)}"}), 500


@third_party_cube_tests_bp.route('/api/third-party-cube-tests/<int:test_id>', methods=['PUT'])
@jwt_required()
@project_access_required
def update_third_party_test(test_id):
    """
    Update third-party test details.
    Can only update if not yet verified.
    """
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
            test = session.query(ThirdPartyCubeTest).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Test not found"}), 404
            
            if test.verification_status in ['verified', 'rejected']:
                return jsonify({"error": "Cannot update verified/rejected test"}), 400
            
            # Update fields if provided
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


@third_party_cube_tests_bp.route('/api/third-party-cube-tests/<int:test_id>/verify', methods=['PUT'])
@jwt_required()
@quality_team_required
def verify_third_party_test(test_id):
    """
    Verify or reject third-party test.
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
            test = session.query(ThirdPartyCubeTest).filter_by(
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


@third_party_cube_tests_bp.route('/api/third-party-cube-tests/<int:test_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required
def delete_third_party_test(test_id):
    """Soft delete third-party test."""
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            test = session.query(ThirdPartyCubeTest).filter_by(
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

@third_party_cube_tests_bp.route('/api/third-party-cube-tests/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Third-Party Cube Test API",
        "version": "1.0.0",
        "note": "Manual entry from lab certificates. OCR in Phase 2."
    }), 200
