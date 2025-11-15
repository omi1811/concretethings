"""
Authentication module with JWT tokens, password hashing, and validation.
Includes rate limiting, account lockout, and role-based access control.
"""
from __future__ import annotations

import re
import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
    decode_token,
)
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from .db import session_scope, SessionLocal
from .models import User, Company, Project, ProjectMembership

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Constants
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION = timedelta(minutes=30)
ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
REFRESH_TOKEN_EXPIRES = timedelta(days=30)


# ============================================================================
# Role-Based Access Control Decorators
# ============================================================================

def require_support_admin(func):
    """
    Decorator to require support admin role.
    Must be used after @jwt_required()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            
            if not user.is_support_admin and not user.is_system_admin:
                return jsonify({
                    "success": False,
                    "error": "Access denied. Support admin privileges required."
                }), 403
            
            return func(*args, **kwargs)
    
    return wrapper


def require_company_admin(func):
    """
    Decorator to require company admin role.
    Must be used after @jwt_required()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            
            if not user.is_company_admin and not user.is_support_admin and not user.is_system_admin:
                return jsonify({
                    "success": False,
                    "error": "Access denied. Company admin privileges required."
                }), 403
            
            return func(*args, **kwargs)
    
    return wrapper


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format."""
    if not email:
        return False, "Email is required"
    
    email = email.strip().lower()
    # RFC 5322 simplified regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number format (international format preferred)."""
    if not phone:
        return False, "Phone number is required"
    
    phone = phone.strip()
    # Remove common separators
    phone_digits = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits after cleanup
    if not phone_digits.isdigit():
        return False, "Phone number must contain only digits"
    
    # Check length (international numbers typically 10-15 digits)
    if len(phone_digits) < 10 or len(phone_digits) > 15:
        return False, "Phone number must be between 10-15 digits"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_full_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate full name."""
    if not name or not name.strip():
        return False, "Full name is required"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Full name must be at least 2 characters"
    
    if len(name) > 255:
        return False, "Full name is too long"
    
    # Allow letters, spaces, hyphens, apostrophes
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        return False, "Full name contains invalid characters"
    
    return True, None


# ============================================================================
# Password Utilities
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using werkzeug's secure method (pbkdf2:sha256)."""
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)


# ============================================================================
# Account Security
# ============================================================================

def check_account_lockout(user: User) -> Tuple[bool, Optional[str]]:
    """Check if account is locked due to failed login attempts."""
    if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        # Check if lockout period has expired
        if user.updated_at and datetime.utcnow() - user.updated_at < ACCOUNT_LOCKOUT_DURATION:
            remaining = ACCOUNT_LOCKOUT_DURATION - (datetime.utcnow() - user.updated_at)
            minutes = int(remaining.total_seconds() / 60)
            return True, f"Account locked. Try again in {minutes} minutes."
        # If lockout expired, reset counter will happen in login
    return False, None


def reset_failed_attempts(user: User) -> None:
    """Reset failed login attempts on successful login."""
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()


def increment_failed_attempts(user: User) -> None:
    """Increment failed login attempts."""
    user.failed_login_attempts += 1
    user.updated_at = datetime.utcnow()


# ============================================================================
# JWT Token Creation
# ============================================================================

def create_tokens(user: User) -> dict:
    """Create access and refresh tokens for user."""
    # Store user_id as string (PyJWT requires sub to be string per RFC 7519)
    identity = str(user.id)
    
    access_token = create_access_token(
        identity=identity,
        expires_delta=ACCESS_TOKEN_EXPIRES
    )
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=REFRESH_TOKEN_EXPIRES
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": int(ACCESS_TOKEN_EXPIRES.total_seconds())
    }


# ============================================================================
# Authorization Decorators
# ============================================================================

def system_admin_required(fn):
    """Decorator to require system admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not user.is_system_admin:
                return jsonify({"error": "System admin access required"}), 403
            
            return fn(*args, **kwargs)
    
    return wrapper


def company_admin_required(fn):
    """Decorator to require company admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not (user.is_system_admin or user.is_company_admin):
                return jsonify({"error": "Company admin access required"}), 403
            
            return fn(*args, **kwargs)
    
    return wrapper


