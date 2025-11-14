"""
Module access control middleware.
Restricts access to endpoints based on company's subscribed modules.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from .db import session_scope
from .models import User, Company


def require_module(module_name: str):
    """
    Decorator to require company to have subscribed to a specific module.
    Must be used after @jwt_required().
    
    Args:
        module_name: Name of required module (e.g., 'concrete_nc', 'safety_nc')
    
    Usage:
        @app.route('/api/concrete/nc/')
        @jwt_required()
        @require_module('concrete_nc')
        def list_ncs():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            
            with session_scope() as session:
                user = session.query(User).filter_by(id=user_id).first()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                company = session.query(Company).filter_by(id=user.company_id).first()
                
                if not company:
                    return jsonify({'error': 'Company not found'}), 404
                
                # Check if company has subscribed to the module
                if not company.has_module(module_name):
                    return jsonify({
                        'error': f'Module not subscribed',
                        'message': f'Your company does not have access to the {module_name} module. Please contact your administrator to upgrade your subscription.',
                        'module': module_name,
                        'subscribed_modules': company.get_subscribed_modules()
                    }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_user_modules():
    """
    Helper function to get current user's subscribed modules.
    Must be called within @jwt_required() context.
    
    Returns:
        list: List of subscribed module names, or empty list if error
    """
    try:
        user_id = get_jwt_identity()
        
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return []
            
            company = session.query(Company).filter_by(id=user.company_id).first()
            
            if not company:
                return []
            
            return company.get_subscribed_modules()
    except:
        return []
