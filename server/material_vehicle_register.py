"""
Material Vehicle Register API
For watchmen/security to log all material vehicle entries
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload
import json

from .models import (
    MaterialVehicleRegister, User, Project, ProjectMembership,
    ProjectSettings, BatchRegister, db
)

material_vehicle_bp = Blueprint('material_vehicle', __name__, url_prefix='/api/material-vehicles')


def check_watchman_permission(user_id, project_id):
    """Check if user is watchman or has higher permissions"""
    membership = db.session.query(ProjectMembership).filter(
        and_(
            ProjectMembership.user_id == user_id,
            ProjectMembership.project_id == project_id,
            ProjectMembership.is_active == True
        )
    ).first()
    
    if not membership:
        return False, "User not assigned to this project"
    
    # Watchman, DataEntry, or higher roles can access
    allowed_roles = ['ProjectAdmin', 'QualityManager', 'QualityEngineer', 'SiteEngineer', 'DataEntry', 'Watchman']
    if membership.role not in allowed_roles:
        return False, "Insufficient permissions"
    
    return True, membership.role


@material_vehicle_bp.route('/create', methods=['POST'])
@jwt_required()
def create_vehicle_entry():
    """
    Create new vehicle entry in material register
    Watchman can add: vehicle number, material type, supplier, driver details, photos
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        project_id = data.get('projectId')
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Get project settings for time limits
        settings = db.session.query(ProjectSettings).filter(
            ProjectSettings.project_id == project_id
        ).first()
        
        allowed_time_hours = settings.vehicle_allowed_time_hours if settings else 3.0
        
        # Create vehicle entry
        vehicle_entry = MaterialVehicleRegister(
            project_id=project_id,
            vehicle_number=data.get('vehicleNumber', '').strip().upper(),
            vehicle_type=data.get('vehicleType'),
            material_type=data.get('materialType', 'Concrete'),
            supplier_name=data.get('supplierName'),
            challan_number=data.get('challanNumber'),
            driver_name=data.get('driverName'),
            driver_phone=data.get('driverPhone'),
            driver_license=data.get('driverLicense'),
            entry_time=datetime.fromisoformat(data['entryTime'].replace('Z', '+00:00')) if data.get('entryTime') else datetime.utcnow(),
            allowed_time_hours=allowed_time_hours,
            purpose=data.get('purpose'),
            remarks=data.get('remarks'),
            created_by=user_id,
            status='on_site'
        )
        
        # Handle photos
        if data.get('photos'):
            vehicle_entry.photos = json.dumps(data['photos'])
        
        db.session.add(vehicle_entry)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Vehicle entry created successfully",
            "vehicleEntry": vehicle_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating vehicle entry: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/list', methods=['GET'])