def project_access_required(project_id_param: str = "project_id"):
    """
    Decorator to check if user has access to a specific project.
    System admins and company admins have access to all projects in their company.
    Regular users need explicit project membership.
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            
            # Get project_id from kwargs or request
            project_id = kwargs.get(project_id_param) or request.view_args.get(project_id_param)
            
            if not project_id:
                return jsonify({"error": "Project ID required"}), 400
            
            with session_scope() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return jsonify({"error": "User not found"}), 404
                
                # System admins have access to all projects
                if user.is_system_admin:
                    return fn(*args, **kwargs)
                
                # Company admins have access to all projects in their company
                if user.is_company_admin:
                    project = session.query(Project).filter(Project.id == project_id).first()
                    if not project:
                        return jsonify({"error": "Project not found"}), 404
                    if project.company_id == user.company_id:
                        return fn(*args, **kwargs)
                    return jsonify({"error": "Access denied to this project"}), 403
                
                # Check project membership for regular users
                membership = session.query(ProjectMembership).filter(
                    ProjectMembership.user_id == user_id,
                    ProjectMembership.project_id == project_id
                ).first()
                
                if not membership:
                    return jsonify({"error": "Project access denied"}), 403
                
                # Add role to kwargs for use in endpoint
                kwargs['user_role'] = membership.role
            
            return fn(*args, **kwargs)
                
        return wrapper
    return decorator


# ============================================================================
# Authentication Endpoints
# ============================================================================

@auth_bp.post("/register")
@system_admin_required
def register():
    """
    Register a new user (only system admins can create users).
    Required fields: email, phone, full_name, password, company_id (optional for system admin)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        full_name = data.get("full_name", "").strip()
        password = data.get("password", "")
        company_id = data.get("company_id")
        is_company_admin = data.get("is_company_admin", False)
        is_system_admin = data.get("is_system_admin", False)
        
        # Validate email
        valid, error = validate_email(email)
        if not valid:
            return jsonify({"error": error}), 400
        
        # Validate phone
        valid, error = validate_phone(phone)
        if not valid:
            return jsonify({"error": error}), 400
        
        # Validate full name
        valid, error = validate_full_name(full_name)
        if not valid:
            return jsonify({"error": error}), 400
        
        # Validate password
        valid, error = validate_password(password)
        if not valid:
            return jsonify({"error": error}), 400
        
        # Validate company exists if provided
        if company_id:
            with session_scope() as s:
                company = s.get(Company, company_id)
                if not company:
                    return jsonify({"error": "Company not found"}), 404
        
        # Create user
        with session_scope() as s:
            # Check if user already exists
            existing = s.query(User).filter(User.email == email).first()
            if existing:
                return jsonify({"error": "User with this email already exists"}), 409
            
            # Check phone uniqueness
            existing_phone = s.query(User).filter(User.phone == phone).first()
            if existing_phone:
                return jsonify({"error": "User with this phone number already exists"}), 409
            
            user = User(
                email=email,
                phone=phone,
                full_name=full_name,
                password_hash=hash_password(password),
                company_id=company_id,
                is_company_admin=is_company_admin,
                is_system_admin=is_system_admin,
                is_active=True,
                failed_login_attempts=0
            )
            s.add(user)
            s.flush()
            
            logger.info(f"User registered: {email}")
            return jsonify({
                "message": "User registered successfully",
                "user": user.to_dict()
            }), 201
            
    except IntegrityError as e:
        logger.error(f"Database integrity error during registration: {e}")
        return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.post("/login")
def login():
    """
    Login with email/phone and password.
    Returns JWT access and refresh tokens.
    """
    try:
        data = request.get_json()
        
        identifier = data.get("email") or data.get("phone")  # Support both email and phone
        password = data.get("password")
        
        if not identifier or not password:
            return jsonify({"error": "Email/phone and password are required"}), 400
        
        identifier = identifier.strip().lower()
        
        with session_scope() as s:
            # Find user by email or phone
            user = s.query(User).filter(
                (User.email == identifier) | (User.phone == identifier)
            ).first()
            
            if not user:
                logger.warning(f"Login attempt with invalid identifier: {identifier}")
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive account: {identifier}")
                return jsonify({"error": "Account is inactive"}), 403
            
            # Check account lockout
            locked, message = check_account_lockout(user)
            if locked:
                logger.warning(f"Login attempt for locked account: {identifier}")
                return jsonify({"error": message}), 403
            
            # Verify password
            if not verify_password(user.password_hash, password):
                increment_failed_attempts(user)
                s.flush()
                
                remaining_attempts = MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
                logger.warning(f"Failed login attempt for {identifier}. Attempts remaining: {remaining_attempts}")
                
                if remaining_attempts <= 0:
                    return jsonify({
                        "error": "Account locked due to too many failed attempts. Try again in 30 minutes."
                    }), 403
                
                return jsonify({
                    "error": f"Invalid credentials. {remaining_attempts} attempts remaining."
                }), 401
            
            # Successful login - reset failed attempts
            reset_failed_attempts(user)
            s.flush()
            
            # Create tokens
            tokens = create_tokens(user)
            
            logger.info(f"User logged in: {user.email}")
            
            return jsonify({
                "message": "Login successful",
                "user": user.to_dict(),
                **tokens
            }), 200
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    try:
        user_id_str = get_jwt_identity()  # Returns string user_id
        
        # Create new access token
        access_token = create_access_token(
            identity=user_id_str,
            expires_delta=ACCESS_TOKEN_EXPIRES
        )
        
        return jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int(ACCESS_TOKEN_EXPIRES.total_seconds())
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": "Token refresh failed"}), 500


