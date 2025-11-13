"""
Geo-Fencing API
Endpoints for managing project geofences and viewing location verification logs
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from server.db import db
from server.models import User, Company, Project
from server.geofence_models import GeofenceLocation, LocationVerification
from flask_jwt_extended import jwt_required, get_jwt_identity

geofence_bp = Blueprint('geofence', __name__)

def get_current_user_id():
    """Extract user ID from JWT token"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('id')
    return identity

def admin_required(f):
    """Decorator to ensure user is Admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ========================================
# 1. CREATE/UPDATE GEOFENCE
# ========================================

@geofence_bp.route('/api/geofence', methods=['POST'])
@admin_required
def create_geofence():
    """
    Create or update project geofence
    Body: {
        project_id, location_name, location_description,
        center_latitude, center_longitude,
        radius_meters (default 100),
        tolerance_meters (default 20),
        address, city, state, pincode,
        strict_mode (default true)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        required = ['project_id', 'location_name', 'center_latitude', 'center_longitude']
        if not all(field in data for field in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400
        
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if geofence already exists for this project
        geofence = GeofenceLocation.query.filter_by(
            project_id=data['project_id'],
            is_deleted=False
        ).first()
        
        if geofence:
            # UPDATE existing geofence
            geofence.location_name = data['location_name']
            geofence.location_description = data.get('location_description')
            geofence.center_latitude = data['center_latitude']
            geofence.center_longitude = data['center_longitude']
            geofence.radius_meters = data.get('radius_meters', 100)
            geofence.tolerance_meters = data.get('tolerance_meters', 20)
            geofence.address = data.get('address')
            geofence.city = data.get('city')
            geofence.state = data.get('state')
            geofence.pincode = data.get('pincode')
            geofence.strict_mode = data.get('strict_mode', True)
            geofence.is_active = data.get('is_active', True)
            geofence.updated_by = user_id
            
            message = 'Geofence updated successfully'
        else:
            # CREATE new geofence
            geofence = GeofenceLocation(
                company_id=project.company_id,
                project_id=data['project_id'],
                location_name=data['location_name'],
                location_description=data.get('location_description'),
                center_latitude=data['center_latitude'],
                center_longitude=data['center_longitude'],
                radius_meters=data.get('radius_meters', 100),
                tolerance_meters=data.get('tolerance_meters', 20),
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                strict_mode=data.get('strict_mode', True),
                is_active=data.get('is_active', True),
                created_by=user_id
            )
            db.session.add(geofence)
            message = 'Geofence created successfully'
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'geofence': geofence.to_dict()
        }), 201 if not geofence else 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 2. GET GEOFENCE BY PROJECT
# ========================================

