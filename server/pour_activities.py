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
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models import PourActivity, BatchRegister, Project, User, db

pour_activities_bp = Blueprint('pour_activities', __name__, url_prefix='/api/pour-activities')


@pour_activities_bp.route('', methods=['POST'])
@jwt_required()
def create_pour_activity(current_user):
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
        data = request.get_json()
        
        # Validate required fields
        if not data.get('projectId'):
            return jsonify({"error": "projectId is required"}), 400
        
        # Verify project exists and user has access
        project = db.session.query(Project).filter_by(id=data['projectId']).first()
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Auto-generate pour_id if not provided
        pour_id = data.get('pourId')
        if not pour_id:
            # Generate: POUR-YYYY-NNN
            last_pour = db.session.query(PourActivity)\
                .filter_by(project_id=data['projectId'])\
                .order_by(PourActivity.id.desc())\
                .first()
            
            next_number = 1
            if last_pour and last_pour.pour_id:
                # Extract number from POUR-2025-001
                parts = last_pour.pour_id.split('-')
                if len(parts) == 3 and parts[2].isdigit():
                    next_number = int(parts[2]) + 1
            
            year = datetime.now().year
            pour_id = f"POUR-{year}-{next_number:03d}"
        
        # Get location data
        location = data.get('location', {})
        
        # Create pour activity
        pour = PourActivity(
            project_id=data['projectId'],
            pour_id=pour_id,
            pour_date=datetime.fromisoformat(data.get('pourDate', datetime.now().isoformat())),
            
            # Location details
            building_name=location.get('buildingName'),
            floor_level=location.get('floorLevel'),
            zone=location.get('zone'),
            grid_reference=location.get('gridReference'),
            structural_element_type=location.get('structuralElementType'),
            element_id=location.get('elementId'),
            location_description=location.get('description'),
            
            # Concrete details
            concrete_type=data.get('concreteType', 'Normal'),
            design_grade=data.get('designGrade'),
            total_quantity_planned=data.get('totalQuantityPlanned', 0.0),
            
            # Status
            status='in_progress',
            started_at=datetime.now(),
            created_by=current_user.id,
            remarks=data.get('remarks')
        )
        
        db.session.add(pour)
        db.session.commit()
        
        return jsonify({
            "message": "Pour activity created successfully",
            "pourActivity": pour.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pour_activities_bp.route('', methods=['GET'])
@jwt_required()
def list_pour_activities(current_user):
    """
    List all pour activities for a project
    
    Query Parameters:
    - projectId: Filter by project (required)
    - status: Filter by status (in_progress/completed/cancelled)
    - concreteType: Filter by concrete type (Normal/PT)
    """
    try:
        project_id = request.args.get('projectId')
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
def get_pour_activity(current_user, pour_id):
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
def update_pour_activity(current_user, pour_id):
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
def complete_pour_activity(current_user, pour_id):
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
        pour.completed_by = current_user.id
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
def add_batch_to_pour(current_user, pour_id):
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
def delete_pour_activity(current_user, pour_id):
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
