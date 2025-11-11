"""
Cube Test Register API Blueprint

This module provides API endpoints for managing concrete cube testing.
Implements automatic strength calculation, IS 516 compliance, and dual notification channels.

Endpoints:
- GET    /api/cube-tests              - List cube tests for a project
- GET    /api/cube-tests/:id          - Get cube test details
- POST   /api/cube-tests              - Create new cube test set
- PUT    /api/cube-tests/:id          - Update test results (auto-calculates, sends notifications on failure)
- PUT    /api/cube-tests/:id/verify   - Verify test results (QM only)
- DELETE /api/cube-tests/:id          - Soft delete cube test

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
import traceback
import json

try:
    from .db import session_scope
    from .models import CubeTestRegister, BatchRegister, RMCVendor, MixDesign, Project, ProjectMembership, User, TestReminder, ThirdPartyLab
    from .email_notifications import notify_test_failure_email
    from .notifications import notify_test_failure
except ImportError:
    from db import session_scope
    from models import CubeTestRegister, BatchRegister, RMCVendor, MixDesign, Project, ProjectMembership, User, TestReminder, ThirdPartyLab
    from models import CubeTestRegister, BatchRegister, RMCVendor, MixDesign, Project, ProjectMembership, User
    from email_notifications import notify_test_failure_email
    from notifications import notify_test_failure


# Create Blueprint
cube_tests_bp = Blueprint('cube_tests', __name__)

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
    """
    Determine pass/fail status based on IS 516:1959 criteria.
    
    IS 516 Criteria:
    - 7 days: minimum 67% of expected strength
    - 28 days: minimum 100% of expected strength
    """
    if average_strength is None or expected_strength is None:
        return "pending"
    
    if test_age_days == 7:
        required_strength = expected_strength * 0.67
    elif test_age_days == 28:
        required_strength = expected_strength
    else:
        # For other ages, use proportional criteria
        if test_age_days < 7:
            required_strength = expected_strength * 0.50
        elif test_age_days < 28:
            # Linear interpolation between 7 and 28 days
            required_strength = expected_strength * (0.67 + (test_age_days - 7) * (0.33 / 21))
        else:
            required_strength = expected_strength
    
    return "pass" if average_strength >= required_strength else "fail"


def generate_ncr_number(project_id: int, test_id: int) -> str:
    """Generate NCR (Non-Conformance Report) number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"NCR-P{project_id}-CT{test_id}-{timestamp}"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@cube_tests_bp.route('/api/cube-tests', methods=['GET'])
