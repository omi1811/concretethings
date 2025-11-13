"""
Multi-App Subscription Middleware

Implements app visibility control based on company subscriptions:
- Safety-only companies: Only see safety features
- Concrete-only companies: Only see QMS/concrete features  
- Both apps: See all features + cross-app integrations (training QR attendance)
"""

from flask import request, jsonify
from functools import wraps
import json as json_module

from flask_jwt_extended import get_jwt_identity

try:
    from .db import session_scope
    from .models import User, Company
except ImportError:
    from db import session_scope
    from models import User, Company


def get_current_user_id():
    """Extract user_id from JWT identity."""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('user_id')
    return int(identity)

import logging
logger = logging.getLogger(__name__)


def get_user_subscribed_apps(user_id):
    """Get list of apps the user's company has subscribed to"""
    with session_scope() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user or not user.company_id:
            return []
        
        company = session.query(Company).filter_by(id=user.company_id).first()
        if not company:
            return []
        
        try:
            apps = json_module.loads(company.subscribed_apps) if company.subscribed_apps else ["safety", "concrete"]
            return apps
        except:
            return ["safety", "concrete"]  # Default to both


def require_app(app_name):
    """
    Decorator to restrict endpoint access based on app subscription
    
    Usage:
        @require_app('safety')
        def safety_endpoint():
            ...
        
        @require_app('concrete')
        def concrete_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_current_user_id()
                subscribed_apps = get_user_subscribed_apps(user_id)
                
                if app_name not in subscribed_apps:
                    return jsonify({
                        "error": f"Access denied. Your company has not subscribed to the {app_name} app.",
                        "subscribedApps": subscribed_apps
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Subscription check error: {str(e)}")
                return jsonify({"error": "Subscription verification failed"}), 500
        
        return decorated_function
    return decorator


def require_both_apps():
    """
    Decorator for cross-app features (only available when company has BOTH apps)
    
    Example: Quality training with worker QR attendance requires both safety and concrete apps
    
    Usage:
        @require_both_apps()
        def training_qr_attendance():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_current_user_id()
                subscribed_apps = get_user_subscribed_apps(user_id)
                
                if "safety" not in subscribed_apps or "concrete" not in subscribed_apps:
                    return jsonify({
                        "error": "This feature requires both Safety and Concrete app subscriptions.",
                        "subscribedApps": subscribed_apps,
                        "requiredApps": ["safety", "concrete"]
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Subscription check error: {str(e)}")
                return jsonify({"error": "Subscription verification failed"}), 500
        
        return decorated_function
    return decorator


def get_user_app_access():
    """
    Get current user's app access details
    
    Returns:
    {
        "subscribedApps": ["safety", "concrete"],
        "hasSafety": true,
        "hasConcrete": true,
        "hasBoth": true,
        "availableFeatures": {
            "safety": [...],
            "concrete": [...],
            "crossApp": [...]
        }
    }
    """
    try:
        user_id = get_current_user_id()
        subscribed_apps = get_user_subscribed_apps(user_id)
        
        has_safety = "safety" in subscribed_apps
        has_concrete = "concrete" in subscribed_apps
        has_both = has_safety and has_concrete
        
        # Define available features based on subscriptions
        features = {
            "safety": [],
            "concrete": [],
            "crossApp": []
        }
        
        if has_safety:
            features["safety"] = [
                "safety_observations",
                "safety_workers",
                "safety_nc",
                "permit_to_work",
                "toolbox_talks"
            ]
        
        if has_concrete:
            features["concrete"] = [
                "mix_designs",
                "batches",
                "cube_tests",
                "pour_activities",
                "material_vehicle_register",
                "quality_training"
            ]
        
        if has_both:
            features["crossApp"] = [
                "training_qr_attendance",  # QR attendance for quality training (requires both apps)
                "integrated_dashboards",
                "cross_app_reports"
            ]
        
        return {
            "subscribedApps": subscribed_apps,
            "hasSafety": has_safety,
            "hasConcrete": has_concrete,
            "hasBoth": has_both,
            "availableFeatures": features
        }
        
    except Exception as e:
        logger.error(f"Error getting app access: {str(e)}")
        return {
            "subscribedApps": [],
            "hasSafety": False,
            "hasConcrete": False,
            "hasBoth": False,
            "availableFeatures": {"safety": [], "concrete": [], "crossApp": []}
        }
