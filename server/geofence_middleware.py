"""
Geo-Fencing Middleware
Location-based access control for data entry endpoints
Ensures users are physically present on-site
"""

from flask import request, jsonify
from functools import wraps
from server.db import db
from server.models import User
from server.geofence_models import GeofenceLocation, LocationVerification
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
import uuid

def get_current_user_id():
    """Extract user ID from JWT token"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('id')
    return identity

def require_location(action_name):
    """
    Decorator to enforce geofence verification
    Usage: @require_location("TBT_CREATE")
    
    Expects request body or headers to contain:
    - latitude: float
    - longitude: float
    - project_id: int (for project-specific geofence)
    - gps_accuracy: float (optional, in meters)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_current_user_id()
                if not user_id:
                    return jsonify({'error': 'Unauthorized. Please login.'}), 401
                
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                # Get location data from request
                data = request.get_json() or {}
                
                # Also check headers for location (mobile apps may send in headers)
                latitude = data.get('latitude') or request.headers.get('X-Latitude')
                longitude = data.get('longitude') or request.headers.get('X-Longitude')
                project_id = data.get('project_id') or request.headers.get('X-Project-ID')
                gps_accuracy = data.get('gps_accuracy') or request.headers.get('X-GPS-Accuracy')
                
                if not latitude or not longitude:
                    return jsonify({
                        'error': 'Location required. Please enable GPS and provide latitude/longitude.',
                        'error_code': 'LOCATION_MISSING'
                    }), 400
                
                if not project_id:
                    return jsonify({
                        'error': 'Project ID required for location verification.',
                        'error_code': 'PROJECT_ID_MISSING'
                    }), 400
                
                # Convert to proper types
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                    project_id = int(project_id)
                    gps_accuracy = float(gps_accuracy) if gps_accuracy else None
                except (ValueError, TypeError):
                    return jsonify({
                        'error': 'Invalid location data format.',
                        'error_code': 'INVALID_LOCATION_FORMAT'
                    }), 400
                
                # Get geofence for project
                geofence = GeofenceLocation.query.filter_by(
                    project_id=project_id,
                    is_active=True,
                    is_deleted=False
                ).first()
                
                if not geofence:
                    # No geofence configured - allow (optional enforcement)
                    # OR you can make it strict and reject if no geofence
                    # For now, we'll log and allow
                    _log_verification(
                        user_id=user_id,
                        company_id=user.company_id,
                        project_id=project_id,
                        latitude=latitude,
                        longitude=longitude,
                        gps_accuracy=gps_accuracy,
                        is_verified=True,
                        distance=None,
                        allowed_radius=None,
                        action=action_name,
                        endpoint=request.endpoint,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent'),
                        device_info=request.headers.get('X-Device-Info')
                    )
                    
                    # Proceed without geofence check
                    return f(*args, **kwargs)
                
                # Verify location
                is_within, distance = geofence.is_within_geofence(latitude, longitude)
                
                # Log verification attempt
                _log_verification(
                    user_id=user_id,
                    company_id=user.company_id,
                    project_id=project_id,
                    latitude=latitude,
                    longitude=longitude,
                    gps_accuracy=gps_accuracy,
                    is_verified=is_within,
                    distance=distance,
                    allowed_radius=geofence.radius_meters + geofence.tolerance_meters,
                    action=action_name,
                    endpoint=request.endpoint,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    device_info=request.headers.get('X-Device-Info')
                )
                
                # Check if within geofence
                if not is_within:
                    if geofence.strict_mode:
                        # REJECT - User is outside geofence
                        return jsonify({
                            'error': 'Access denied. You must be physically present on-site to perform this action.',
                            'error_code': 'OUTSIDE_GEOFENCE',
                            'details': {
                                'your_distance_from_site': f"{distance:.0f} meters",
                                'allowed_distance': f"{geofence.radius_meters + geofence.tolerance_meters} meters",
                                'please_move_closer': f"{distance - (geofence.radius_meters + geofence.tolerance_meters):.0f} meters",
                                'site_location': geofence.location_name,
                                'gps_accuracy': f"{gps_accuracy:.0f} meters" if gps_accuracy else "Unknown"
                            }
                        }), 403
                    else:
                        # WARNING MODE - Log but allow
                        # You can add a warning message in response
                        pass
                
                # Location verified - proceed with original function
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': f'Location verification failed: {str(e)}',
                    'error_code': 'VERIFICATION_ERROR'
                }), 500
        
        return decorated_function
    return decorator


def _log_verification(user_id, company_id, project_id, latitude, longitude, 
                      gps_accuracy, is_verified, distance, allowed_radius, 
                      action, endpoint, ip_address, user_agent, device_info):
    """
    Internal function to log location verification attempt
    """
    try:
        verification = LocationVerification(
            company_id=company_id,
            project_id=project_id,
            user_id=user_id,
            submitted_latitude=latitude,
            submitted_longitude=longitude,
            submitted_accuracy=gps_accuracy,
            is_verified=is_verified,
            distance_from_center=distance,
            allowed_radius=allowed_radius,
            action=action,
            endpoint=endpoint,
            request_id=str(uuid.uuid4()),
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            verified_at=datetime.utcnow()
        )
        
        db.session.add(verification)
        db.session.commit()
        
    except Exception as e:
        # Don't fail the request if logging fails
        print(f"Warning: Failed to log location verification: {str(e)}")
        db.session.rollback()


# ========================================
# EXAMPLE USAGE IN ENDPOINTS
# ========================================

"""
Example 1: Protect TBT creation

from server.geofence_middleware import require_location

@tbt_bp.route('/api/tbt', methods=['POST'])
@jwt_required()
@require_location("TBT_CREATE")
def create_tbt():
    # Your existing code
    # Location is already verified before reaching here
    ...

Example 2: Protect NC raising

@nc_bp.route('/api/safety-nc', methods=['POST'])
@jwt_required()
@require_location("NC_RAISE")
def raise_nc():
    # Your existing code
    ...

Example 3: Protect PTW submission

@ptw_bp.route('/api/permit-to-work', methods=['POST'])
@jwt_required()
@require_location("PTW_SUBMIT")
def submit_ptw():
    # Your existing code
    ...

Example 4: Protect Batch entry

@batch_bp.route('/api/batches', methods=['POST'])
@jwt_required()
@require_location("BATCH_ENTRY")
def create_batch():
    # Your existing code
    ...

Example 5: Protect Vehicle entry

@vehicle_bp.route('/api/material-vehicle-register', methods=['POST'])
@jwt_required()
@require_location("VEHICLE_ENTRY")
def record_vehicle():
    # Your existing code
    ...
"""