@jwt_required()
@project_access_required
def get_cube_tests():
    """
    Get list of cube tests for a project.
    
    Query Parameters:
    - project_id (required): Filter by project
    - batch_id (optional): Filter by batch
    - status (optional): Filter by pass/fail status
    - age (optional): Filter by test age (7, 28)
    - date_from (optional): Filter by casting date range
    - date_to (optional): Filter by casting date range
    
    Returns:
    - List of cube test objects
    """
    try:
        project_id = request.args.get('project_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        status = request.args.get('status')
        age = request.args.get('age', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        with session_scope() as session:
            # Base query
            query = session.query(CubeTestRegister).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            # Apply filters
            if batch_id:
                query = query.filter_by(batch_id=batch_id)
            if status:
                query = query.filter_by(pass_fail_status=status)
            if age:
                query = query.filter_by(test_age_days=age)
            
            # Date range filter
            if date_from:
                try:
                    date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(CubeTestRegister.casting_date >= date_from_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_from format"}), 400
            
            if date_to:
                try:
                    date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(CubeTestRegister.casting_date <= date_to_dt)
                except ValueError:
                    return jsonify({"error": "Invalid date_to format"}), 400
            
            tests = query.order_by(CubeTestRegister.casting_date.desc()).all()
            
            # Enrich with batch and mix design info
            result = []
            for test in tests:
                test_dict = test.to_dict()
                
                # Add batch number
                if test.batch_id:
                    batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
                    test_dict['batch_number'] = batch.batch_number if batch else None
                    
                    # Add mix design info
                    if batch and batch.mix_design_id:
                        mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                        test_dict['mix_design_name'] = mix.name if mix else None
                        test_dict['mix_design_grade'] = mix.grade if mix else None
                
                result.append(test_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "cube_tests": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching cube tests: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch cube tests: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests/<int:test_id>', methods=['GET'])
@jwt_required()
@project_access_required
def get_cube_test(test_id):
    """Get details of a specific cube test."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            test = session.query(CubeTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Cube test not found"}), 404
            
            test_dict = test.to_dict()
            
            # Add batch details
            if test.batch_id:
                batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
                if batch:
                    test_dict['batch'] = {
                        'id': batch.id,
                        'batch_number': batch.batch_number,
                        'delivery_date': batch.delivery_date.isoformat() if batch.delivery_date else None,
                        'location_description': batch.location_description
                    }
                    
                    # Add mix design details
                    if batch.mix_design_id:
                        mix = session.query(MixDesign).filter_by(id=batch.mix_design_id).first()
                        if mix:
                            test_dict['mix_design'] = {
                                'id': mix.id,
                                'name': mix.name,
                                'grade': mix.grade,
                                'type': mix.type
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
                "cube_test": test_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching cube test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch cube test: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests', methods=['POST'])
@jwt_required()
@project_access_required
def create_cube_test():
    """
    Create a new cube test set.
    
    Request Body:
    {
        "project_id": int (required),
        "batch_id": int (required),
        "test_age_days": int (required, e.g., 7, 28),
        "number_of_cubes": int (required, 1-3),
        "casting_date": str (required, ISO date),
        "expected_strength_mpa": float (required),
        "remarks": str (optional)
    }
    
    Returns:
    - Created cube test object
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['project_id', 'batch_id', 'test_age_days', 'number_of_cubes', 
                          'casting_date', 'expected_strength_mpa']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        project_id = data['project_id']
        batch_id = data['batch_id']
        test_age_days = data['test_age_days']
        number_of_cubes = data['number_of_cubes']
        expected_strength_mpa = float(data['expected_strength_mpa'])
        remarks = data.get('remarks')
        
        # Validate number of cubes
        if number_of_cubes not in [1, 2, 3]:
            return jsonify({"error": "number_of_cubes must be 1, 2, or 3"}), 400
        
        # Parse casting date
        try:
            casting_date = datetime.fromisoformat(data['casting_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid casting_date format. Use ISO 8601 format"}), 400
        
        with session_scope() as session:
            # Validate batch exists
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Create cube test
            test = CubeTestRegister(
                project_id=project_id,
                batch_id=batch_id,
                test_age_days=test_age_days,
                number_of_cubes=number_of_cubes,
                casting_date=casting_date,
                expected_strength_mpa=expected_strength_mpa,
                pass_fail_status='pending',
                remarks=remarks,
                created_by=user_id
            )
            
            session.add(test)
            session.flush()
            
            test_dict = test.to_dict()
            test_dict['batch_number'] = batch.batch_number
        
        return jsonify({
            "success": True,
            "message": "Cube test created successfully. Awaiting test results.",
            "cube_test": test_dict
        }), 201
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating cube test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create cube test: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests/<int:test_id>', methods=['PUT'])
@jwt_required()
@project_access_required
def update_cube_test(test_id):
    """
    Update cube test with results.
    Automatically calculates average strength and pass/fail status.
    Sends dual notifications (Email + WhatsApp) on failure.
    Generates NCR on failure.
    
    Request Body:
    {
        "project_id": int (required),
        "cube_1_strength_mpa": float (optional),
        "cube_2_strength_mpa": float (optional),
        "cube_3_strength_mpa": float (optional),
        "testing_date": str (optional, ISO date),
        "remarks": str (optional)
    }
    
    Returns:
    - Updated cube test object
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            test = session.query(CubeTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Cube test not found"}), 404
            
            # Update cube strengths
            if 'cube_1_strength_mpa' in data:
                test.cube_1_strength_mpa = float(data['cube_1_strength_mpa']) if data['cube_1_strength_mpa'] else None
            if 'cube_2_strength_mpa' in data:
                test.cube_2_strength_mpa = float(data['cube_2_strength_mpa']) if data['cube_2_strength_mpa'] else None
            if 'cube_3_strength_mpa' in data:
                test.cube_3_strength_mpa = float(data['cube_3_strength_mpa']) if data['cube_3_strength_mpa'] else None
            
            # Update testing date
            if 'testing_date' in data:
                try:
                    test.testing_date = datetime.fromisoformat(data['testing_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid testing_date format"}), 400
            
            # Update remarks
            if 'remarks' in data:
                test.remarks = data['remarks']
            
            # Auto-calculate average strength
            test.average_strength_mpa = calculate_average_strength(
                test.cube_1_strength_mpa,
                test.cube_2_strength_mpa,
                test.cube_3_strength_mpa
            )
            
            # Determine pass/fail status
            old_status = test.pass_fail_status
            test.pass_fail_status = determine_pass_fail(
                test.average_strength_mpa,
                test.expected_strength_mpa,
                test.test_age_days
            )
            
            # Generate NCR on failure
            if test.pass_fail_status == 'fail' and old_status != 'fail':
                test.ncr_generated = True
                test.ncr_number = generate_ncr_number(project_id, test_id)
            
            test.updated_at = datetime.utcnow()
            session.flush()
            
            # Get enriched data for notifications
            batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
            mix_design = session.query(MixDesign).filter_by(id=batch.mix_design_id).first() if batch else None
            vendor = session.query(RMCVendor).filter_by(id=batch.vendor_id).first() if batch else None
            project = session.query(Project).filter_by(id=project_id).first()
            
            test_dict = test.to_dict()
            test_dict['batch_number'] = batch.batch_number if batch else None
            test_dict['mix_design_name'] = mix_design.name if mix_design else None
        
        # Send notifications on failure (Email + WhatsApp)
        if test.pass_fail_status == 'fail' and old_status != 'fail':
            try:
                # Prepare notification data
                notification_data = {
                    'test_id': test_id,
                    'batch_number': batch.batch_number if batch else "Unknown",
                    'mix_design_grade': mix_design.grade if mix_design else "Unknown",
                    'test_age_days': test.test_age_days,
                    'expected_strength': test.expected_strength_mpa,
                    'average_strength': test.average_strength_mpa,
                    'cube_1_strength': test.cube_1_strength_mpa,
                    'cube_2_strength': test.cube_2_strength_mpa,
                    'cube_3_strength': test.cube_3_strength_mpa,
                    'ncr_number': test.ncr_number,
                    'project_name': project.name if project else "Unknown Project",
                    'vendor_name': vendor.vendor_name if vendor else "Unknown Vendor",
                    'vendor_email': vendor.email if vendor and vendor.email else None,
                    'casting_date': test.casting_date.strftime("%Y-%m-%d") if test.casting_date else None,
                    'testing_date': test.testing_date.strftime("%Y-%m-%d") if test.testing_date else None
                }
                
                # Send email notification
                try:
                    notify_test_failure_email(**notification_data)
                except Exception as email_error:
                    print(f"Warning: Email notification failed: {str(email_error)}")
                
                # Send WhatsApp notification
                try:
                    notify_test_failure(test_id, notification_data)
                except Exception as whatsapp_error:
                    print(f"Warning: WhatsApp notification failed: {str(whatsapp_error)}")
                
                # Mark notification as sent
                test.notification_sent = True
                session.flush()
                
            except Exception as notification_error:
                print(f"Warning: Notification failed: {str(notification_error)}")
                # Don't fail the update if notification fails
        
        return jsonify({
            "success": True,
            "message": f"Cube test updated successfully. Status: {test.pass_fail_status}",
            "cube_test": test_dict
        }), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error updating cube test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update cube test: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests/<int:test_id>/verify', methods=['PUT'])
@jwt_required()
@quality_team_required
def verify_cube_test(test_id):
    """
    Verify cube test results.
    Only accessible to Quality Managers and Quality Engineers.
    
    Request Body:
    {
        "project_id": int (required),
        "verification_status": "verified" | "rejected" (required),
        "verification_remarks": str (optional)
    }
    
    Returns:
    - Updated cube test object
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
            test = session.query(CubeTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Cube test not found"}), 404
            
            # Update verification
            test.verification_status = verification_status
            test.verified_by = user_id
            test.verified_at = datetime.utcnow()
            test.verification_remarks = verification_remarks
            test.updated_at = datetime.utcnow()
            
            session.flush()
            test_dict = test.to_dict()
        
        return jsonify({
            "success": True,
            "message": f"Cube test {verification_status} successfully",
            "cube_test": test_dict
        }), 200
    
    except Exception as e:
        print(f"Error verifying cube test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to verify cube test: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests/<int:test_id>', methods=['DELETE'])
@jwt_required()
@quality_team_required
def delete_cube_test(test_id):
    """Soft delete a cube test."""
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        with session_scope() as session:
            test = session.query(CubeTestRegister).filter_by(
                id=test_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not test:
                return jsonify({"error": "Cube test not found"}), 404
            
            # Soft delete
            test.is_deleted = True
            test.deleted_at = datetime.utcnow()
            test.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Cube test deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting cube test: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete cube test: {str(e)}"}), 500


# ============================================================================
# BULK CUBE SET CREATION & TESTING WORKFLOW
# ============================================================================

@cube_tests_bp.route('/api/cube-tests/bulk-create', methods=['POST'])
@jwt_required()
@project_access_required
def bulk_create_cube_sets():
    """
    Create multiple cube test sets in one operation (e.g., 3/7/28/56 day sets).
    Automatically creates 3 cubes (A, B, C) per set and schedules test reminders.
    
    Request Body:
    {
        "batch_id": 1,
        "project_id": 1,
        "casting_date": "2025-11-11",
        "casting_time": "10:30",
        "test_ages": [3, 7, 28, 56],  // Days
        "number_of_sets_per_age": 1,  // How many sets per age (usually 1)
        "third_party_lab_assignments": {  // Optional
            "28": 5,  // Send 28-day tests to lab ID 5
            "56": 5
        },
        "curing_method": "Water",
        "curing_temperature": 23.0
    }
    
    Returns:
    - List of created cube test sets with reminder schedules
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['batch_id', 'project_id', 'casting_date', 'test_ages']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        batch_id = data['batch_id']
        project_id = data['project_id']
        casting_date_str = data['casting_date']
        casting_time = data.get('casting_time')
        test_ages = data['test_ages']  # e.g., [3, 7, 28, 56]
        sets_per_age = data.get('number_of_sets_per_age', 1)
        third_party_assignments = data.get('third_party_lab_assignments', {})
        curing_method = data.get('curing_method', 'Water')
        curing_temperature = data.get('curing_temperature')
        
        # Parse casting date
        casting_date = datetime.fromisoformat(casting_date_str.replace('Z', '+00:00'))
        
        created_tests = []
        created_reminders = []
        
        with session_scope() as session:
            # Verify batch exists
            batch = session.query(BatchRegister).filter_by(
                id=batch_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not batch:
                return jsonify({"error": "Batch not found"}), 404
            
            # Get mix design for required strength
            mix_design = session.query(MixDesign).filter_by(
                id=batch.mix_design_id
            ).first()
            
            required_strength_mpa = None
            if mix_design and mix_design.specified_strength_psi:
                # Convert PSI to MPa (1 psi = 0.00689476 MPa)
                required_strength_mpa = round(mix_design.specified_strength_psi * 0.00689476, 2)
            
            # Get existing set numbers for this batch
            existing_sets = session.query(CubeTestRegister).filter_by(
                batch_id=batch_id,
                is_deleted=False
            ).all()
            max_set_number = max([s.set_number for s in existing_sets], default=0)
            
            current_set_number = max_set_number
            
            # Create cube sets for each test age
            for test_age in test_ages:
                # Get third-party lab assignment if specified
                third_party_lab_id = third_party_assignments.get(str(test_age))
                
                # Create multiple sets per age if requested
                for set_index in range(sets_per_age):
                    current_set_number += 1
                    
                    # Calculate testing date (casting_date + test_age days)
                    testing_date = casting_date + timedelta(days=test_age)
                    
                    # Create cube test record
                    cube_test = CubeTestRegister(
                        batch_id=batch_id,
                        project_id=project_id,
                        set_number=current_set_number,
                        test_age_days=test_age,
                        cube_identifier=None,  # Set-level record (A/B/C are in the fields)
                        third_party_lab_id=third_party_lab_id,
                        casting_date=casting_date,
                        casting_time=casting_time,
                        cast_by=user_id,
                        curing_method=curing_method,
                        curing_temperature=curing_temperature,
                        required_strength_mpa=required_strength_mpa,
                        pass_fail_status='pending'
                    )
                    
                    session.add(cube_test)
                    session.flush()  # Get the ID
                    
                    # Create test reminder
                    reminder = TestReminder(
                        cube_test_id=cube_test.id,
                        project_id=project_id,
                        reminder_date=testing_date,
                        test_age_days=test_age,
                        status='pending'
                    )
                    
                    session.add(reminder)
                    session.flush()
                    
                    created_tests.append({
                        "id": cube_test.id,
                        "setNumber": cube_test.set_number,
                        "testAgeDays": test_age,
                        "castingDate": casting_date.isoformat(),
                        "testingDate": testing_date.isoformat(),
                        "thirdPartyLabId": third_party_lab_id,
                        "cubes": ["A", "B", "C"]
                    })
                    
                    created_reminders.append({
                        "id": reminder.id,
                        "cubeTestId": cube_test.id,
                        "reminderDate": testing_date.isoformat(),
                        "testAgeDays": test_age
                    })
        
        return jsonify({
            "success": True,
            "message": f"Created {len(created_tests)} cube test sets with reminders",
            "cube_tests": created_tests,
            "reminders": created_reminders
        }), 201
    
    except Exception as e:
        print(f"Error bulk creating cube tests: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create cube tests: {str(e)}"}), 500


@cube_tests_bp.route('/api/cube-tests/reminders/today', methods=['GET'])
@jwt_required()
def get_todays_reminders():
    """
    Get all cube tests due for testing today across all user's projects.
    Used for daily reminder notifications to quality engineers.
    
    Query Parameters:
    - date (optional): Specific date to check (default: today)
    
    Returns:
    - List of cube tests due today with batch and location details
    """
    try:
        user_id = get_current_user_id()
        
        # Get target date (default to today)
        date_str = request.args.get('date')
        if date_str:
            target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        else:
            target_date = datetime.utcnow().date()
        
        with session_scope() as session:
            # Get all projects user has access to
            memberships = session.query(ProjectMembership).filter_by(
                user_id=user_id
            ).all()
            
            project_ids = [m.project_id for m in memberships]
            
            if not project_ids:
                return jsonify({
                    "success": True,
                    "reminders": []
                }), 200
            
            # Get reminders for today
            reminders = session.query(TestReminder).filter(
                TestReminder.project_id.in_(project_ids),
                TestReminder.status == 'pending',
                TestReminder.test_completed == False,
                TestReminder.reminder_date >= datetime.combine(target_date, datetime.min.time()),
                TestReminder.reminder_date < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
            ).all()
            
            reminder_data = []
            for reminder in reminders:
                cube_test = session.query(CubeTestRegister).filter_by(
                    id=reminder.cube_test_id,
                    is_deleted=False
                ).first()
                
                if not cube_test:
                    continue
                
                batch = session.query(BatchRegister).filter_by(
                    id=cube_test.batch_id
                ).first()
                
                project = session.query(Project).filter_by(
                    id=reminder.project_id
                ).first()
                
                third_party_lab = None
                if cube_test.third_party_lab_id:
                    third_party_lab = session.query(ThirdPartyLab).filter_by(
                        id=cube_test.third_party_lab_id
                    ).first()
                
                reminder_data.append({
                    "reminderId": reminder.id,
                    "cubeTestId": cube_test.id,
                    "setNumber": cube_test.set_number,
                    "testAgeDays": cube_test.test_age_days,
                    "castingDate": cube_test.casting_date.isoformat(),
                    "testingDate": reminder.reminder_date.isoformat(),
                    "project": {
                        "id": project.id if project else None,
                        "name": project.name if project else None
                    },
                    "batch": {
                        "id": batch.id if batch else None,
                        "batchNumber": batch.batch_number if batch else None,
                        "location": {
                            "buildingName": batch.building_name if batch else None,
                            "floorLevel": batch.floor_level if batch else None,
                            "structuralElementType": batch.structural_element_type if batch else None,
                            "elementId": batch.element_id if batch else None
                        }
                    },
                    "thirdPartyLab": {
                        "id": third_party_lab.id if third_party_lab else None,
                        "name": third_party_lab.lab_name if third_party_lab else None
                    } if third_party_lab else None,
                    "cubes": ["A", "B", "C"]
                })
            
            return jsonify({
                "success": True,
                "date": target_date.isoformat(),
                "count": len(reminder_data),
                "reminders": reminder_data
            }), 200
    
    except Exception as e:
        print(f"Error fetching today's reminders: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch reminders: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@cube_tests_bp.route('/api/cube-tests/health', methods=['GET'])
def health_check():
    """Health check endpoint for cube test API."""
    return jsonify({
        "status": "ok",
        "service": "Cube Test Register API",
        "version": "1.0.0"
    }), 200