@jwt_required()
def list_vehicle_entries():
    """
    List all vehicle entries for a project
    Supports filtering by status, date range, material type
    """
    try:
        user_id = get_jwt_identity()
        project_id = request.args.get('projectId', type=int)
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Build query
        query = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.project_id == project_id
        )
        
        # Filters
        status = request.args.get('status')
        if status:
            query = query.filter(MaterialVehicleRegister.status == status)
        
        material_type = request.args.get('materialType')
        if material_type:
            query = query.filter(MaterialVehicleRegister.material_type == material_type)
        
        date_from = request.args.get('dateFrom')
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(MaterialVehicleRegister.entry_time >= date_from_obj)
        
        date_to = request.args.get('dateTo')
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(MaterialVehicleRegister.entry_time <= date_to_obj)
        
        # Exceeded time limit filter
        exceeded_only = request.args.get('exceededOnly', 'false').lower() == 'true'
        if exceeded_only:
            query = query.filter(MaterialVehicleRegister.exceeded_time_limit == True)
        
        # Order by entry time (newest first)
        query = query.order_by(desc(MaterialVehicleRegister.entry_time))
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('perPage', 50, type=int)
        
        # Manual pagination
        total = query.count()
        offset = (page - 1) * per_page
        items = query.limit(per_page).offset(offset).all()
        pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return jsonify({
            "success": True,
            "vehicleEntries": [entry.to_dict() for entry in items],
            "pagination": {
                "page": page,
                "perPage": per_page,
                "total": total,
                "pages": pages
            }
        }), 200
        
    except Exception as e:
        print(f"Error listing vehicle entries: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_vehicle_entry(entry_id):
    """Get details of a specific vehicle entry"""
    try:
        user_id = get_jwt_identity()
        
        entry = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == entry_id
        ).first()
        
        if not entry:
            return jsonify({"error": "Vehicle entry not found"}), 404
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, entry.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        return jsonify({
            "success": True,
            "vehicleEntry": entry.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error fetching vehicle entry: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/<int:entry_id>/update', methods=['PUT'])
@jwt_required()
def update_vehicle_entry(entry_id):
    """
    Update vehicle entry
    Watchman can update: exit time, photos, remarks
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        entry = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == entry_id
        ).first()
        
        if not entry:
            return jsonify({"error": "Vehicle entry not found"}), 404
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, entry.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Update fields
        if 'exitTime' in data and data['exitTime']:
            entry.exit_time = datetime.fromisoformat(data['exitTime'].replace('Z', '+00:00'))
            entry.status = 'exited'
            
            # Calculate duration
            if entry.entry_time and entry.exit_time:
                duration = entry.exit_time - entry.entry_time
                entry.duration_hours = duration.total_seconds() / 3600
        
        if 'photos' in data:
            entry.photos = json.dumps(data['photos'])
        
        if 'remarks' in data:
            entry.remarks = data['remarks']
        
        if 'purpose' in data:
            entry.purpose = data['purpose']
        
        if 'driverName' in data:
            entry.driver_name = data['driverName']
        
        if 'driverPhone' in data:
            entry.driver_phone = data['driverPhone']
        
        if 'supplierName' in data:
            entry.supplier_name = data['supplierName']
        
        if 'challanNumber' in data:
            entry.challan_number = data['challanNumber']
        
        entry.updated_by = user_id
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Vehicle entry updated successfully",
            "vehicleEntry": entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating vehicle entry: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/<int:entry_id>/mark-exit', methods=['POST'])
@jwt_required()
def mark_vehicle_exit(entry_id):
    """Quick endpoint to mark vehicle as exited"""
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        
        entry = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == entry_id
        ).first()
        
        if not entry:
            return jsonify({"error": "Vehicle entry not found"}), 404
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, entry.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        if entry.status == 'exited':
            return jsonify({"error": "Vehicle already marked as exited"}), 400
        
        # Mark as exited
        exit_time = data.get('exitTime')
        if exit_time:
            entry.exit_time = datetime.fromisoformat(exit_time.replace('Z', '+00:00'))
        else:
            entry.exit_time = datetime.utcnow()
        
        entry.status = 'exited'
        
        # Calculate duration
        if entry.entry_time and entry.exit_time:
            duration = entry.exit_time - entry.entry_time
            entry.duration_hours = duration.total_seconds() / 3600
        
        entry.updated_by = user_id
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Vehicle {entry.vehicle_number} marked as exited",
            "vehicleEntry": entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error marking vehicle exit: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/upload-photo', methods=['POST'])
@jwt_required()
def upload_vehicle_photo():
    """
    Upload photos for vehicle entry (MTC, vehicle photo, etc.)
    Stores in uploads/ directory and returns URL
    """
    try:
        user_id = get_jwt_identity()
        
        if 'photo' not in request.files:
            return jsonify({"error": "No photo file provided"}), 400
        
        photo = request.files['photo']
        entry_id = request.form.get('entryId', type=int)
        photo_type = request.form.get('photoType', 'general')  # MTC, vehicle, challan, etc.
        
        if not entry_id:
            return jsonify({"error": "Entry ID required"}), 400
        
        # Check entry exists
        entry = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == entry_id
        ).first()
        
        if not entry:
            return jsonify({"error": "Vehicle entry not found"}), 404
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, entry.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Save photo
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(photo.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"vehicle_{entry_id}_{photo_type}_{timestamp}_{filename}"
        
        upload_folder = 'uploads/vehicle_photos'
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        photo.save(filepath)
        
        # Update entry photos
        photos = []
        if entry.photos:
            try:
                photos = json.loads(entry.photos)
            except:
                photos = []
        
        photos.append({
            "type": photo_type,
            "url": f"/{filepath}",
            "filename": filename,
            "uploadedAt": datetime.utcnow().isoformat(),
            "uploadedBy": user_id
        })
        
        entry.photos = json.dumps(photos)
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Photo uploaded successfully",
            "photo": {
                "type": photo_type,
                "url": f"/{filepath}",
                "filename": filename
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading photo: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/check-time-limits', methods=['POST'])
@jwt_required()
def check_time_limits():
    """
    Background job endpoint: Check vehicles exceeding time limits
    Send notifications to quality engineers
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        project_id = data.get('projectId')
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        # Get project settings
        settings = db.session.query(ProjectSettings).filter(
            ProjectSettings.project_id == project_id
        ).first()
        
        if not settings or not settings.send_time_warnings:
            return jsonify({"success": True, "message": "Time warnings disabled"}), 200
        
        allowed_time_hours = settings.vehicle_allowed_time_hours
        
        # Find RMC vehicles (Concrete only) on site exceeding time limit
        # Time warnings ONLY for RMC vehicles, not for Steel, Cement, Sand, etc.
        cutoff_time = datetime.utcnow() - timedelta(hours=allowed_time_hours)
        
        exceeded_vehicles = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete']),
                MaterialVehicleRegister.status == 'on_site',
                MaterialVehicleRegister.entry_time <= cutoff_time,
                MaterialVehicleRegister.time_warning_sent == False
            )
        ).all()
        
        if not exceeded_vehicles:
            return jsonify({
                "success": True,
                "message": "No vehicles exceeding time limit",
                "count": 0
            }), 200
        
        # Get quality engineers for notification
        quality_engineers = db.session.query(User).join(ProjectMembership).filter(
            and_(
                ProjectMembership.project_id == project_id,
                ProjectMembership.role.in_(['QualityEngineer', 'QualityManager', 'ProjectAdmin']),
                ProjectMembership.is_active == True,
                User.is_active == True
            )
        ).all()
        
        # Send notifications (placeholder - implement actual notification logic)
        from .notifications import send_time_limit_warning
        
        for vehicle in exceeded_vehicles:
            # Calculate how long vehicle has been on site
            time_on_site = datetime.utcnow() - vehicle.entry_time
            hours_on_site = time_on_site.total_seconds() / 3600
            
            # Mark as exceeded
            vehicle.exceeded_time_limit = True
            vehicle.time_warning_sent = True
            vehicle.time_warning_sent_at = datetime.utcnow()
            
            # Send notification
            notification_data = {
                "vehicleNumber": vehicle.vehicle_number,
                "materialType": vehicle.material_type,
                "supplierName": vehicle.supplier_name,
                "entryTime": vehicle.entry_time.isoformat(),
                "hoursOnSite": round(hours_on_site, 2),
                "allowedHours": allowed_time_hours,
                "projectId": project_id
            }
            
            for engineer in quality_engineers:
                send_time_limit_warning(engineer, notification_data)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Sent warnings for {len(exceeded_vehicles)} vehicle(s)",
            "count": len(exceeded_vehicles),
            "vehicles": [v.to_dict() for v in exceeded_vehicles]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error checking time limits: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/link-to-batch', methods=['POST'])
