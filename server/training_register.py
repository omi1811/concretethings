"""
Site Training Register API Blueprint

This module provides API endpoints for managing site training records.
Captures training photos (click or upload), trainee names, location, and activity type.

Endpoints:
- GET    /api/training-records              - List training records with filters
- GET    /api/training-records/:id          - Get specific training record details
- GET    /api/training-records/:id/photo    - Serve training photo
- POST   /api/training-records              - Create new training record with photo
- PUT    /api/training-records/:id          - Update training record
- DELETE /api/training-records/:id          - Soft delete training record (QM only)
- GET    /api/training-records/stats        - Get training statistics
- GET    /api/training-records/health       - Health check

All endpoints require JWT authentication and project-level access control.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import traceback

try:
    from .db import session_scope
    from .models import TrainingRecord, User, Project, ProjectMembership
except ImportError:
    from db import session_scope
    from models import TrainingRecord, User, Project, ProjectMembership


# Create Blueprint
training_register_bp = Blueprint('training_register', __name__)


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
    """
    Decorator to check if user has access to the project.
    Expects 'project_id' in request JSON or query params.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        # Get project_id from request
        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
        else:
            data = request.get_json() if request.is_json else {}
            project_id = data.get('project_id') if data else request.form.get('project_id', type=int)
        
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