@geofence_bp.route('/api/geofence/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_geofence(project_id):
    """Get geofence configuration for a specific project"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        geofence = GeofenceLocation.query.filter_by(
            project_id=project_id,
            company_id=user.company_id,
            is_deleted=False
        ).first()
        
        if not geofence:
            return jsonify({
                'message': 'No geofence configured for this project',
                'geofence': None
            }), 200
        
        return jsonify({'geofence': geofence.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 3. LIST ALL GEOFENCES
# ========================================

@geofence_bp.route('/api/geofence', methods=['GET'])
@jwt_required()
def list_geofences():
    """List all geofences for company"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        geofences = GeofenceLocation.query.filter_by(
            company_id=user.company_id,
            is_deleted=False
        ).all()
        
        return jsonify({
            'geofences': [g.to_dict() for g in geofences],
            'count': len(geofences)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 4. VERIFY LOCATION (Manual Check)
# ========================================

@geofence_bp.route('/api/geofence/verify', methods=['POST'])
@jwt_required()
def verify_location():
    """
    Manually verify if location is within geofence
    Body: {
        project_id, latitude, longitude
    }
    Returns: verification result without enforcing access control
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        data = request.get_json()
        
        required = ['project_id', 'latitude', 'longitude']
        if not all(field in data for field in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400
        
        project_id = data['project_id']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        geofence = GeofenceLocation.query.filter_by(
            project_id=project_id,
            company_id=user.company_id,
            is_deleted=False
        ).first()
        
        if not geofence:
            return jsonify({
                'verified': True,
                'message': 'No geofence configured for this project',
                'distance': None
            }), 200
        
        # Check location
        is_within, distance = geofence.is_within_geofence(latitude, longitude)
        
        return jsonify({
            'verified': is_within,
            'distance_from_center': round(distance, 2),
            'allowed_radius': geofence.radius_meters + geofence.tolerance_meters,
            'geofence': {
                'location_name': geofence.location_name,
                'center_latitude': float(geofence.center_latitude),
                'center_longitude': float(geofence.center_longitude),
                'radius_meters': geofence.radius_meters,
                'tolerance_meters': geofence.tolerance_meters
            },
            'status': 'WITHIN_GEOFENCE' if is_within else 'OUTSIDE_GEOFENCE',
            'message': 'You are within the site boundary' if is_within else f'You are {round(distance - (geofence.radius_meters + geofence.tolerance_meters), 0)} meters outside the site boundary'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 5. LOCATION VERIFICATION LOGS
# ========================================

@geofence_bp.route('/api/geofence/logs', methods=['GET'])
@jwt_required()
def get_verification_logs():
    """
    Get location verification logs
    Query params: project_id, user_id, verified_only, failed_only, start_date, end_date, limit
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = LocationVerification.query.filter(
            LocationVerification.company_id == user.company_id
        )
        
        # Filters
        if request.args.get('project_id'):
            query = query.filter(LocationVerification.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('user_id'):
            query = query.filter(LocationVerification.user_id == request.args.get('user_id', type=int))
        
        if request.args.get('verified_only') == 'true':
            query = query.filter(LocationVerification.is_verified == True)
        
        if request.args.get('failed_only') == 'true':
            query = query.filter(LocationVerification.is_verified == False)
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(LocationVerification.verified_at >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(LocationVerification.verified_at <= end_date)
        
        # Limit results
        limit = request.args.get('limit', default=100, type=int)
        query = query.order_by(LocationVerification.verified_at.desc()).limit(limit)
        
        logs = query.all()
        
        # Statistics
        total_attempts = len(logs)
        verified = sum(1 for log in logs if log.is_verified)
        failed = total_attempts - verified
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'count': total_attempts,
            'statistics': {
                'total_attempts': total_attempts,
                'verified': verified,
                'failed': failed,
                'success_rate': round((verified / total_attempts * 100), 2) if total_attempts > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 6. VIOLATION ALERTS
# ========================================

@geofence_bp.route('/api/geofence/violations', methods=['GET'])
@jwt_required()
def get_violations():
    """
    Get failed location verification attempts (potential violations)
    Query params: project_id, days (default 7)
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        days = request.args.get('days', default=7, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        query = LocationVerification.query.filter(
            LocationVerification.company_id == user.company_id,
            LocationVerification.is_verified == False,
            LocationVerification.verified_at >= start_date
        )
        
        if request.args.get('project_id'):
            query = query.filter(LocationVerification.project_id == request.args.get('project_id', type=int))
        
        violations = query.order_by(LocationVerification.verified_at.desc()).all()
        
        # Group by user
        user_violations = {}
        for violation in violations:
            user_name = violation.user.name if violation.user else "Unknown"
            if user_name not in user_violations:
                user_violations[user_name] = 0
            user_violations[user_name] += 1
        
        return jsonify({
            'violations': [v.to_dict() for v in violations],
            'count': len(violations),
            'by_user': user_violations,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 7. UPDATE GEOFENCE STATUS
# ========================================

@geofence_bp.route('/api/geofence/<int:geofence_id>/toggle', methods=['PUT'])
@admin_required
def toggle_geofence(geofence_id):
    """
    Enable/disable geofence
    Body: {
        is_active: true/false,
        strict_mode: true/false (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        geofence = GeofenceLocation.query.get(geofence_id)
        if not geofence or geofence.is_deleted:
            return jsonify({'error': 'Geofence not found'}), 404
        
        geofence.is_active = data.get('is_active', geofence.is_active)
        
        if 'strict_mode' in data:
            geofence.strict_mode = data['strict_mode']
        
        geofence.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'message': f'Geofence {"enabled" if geofence.is_active else "disabled"} successfully',
            'geofence': geofence.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 8. DELETE GEOFENCE
# ========================================

@geofence_bp.route('/api/geofence/<int:geofence_id>', methods=['DELETE'])
@admin_required
def delete_geofence(geofence_id):
    """Soft delete geofence (Admin only)"""
    try:
        user_id = get_current_user_id()
        
        geofence = GeofenceLocation.query.get(geofence_id)
        if not geofence or geofence.is_deleted:
            return jsonify({'error': 'Geofence not found'}), 404
        
        geofence.is_deleted = True
        geofence.is_active = False
        geofence.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({'message': 'Geofence deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