@jwt_required()
def link_vehicle_to_batch():
    """
    Link a material vehicle entry to an RMC batch
    Used by quality engineer when doing bulk entry
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        vehicle_entry_id = data.get('vehicleEntryId')
        batch_id = data.get('batchId')
        
        if not vehicle_entry_id or not batch_id:
            return jsonify({"error": "Vehicle entry ID and batch ID required"}), 400
        
        # Get vehicle entry
        vehicle_entry = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == vehicle_entry_id
        ).first()
        
        if not vehicle_entry:
            return jsonify({"error": "Vehicle entry not found"}), 404
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, vehicle_entry.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Check batch exists
        batch = db.session.query(BatchRegister).filter(
            BatchRegister.id == batch_id
        ).first()
        
        if not batch:
            return jsonify({"error": "Batch not found"}), 404
        
        # Link
        vehicle_entry.linked_batch_id = batch_id
        vehicle_entry.is_linked_to_batch = True
        vehicle_entry.updated_by = user_id
        vehicle_entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Vehicle {vehicle_entry.vehicle_number} linked to batch {batch.batch_number}",
            "vehicleEntry": vehicle_entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error linking vehicle to batch: {str(e)}")
        return jsonify({"error": str(e)}), 500


@material_vehicle_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_vehicle_stats():
    """Get statistics for material vehicle register"""
    try:
        user_id = get_jwt_identity()
        project_id = request.args.get('projectId', type=int)
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        # Check permissions
        has_permission, role = check_watchman_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Get stats
        total_entries = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.project_id == project_id
        ).count()
        
        on_site = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.status == 'on_site'
            )
        ).count()
        
        exited = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.status == 'exited'
            )
        ).count()
        
        exceeded_time = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.exceeded_time_limit == True
            )
        ).count()
        
        linked_to_batches = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.is_linked_to_batch == True
            )
        ).count()
        
        # Today's entries
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_entries = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.entry_time >= today_start
            )
        ).count()
        
        return jsonify({
            "success": True,
            "stats": {
                "totalEntries": total_entries,
                "onSite": on_site,
                "exited": exited,
                "exceededTimeLimit": exceeded_time,
                "linkedToBatches": linked_to_batches,
                "todayEntries": today_entries
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