def quality_manager_required(f):
    """
    Decorator to check if user is Quality Manager.
    Only QM can delete training records.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        # Get project_id
        if request.method == 'GET':
            project_id = request.args.get('project_id', type=int)
        else:
            data = request.get_json() if request.is_json else {}
            project_id = data.get('project_id') if data else request.form.get('project_id', type=int)
        
        if not project_id:
            return jsonify({"error": "project_id is required"}), 400
        
        # Check user role
        with session_scope() as session:
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if not membership or membership.role != 'Quality Manager':
                return jsonify({"error": "Access denied. Only Quality Managers can perform this action"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# ROUTES
# ============================================================================

@training_register_bp.route('/api/training-records/health', methods=['GET'])
def health_check():
    """Health check endpoint for training register service."""
    return jsonify({
        "service": "training-register-api",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@training_register_bp.route('/api/training-records', methods=['GET'])
@jwt_required()
@project_access_required
def get_training_records():
    """
    Get list of training records for a project.
    
    Query Parameters:
    - project_id (required): Filter by project
    - building (optional): Filter by building/location
    - activity (optional): Filter by activity type
    - trainer_id (optional): Filter by trainer
    - start_date (optional): Filter records from this date (YYYY-MM-DD)
    - end_date (optional): Filter records until this date (YYYY-MM-DD)
    
    Returns:
    - List of training record objects with trainee names
    """
    try:
        project_id = request.args.get('project_id', type=int)
        building = request.args.get('building')
        activity = request.args.get('activity')
        trainer_id = request.args.get('trainer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        with session_scope() as session:
            query = session.query(TrainingRecord).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            # Apply filters
            if building:
                query = query.filter_by(building=building)
            
            if activity:
                query = query.filter_by(activity=activity)
            
            if trainer_id:
                query = query.filter_by(trainer_id=trainer_id)
            
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(TrainingRecord.training_date >= start_dt)
                except ValueError:
                    return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    query = query.filter(TrainingRecord.training_date <= end_dt)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
            
            records = query.order_by(TrainingRecord.training_date.desc()).all()
            
            # Enrich with trainer name
            result = []
            for record in records:
                trainer = session.query(User).filter_by(id=record.trainer_id).first()
                record_dict = record.to_dict()
                record_dict['trainer_name'] = trainer.full_name if trainer else "Unknown"
                result.append(record_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "records": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching training records: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch training records: {str(e)}"}), 500


@training_register_bp.route('/api/training-records/<int:record_id>', methods=['GET'])
@jwt_required()
@project_access_required
def get_training_record(record_id):
    """Get details of a specific training record."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            record = session.query(TrainingRecord).filter_by(
                id=record_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not record:
                return jsonify({"error": "Training record not found"}), 404
            
            # Enrich with trainer details
            trainer = session.query(User).filter_by(id=record.trainer_id).first()
            record_dict = record.to_dict()
            record_dict['trainer_name'] = trainer.full_name if trainer else "Unknown"
            record_dict['trainer_email'] = trainer.email if trainer else None
            
            return jsonify({
                "success": True,
                "record": record_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching training record: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch training record: {str(e)}"}), 500


@training_register_bp.route('/api/training-records/<int:record_id>/photo', methods=['GET'])
@jwt_required()
@project_access_required
def get_training_photo(record_id):
    """Serve training photo."""
    try:
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            record = session.query(TrainingRecord).filter_by(
                id=record_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not record:
                return jsonify({"error": "Training record not found"}), 404
            
            if not record.photo_data:
                return jsonify({"error": "No photo available"}), 404
            
            return send_file(
                BytesIO(record.photo_data),
                mimetype=record.photo_mimetype or 'image/jpeg',
                as_attachment=False,
                download_name=record.photo_filename or f"training_{record_id}.jpg"
            )
    
    except Exception as e:
        print(f"Error serving training photo: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to serve photo: {str(e)}"}), 500


@training_register_bp.route('/api/training-records', methods=['POST'])
@jwt_required()
@project_access_required
def create_training_record():
    """
    Create new training record with photo.
    
    Form Data:
    - project_id (required): Project ID
    - photo (required): Training photo file
    - trainee_names (required): JSON array of trainee names ["Name1", "Name2"]
    - building (required): Building/location name
    - activity (required): Activity type (Blockwork, Gypsum, Plastering, etc.)
    - training_date (optional): Date of training (YYYY-MM-DD HH:MM:SS), defaults to now
    - training_topic (required): Topic/title of training
    - duration_minutes (optional): Duration in minutes
    - remarks (optional): Additional remarks
    
    Returns:
    - Created training record object
    """
    try:
        user_id = get_current_user_id()
        
        # Get form data
        project_id = request.form.get('project_id', type=int)
        trainee_names = request.form.get('trainee_names')  # JSON string
        building = request.form.get('building')
        activity = request.form.get('activity')
        training_topic = request.form.get('training_topic')
        training_date_str = request.form.get('training_date')
        duration_minutes = request.form.get('duration_minutes', type=int)
        remarks = request.form.get('remarks')
        
        # Validate required fields
        if not all([project_id, trainee_names, building, activity, training_topic]):
            return jsonify({"error": "Missing required fields: project_id, trainee_names, building, activity, training_topic"}), 400
        
        # Validate and parse trainee names
        import json
        try:
            trainee_list = json.loads(trainee_names)
            if not isinstance(trainee_list, list) or len(trainee_list) == 0:
                return jsonify({"error": "trainee_names must be a non-empty JSON array"}), 400
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid trainee_names format. Must be JSON array"}), 400
        
        # Get and validate photo
        if 'photo' not in request.files:
            return jsonify({"error": "Photo is required"}), 400
        
        photo_file = request.files['photo']
        if photo_file.filename == '':
            return jsonify({"error": "No photo selected"}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        file_ext = photo_file.filename.rsplit('.', 1)[1].lower() if '.' in photo_file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}), 400
        
        # Read photo data
        photo_data = photo_file.read()
        
        # Validate file size (max 10MB)
        if len(photo_data) > 10 * 1024 * 1024:
            return jsonify({"error": "Photo size exceeds 10MB limit"}), 400
        
        # Parse training date or use current timestamp
        if training_date_str:
            try:
                training_date = datetime.strptime(training_date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    training_date = datetime.strptime(training_date_str, '%Y-%m-%d')
                except ValueError:
                    return jsonify({"error": "Invalid training_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
        else:
            training_date = datetime.utcnow()
        
        # Create training record
        with session_scope() as session:
            # Verify project exists
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
            
            new_record = TrainingRecord(
                project_id=project_id,
                trainer_id=user_id,
                training_date=training_date,
                training_topic=training_topic,
                trainee_names_json=trainee_names,  # Store as JSON string
                building=building,
                activity=activity,
                duration_minutes=duration_minutes,
                photo_filename=photo_file.filename,
                photo_data=photo_data,
                photo_mimetype=photo_file.content_type,
                remarks=remarks
            )
            
            session.add(new_record)
            session.flush()
            
            # Get trainer details for response
            trainer = session.query(User).filter_by(id=user_id).first()
            record_dict = new_record.to_dict()
            record_dict['trainer_name'] = trainer.full_name if trainer else "Unknown"
            
            return jsonify({
                "success": True,
                "message": "Training record created successfully",
                "record": record_dict
            }), 201
    
    except Exception as e:
        print(f"Error creating training record: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create training record: {str(e)}"}), 500


@training_register_bp.route('/api/training-records/<int:record_id>', methods=['PUT'])
@jwt_required()
@project_access_required
def update_training_record(record_id):
    """
    Update training record details.
    Can update trainee names, building, activity, remarks, etc.
    Cannot update photo (delete and recreate for new photo).
    """
    try:
        user_id = get_current_user_id()
        project_id = request.form.get('project_id', type=int) if request.form else request.json.get('project_id')
        
        data = request.json if request.is_json else request.form.to_dict()
        
        with session_scope() as session:
            record = session.query(TrainingRecord).filter_by(
                id=record_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not record:
                return jsonify({"error": "Training record not found"}), 404
            
            # Only trainer or QM can update
            membership = session.query(ProjectMembership).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if record.trainer_id != user_id and membership.role != 'Quality Manager':
                return jsonify({"error": "Only the trainer or Quality Manager can update this record"}), 403
            
            # Update allowed fields
            if 'trainee_names' in data:
                import json
                try:
                    trainee_list = json.loads(data['trainee_names']) if isinstance(data['trainee_names'], str) else data['trainee_names']
                    if not isinstance(trainee_list, list) or len(trainee_list) == 0:
                        return jsonify({"error": "trainee_names must be a non-empty array"}), 400
                    record.trainee_names_json = json.dumps(trainee_list)
                except (json.JSONDecodeError, TypeError):
                    return jsonify({"error": "Invalid trainee_names format"}), 400
            
            if 'building' in data:
                record.building = data['building']
            
            if 'activity' in data:
                record.activity = data['activity']
            
            if 'training_topic' in data:
                record.training_topic = data['training_topic']
            
            if 'duration_minutes' in data:
                record.duration_minutes = int(data['duration_minutes']) if data['duration_minutes'] else None
            
            if 'remarks' in data:
                record.remarks = data['remarks']
            
            record.updated_at = datetime.utcnow()
            session.flush()
            
            # Get updated record with trainer details
            trainer = session.query(User).filter_by(id=record.trainer_id).first()
            record_dict = record.to_dict()
            record_dict['trainer_name'] = trainer.full_name if trainer else "Unknown"
            
            return jsonify({
                "success": True,
                "message": "Training record updated successfully",
                "record": record_dict
            }), 200
    
    except Exception as e:
        print(f"Error updating training record: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update training record: {str(e)}"}), 500


@training_register_bp.route('/api/training-records/<int:record_id>', methods=['DELETE'])
@jwt_required()
@quality_manager_required
def delete_training_record(record_id):
    """
    Soft delete training record.
    Only Quality Manager can delete records.
    """
    try:
        user_id = get_current_user_id()
        project_id = request.args.get('project_id', type=int)
        
        with session_scope() as session:
            record = session.query(TrainingRecord).filter_by(
                id=record_id,
                project_id=project_id,
                is_deleted=False
            ).first()
            
            if not record:
                return jsonify({"error": "Training record not found"}), 404
            
            # Soft delete
            record.is_deleted = True
            record.deleted_at = datetime.utcnow()
            record.deleted_by = user_id
            
            session.flush()
            
            return jsonify({
                "success": True,
                "message": "Training record deleted successfully"
            }), 200
    
    except Exception as e:
        print(f"Error deleting training record: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete training record: {str(e)}"}), 500


@training_register_bp.route('/api/training-records/stats', methods=['GET'])
@jwt_required()
@project_access_required
def get_training_stats():
    """
    Get training statistics for a project.
    
    Query Parameters:
    - project_id (required): Project ID
    - start_date (optional): Stats from this date
    - end_date (optional): Stats until this date
    
    Returns:
    - Total trainings count
    - Total trainees count
    - Trainings by activity
    - Trainings by building
    - Recent trainings
    """
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        with session_scope() as session:
            query = session.query(TrainingRecord).filter_by(
                project_id=project_id,
                is_deleted=False
            )
            
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(TrainingRecord.training_date >= start_dt)
                except ValueError:
                    return jsonify({"error": "Invalid start_date format"}), 400
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    query = query.filter(TrainingRecord.training_date <= end_dt)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format"}), 400
            
            records = query.all()
            
            # Calculate statistics
            import json
            total_trainings = len(records)
            total_trainees = 0
            activity_counts = {}
            building_counts = {}
            
            for record in records:
                # Count trainees
                try:
                    trainees = json.loads(record.trainee_names_json)
                    total_trainees += len(trainees)
                except:
                    pass
                
                # Count by activity
                activity_counts[record.activity] = activity_counts.get(record.activity, 0) + 1
                
                # Count by building
                building_counts[record.building] = building_counts.get(record.building, 0) + 1
            
            # Get recent trainings
            recent = query.order_by(TrainingRecord.training_date.desc()).limit(5).all()
            recent_list = []
            for record in recent:
                trainer = session.query(User).filter_by(id=record.trainer_id).first()
                record_dict = record.to_dict()
                record_dict['trainer_name'] = trainer.full_name if trainer else "Unknown"
                recent_list.append(record_dict)
            
            return jsonify({
                "success": True,
                "stats": {
                    "total_trainings": total_trainings,
                    "total_trainees": total_trainees,
                    "by_activity": activity_counts,
                    "by_building": building_counts,
                    "recent_trainings": recent_list
                }
            }), 200
    
    except Exception as e:
        print(f"Error fetching training stats: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch statistics: {str(e)}"}), 500