@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_jwt_identity()  # Returns user_id as string
        
        with session_scope() as s:
            user = s.get(User, int(user_id))
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify(user.to_dict()), 200
            
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({"error": "Failed to fetch user"}), 500


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user_id = get_jwt_identity()  # Returns user_id as string
        
        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        if not current_password or not new_password:
            return jsonify({"error": "Current and new password are required"}), 400
        
        # Validate new password
        valid, error = validate_password(new_password)
        if not valid:
            return jsonify({"error": error}), 400
        
        with session_scope() as s:
            user = s.get(User, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify current password
            if not verify_password(user.password_hash, current_password):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            # Update password
            user.password_hash = hash_password(new_password)
            user.updated_at = datetime.utcnow()
            s.flush()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return jsonify({"message": "Password changed successfully"}), 200
            
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({"error": "Failed to change password"}), 500


# ============================================================================
# Password Reset Flow
# ============================================================================

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Send password reset link to user's email
    Generates a time-limited JWT token for password reset
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        with SessionLocal() as session:
            user = session.query(User).filter_by(email=email).first()
            
            if not user:
                # Security: Don't reveal if email exists
                return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
            
            if not user.is_active:
                return jsonify({"error": "Account is inactive"}), 403
            
            # Generate password reset token (valid for 1 hour)
            reset_token = create_access_token(
                identity=user.id,
                additional_claims={"type": "password_reset"},
                expires_delta=timedelta(hours=1)
            )
            
            # Send password reset email
            try:
                from email_template_renderer import EmailTemplateRenderer
                from email_notifications import EmailService
                
                # Generate reset link
                reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
                
                html = EmailTemplateRenderer.render_password_reset(
                    user_name=user.full_name,
                    reset_link=reset_link,
                    expiry_hours=1
                )
                
                email_service = EmailService()
                email_service.send_email(
                    to=user.email,
                    subject="ProSite - Password Reset Request",
                    html_body=html
                )
                
                logger.info(f"Password reset email sent to: {user.email}")
                
            except Exception as email_error:
                logger.error(f"Failed to send reset email: {email_error}")
                # Don't fail the request if email fails
                pass
            
            return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
            
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({"error": "Failed to process request"}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token from email
    Token must contain type: password_reset
    """
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('newPassword', '').strip()
        
        if not token:
            return jsonify({"error": "Reset token is required"}), 400
        
        if not new_password:
            return jsonify({"error": "New password is required"}), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Verify and decode token
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            token_type = decoded.get('type')
            
            if token_type != 'password_reset':
                return jsonify({"error": "Invalid token type"}), 400
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Reset link has expired. Please request a new one"}), 400
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid reset link"}), 400
        
        with SessionLocal() as session:
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not user.is_active:
                return jsonify({"error": "Account is inactive"}), 403
            
            # Update password
            user.password_hash = generate_password_hash(new_password)
            user.failed_login_attempts = 0  # Reset failed attempts
            user.account_locked_until = None  # Unlock account if locked
            user.updated_at = datetime.utcnow()
            
            session.commit()
            
            logger.info(f"Password reset successful for user: {user.email}")
            
            # Send confirmation email
            try:
                from email_template_renderer import EmailTemplateRenderer
                from email_notifications import EmailService
                
                html = EmailTemplateRenderer.render_password_reset_confirmation(
                    user_name=user.full_name,
                    reset_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                )
                
                email_service = EmailService()
                email_service.send_email(
                    to=user.email,
                    subject="ProSite - Password Reset Successful",
                    html_body=html
                )
                
            except Exception as email_error:
                logger.error(f"Failed to send confirmation email: {email_error}")
                pass
            
            return jsonify({"message": "Password reset successful. You can now login with your new password"}), 200
            
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return jsonify({"error": "Failed to reset password"}), 500


# ============================================================================
# JWT Configuration Helper
# ============================================================================

def init_jwt(app):
    """Initialize JWT extension with app."""
    # Configure to not verify sub claim type (we use integer user_id)
    app.config.setdefault('JWT_DECODE_ALGORITHMS', ['HS256'])
    
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token has expired",
            "message": "Please login again"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "Invalid token",
            "message": "Signature verification failed"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Authorization required",
            "message": "Request does not contain an access token"
        }), 401
    
    return jwt
