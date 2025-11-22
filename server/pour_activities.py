"""
Pour Activity API - Batch Consolidation for Concrete Pours
Enables grouping multiple batches/vehicles into one pouring activity.
Use Case: 4m³ slab needs 3+ vehicles → Create ONE pour → Link all batches → ONE set of cube tests

Supports:
- Normal concrete: Tests at 3, 7, 28, 56 days
- PT (Post-Tensioned) concrete: Tests at 5, 7, 28, 56 days (5 instead of 3)
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import PourActivity, BatchRegister, Project, User
from server.db import db

DEBUG_LOG_PATH = r"C:\Users\shrot\OneDrive\Desktop\ProSite\concretethings\server_debug.log"

def _log_debug(msg):
    try:
        with open(DEBUG_LOG_PATH, "a") as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except:
        pass

def _get_current_user():
    """Resolve the current authenticated user from the JWT."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return db.session.query(User).filter_by(id=user_id).first()

pour_activities_bp = Blueprint('pour_activities', __name__, url_prefix='/api/pour-activities')


@pour_activities_bp.route('', methods=['POST'])
@jwt_required()
def create_pour_activity():
    """
    Create a new pour activity
    
    Request Body:
    {
        "projectId": 1,
        "pourId": "POUR-2025-001",  # Optional, auto-generated if not provided
        "pourDate": "2025-01-15T10:00:00",
        "location": {
            "buildingName": "Tower A",
            "floorLevel": "Level 5",
            "zone": "North Wing",
            "gridReference": "A-12",
            "structuralElementType": "Slab",
            "elementId": "S-A12-L5",
            "description": "Slab at Grid A-12, Level 5"
        },
        "concreteType": "PT",  # "Normal" or "PT" (Post-Tensioned)
        "designGrade": "M40",
        "totalQuantityPlanned": 4.0,
        "remarks": "Large slab pour requiring 3+ vehicles"
    }
    """

    try:
        _log_debug("create_pour_activity called")
        data = request.get_json() or {}
        
        _log_debug("Validating projectId")
        if not data.get('projectId'):
            return jsonify({"error": "projectId is required"}), 400
        
        _log_debug("Getting current user")
        current_user = _get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        try:
            project_id = int(data['projectId'])
        except (TypeError, ValueError):
            return jsonify({"error": "projectId must be numeric"}), 400

        _log_debug(f"Verifying project {project_id}")
        project = db.session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        _log_debug("Generating pour_id")
        pour_id = data.get('pourId')
        if not pour_id:
            last_pour = db.session.query(PourActivity)\
                .filter_by(project_id=project_id)\
                .order_by(PourActivity.id.desc())\
                .first()
            
            next_number = 1
            if last_pour and last_pour.pour_id:
                parts = last_pour.pour_id.split('-')
                if len(parts) == 3 and parts[2].isdigit():
                    next_number = int(parts[2]) + 1
            
            year = datetime.now().year
            pour_id = f"POUR-{year}-{next_number:03d}"
        
        _log_debug("Creating PourActivity object")
        location = data.get('location', {})
        
        pour = PourActivity(
            project_id=project_id,
            pour_id=pour_id,
            pour_date=datetime.fromisoformat(data.get('pourDate', datetime.now().isoformat())),
            building_name=location.get('buildingName'),
            floor_level=location.get('floorLevel'),
            zone=location.get('zone'),
            grid_reference=location.get('gridReference'),
            structural_element_type=location.get('structuralElementType'),
            element_id=location.get('elementId'),
            location_description=location.get('description'),
            concrete_type=data.get('concreteType', 'Normal'),
            design_grade=data.get('designGrade'),
            total_quantity_planned=data.get('totalQuantityPlanned', 0.0),
            status='in_progress',
            started_at=datetime.now(),
            created_by=current_user.id,
            remarks=data.get('remarks')
        )
        
        _log_debug("Adding pour to session")
        db.session.add(pour)
        db.session.flush()
        
        # Create planned cube tests if schedule provided
        cube_schedule = data.get('cubeSchedule', [])
        if cube_schedule:
            from server.models import CubeTestRegister, TestReminder
            
            current_set_number = 0
            
            for item in cube_schedule:
                try:
                    age = int(item.get('age'))
                    sets = int(item.get('sets', 1))
                    
                    for _ in range(sets):
                        current_set_number += 1
                        
                        # Calculate testing date
                        casting_date = pour.pour_date
                        testing_date = casting_date + timedelta(days=age)
                        
                        # Create planned test
                        cube_test = CubeTestRegister(
                            project_id=project_id,
                            batch_id=None,  # No batch yet
                            pour_activity_id=pour.id,
                            set_number=current_set_number,
                            test_age_days=age,
                            casting_date=casting_date,
                            cast_by=current_user.id,
                            concrete_type=pour.concrete_type,
                            concrete_grade=pour.design_grade,
                            number_of_cubes=3,  # Default
                            pass_fail_status='planned',
                            remarks="Planned test from Pour Activity"
                        )
                        db.session.add(cube_test)
                        db.session.flush()
                        
                        # Create reminder
                        reminder = TestReminder(
                            cube_test_id=cube_test.id,
                            project_id=project_id,
                            reminder_date=testing_date,  # Pass datetime object
                            test_age_days=age,
                            status='pending'
                        )
                        db.session.add(reminder)
                        
                except (ValueError, TypeError):
                    continue
        
        db.session.commit()
        
        return jsonify({
            "message": "Pour activity created successfully",
            "pourActivity": pour.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        _log_debug(f"Error creating pour activity: {e}")
        _log_debug(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('', methods=['GET'])
@jwt_required()
def list_pour_activities():
    """
    List all pour activities for a project
    
    Query Parameters:
    - projectId: Filter by project (required)
    - status: Filter by status (in_progress/completed/cancelled)
    - concreteType: Filter by concrete type (Normal/PT)
    """
    try:
        project_id = request.args.get('projectId', type=int)
        if not project_id:
            return jsonify({"error": "projectId is required"}), 400
        
        # Build query
        query = db.session.query(PourActivity)\
            .filter_by(project_id=project_id)\
            .options(joinedload(PourActivity.batches))
        
        # Apply filters
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        concrete_type = request.args.get('concreteType')
        if concrete_type:
            query = query.filter_by(concrete_type=concrete_type)
        
        # Order by most recent first
        pour_activities = query.order_by(PourActivity.pour_date.desc()).all()
        
        return jsonify({
            "pourActivities": [pour.to_dict() for pour in pour_activities],
            "total": len(pour_activities)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('/<int:pour_id>', methods=['GET'])
@jwt_required()
def get_pour_activity(pour_id):
    """
    Get pour activity details with linked batches
    """
    try:
        pour = db.session.query(PourActivity)\
            .options(joinedload(PourActivity.batches))\
            .filter_by(id=pour_id)\
            .first()
        
        if not pour:
            return jsonify({"error": "Pour activity not found"}), 404
        
        # Get pour data
        pour_data = pour.to_dict()
        
        # Add batch details
        pour_data['batches'] = [batch.to_dict() for batch in pour.batches]
        
        # Calculate actual total quantity from batches
        total_received = sum(batch.quantity_received or 0 for batch in pour.batches)
        pour_data['totalQuantityReceived'] = total_received
        
        return jsonify({"pourActivity": pour_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('/<int:pour_id>', methods=['PUT'])
@jwt_required()
def update_pour_activity(pour_id):
    """
    Update pour activity details
    
    Request Body:
    {
        "location": { ... },
        "concreteType": "PT",
        "designGrade": "M40",
        "totalQuantityPlanned": 5.0,
        "remarks": "Updated pour details"
    }
    """
    try:
        pour = db.session.query(PourActivity).filter_by(id=pour_id).first()
        if not pour:
            return jsonify({"error": "Pour activity not found"}), 404
        
        # Can't update completed pours
        if pour.status == 'completed':
            return jsonify({"error": "Cannot update completed pour activity"}), 400
        
        data = request.get_json()
        
        # Update location if provided
        location = data.get('location')
        if location:
            pour.building_name = location.get('buildingName', pour.building_name)
            pour.floor_level = location.get('floorLevel', pour.floor_level)
            pour.zone = location.get('zone', pour.zone)
            pour.grid_reference = location.get('gridReference', pour.grid_reference)
            pour.structural_element_type = location.get('structuralElementType', pour.structural_element_type)
            pour.element_id = location.get('elementId', pour.element_id)
            pour.location_description = location.get('description', pour.location_description)
        
        # Update concrete details
        if 'concreteType' in data:
            pour.concrete_type = data['concreteType']
        if 'designGrade' in data:
            pour.design_grade = data['designGrade']
        if 'totalQuantityPlanned' in data:
            pour.total_quantity_planned = data['totalQuantityPlanned']
        if 'remarks' in data:
            pour.remarks = data['remarks']
        
        db.session.commit()
        
        return jsonify({
            "message": "Pour activity updated successfully",
            "pourActivity": pour.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('/<int:pour_id>/complete', methods=['POST'])
@jwt_required()
def complete_pour_activity(pour_id):
    """
    Mark pour activity as completed
    This will trigger the cube casting modal on frontend
    
    Request Body:
    {
        "remarks": "Pour completed successfully, all 3 vehicles delivered"
    }
    """
    try:
        pour = db.session.query(PourActivity)\
            .options(joinedload(PourActivity.batches))\
            .filter_by(id=pour_id)\
            .first()
        
        if not pour:
            return jsonify({"error": "Pour activity not found"}), 404
        
        if pour.status == 'completed':
            return jsonify({"error": "Pour activity already completed"}), 400
        
        # Validate at least one batch is linked
        if not pour.batches or len(pour.batches) == 0:
            return jsonify({"error": "Cannot complete pour with no batches linked"}), 400
        
        # Calculate total received quantity
        total_received = sum(batch.quantity_received or 0 for batch in pour.batches)
        
        # Update pour
        data = request.get_json() or {}
        pour.status = 'completed'
        pour.completed_at = datetime.now()
        current_user = _get_current_user()
        pour.completed_by = current_user.id if current_user else None
        pour.total_quantity_received = total_received
        if data.get('remarks'):
            pour.remarks = data['remarks']
        
        db.session.commit()
        
        # Return pour data with batches for cube modal
        pour_data = pour.to_dict()
        pour_data['batches'] = [batch.to_dict() for batch in pour.batches]
        pour_data['totalQuantityReceived'] = total_received
        
        return jsonify({
            "message": "Pour activity completed successfully",
            "pourActivity": pour_data,
            "showCubeModal": True,  # Signal to frontend
            "concreteType": pour.concrete_type,  # For PT logic
            "testAges": [5, 7, 28, 56] if pour.concrete_type == 'PT' else [3, 7, 28, 56]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('/<int:pour_id>/batches', methods=['POST'])
@jwt_required()
def add_batch_to_pour(pour_id):
    """
    Link an existing batch to a pour activity
    
    Request Body:
    {
        "batchId": 123
    }
    """
    try:
        pour = db.session.query(PourActivity).filter_by(id=pour_id).first()
        if not pour:
            return jsonify({"error": "Pour activity not found"}), 404
        
        if pour.status == 'completed':
            return jsonify({"error": "Cannot add batches to completed pour"}), 400
        
        data = request.get_json()
        batch_id = data.get('batchId')
        
        if not batch_id:
            return jsonify({"error": "batchId is required"}), 400
        
        # Get batch
        batch = db.session.query(BatchRegister).filter_by(id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404
        
        # Validate batch is not already linked to another pour
        if batch.pour_activity_id and batch.pour_activity_id != pour_id:
            return jsonify({"error": "Batch is already linked to another pour activity"}), 400
        
        # Link batch to pour
        batch.pour_activity_id = pour_id
        db.session.commit()
        
        return jsonify({
            "message": "Batch added to pour activity successfully",
            "batch": batch.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('/<int:pour_id>', methods=['DELETE'])
@jwt_required()
def delete_pour_activity(pour_id):
    """
    Cancel/soft delete a pour activity
    Only in_progress pours can be cancelled
    """
    try:
        pour = db.session.query(PourActivity).filter_by(id=pour_id).first()
        if not pour:
            return jsonify({"error": "Pour activity not found"}), 404
        
        if pour.status == 'completed':
            return jsonify({"error": "Cannot cancel completed pour activity"}), 400
        
        # Unlink all batches
        for batch in pour.batches:
            batch.pour_activity_id = None
        
        # Mark as cancelled (soft delete)
        pour.status = 'cancelled'
        db.session.commit()
        
        return jsonify({"message": "Pour activity cancelled successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
