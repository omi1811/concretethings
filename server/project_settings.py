"""
Project Settings API
Manage project-specific configurations including material vehicle addon settings
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_

from .models import db
from .models import ProjectSettings, Project, ProjectMembership, User

project_settings_bp = Blueprint('project_settings', __name__, url_prefix='/api/project-settings')


def check_admin_permission(user_id, project_id):
    """Check if user is project admin"""
    membership = db.session.query(ProjectMembership).filter(
        and_(
            ProjectMembership.user_id == user_id,
            ProjectMembership.project_id == project_id,
            ProjectMembership.is_active == True
        )
    ).first()
    
    if not membership:
        return False, "User not assigned to this project"
    
    # Only ProjectAdmin can manage settings
    if membership.role != 'ProjectAdmin':
        return False, "Only Project Admins can manage settings"
    
    return True, membership.role


@project_settings_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_settings(project_id):
    """Get settings for a project"""
    try:
        user_id = get_jwt_identity()
        
        # Check user has access to project
        membership = db.session.query(ProjectMembership).filter(
            and_(
                ProjectMembership.user_id == user_id,
                ProjectMembership.project_id == project_id,
                ProjectMembership.is_active == True
            )
        ).first()
        
        if not membership:
            return jsonify({"error": "Access denied"}), 403
        
        # Get or create settings
        settings = db.session.query(ProjectSettings).filter(
            ProjectSettings.project_id == project_id
        ).first()
        
        if not settings:
            # Create default settings
            settings = ProjectSettings(
                project_id=project_id,
                enable_material_vehicle_addon=False,
                vehicle_allowed_time_hours=3.0,
                send_time_warnings=True,
                enable_test_reminders=True,
                reminder_time="09:00",
                notify_project_admins=True,
                notify_quality_engineers=True,
                enable_whatsapp_notifications=False,
                enable_email_notifications=True
            )
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "settings": settings.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error fetching project settings: {str(e)}")
        return jsonify({"error": str(e)}), 500


@project_settings_bp.route('/<int:project_id>/update', methods=['PUT'])
@jwt_required()
def update_project_settings(project_id):
    """Update project settings (ProjectAdmin only)"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Check admin permission
        has_permission, role = check_admin_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Get or create settings
        settings = db.session.query(ProjectSettings).filter(
            ProjectSettings.project_id == project_id
        ).first()
        
        if not settings:
            settings = ProjectSettings(project_id=project_id)
            db.session.add(settings)
        
        # Update fields
        if 'enableMaterialVehicleAddon' in data:
            settings.enable_material_vehicle_addon = data['enableMaterialVehicleAddon']
        
        if 'vehicleAllowedTimeHours' in data:
            settings.vehicle_allowed_time_hours = float(data['vehicleAllowedTimeHours'])
        
        if 'sendTimeWarnings' in data:
            settings.send_time_warnings = data['sendTimeWarnings']
        
        if 'enableTestReminders' in data:
            settings.enable_test_reminders = data['enableTestReminders']
        
        if 'reminderTime' in data:
            settings.reminder_time = data['reminderTime']
        
        if 'notifyProjectAdmins' in data:
            settings.notify_project_admins = data['notifyProjectAdmins']
        
        if 'notifyQualityEngineers' in data:
            settings.notify_quality_engineers = data['notifyQualityEngineers']
        
        if 'enableWhatsappNotifications' in data:
            settings.enable_whatsapp_notifications = data['enableWhatsappNotifications']
        
        if 'enableEmailNotifications' in data:
            settings.enable_email_notifications = data['enableEmailNotifications']
        
        settings.updated_by = user_id
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Project settings updated successfully",
            "settings": settings.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating project settings: {str(e)}")
        return jsonify({"error": str(e)}), 500


@project_settings_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_settings():
    """Get settings for all projects user has access to"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's projects
        memberships = db.session.query(ProjectMembership).filter(
            and_(
                ProjectMembership.user_id == user_id,
                ProjectMembership.is_active == True
            )
        ).all()
        
        project_ids = [m.project_id for m in memberships]
        
        # Get settings for all projects
        settings_list = db.session.query(ProjectSettings).filter(
            ProjectSettings.project_id.in_(project_ids)
        ).all()
        
        return jsonify({
            "success": True,
            "settings": [s.to_dict() for s in settings_list]
        }), 200
        
    except Exception as e:
        print(f"Error fetching all settings: {str(e)}")
        return jsonify({"error": str(e)}), 500
