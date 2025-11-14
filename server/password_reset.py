"""
Password Reset functionality with email-based token system.
Implements secure password reset flow without external dependencies.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .db import session_scope, Base
from .models import User
from .email_notifications import send_email
import logging

logger = logging.getLogger(__name__)

password_reset_bp = Blueprint('password_reset', __name__, url_prefix='/api/auth')

# Token expires in 1 hour
TOKEN_EXPIRY_HOURS = 1


class PasswordResetToken(Base):
    """Store password reset tokens with expiry."""
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(default=False)


def generate_reset_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


@password_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset. Sends email with reset link.
    
    POST /api/auth/forgot-password
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        with session_scope() as session:
            user = session.query(User).filter_by(email=email).first()
            
            # Always return success to prevent email enumeration
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return jsonify({
                    'message': 'If that email exists, a password reset link has been sent'
                }), 200
            
            # Generate reset token
            token = generate_reset_token()
            token_hash_value = hash_token(token)
            expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            
            # Invalidate any existing tokens for this user
            session.query(PasswordResetToken).filter_by(
                user_id=user.id,
                used=False
            ).update({'used': True})
            
            # Create new token
            reset_token = PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash_value,
                expires_at=expires_at
            )
            session.add(reset_token)
            session.flush()
            
            # Send reset email
            reset_url = f"{request.host_url}reset-password?token={token}"
            
            email_body = f"""
Hello {user.full_name},

You requested to reset your password for ConcreteTHings.

Please click the link below to reset your password:
{reset_url}

This link will expire in {TOKEN_EXPIRY_HOURS} hour(s).

If you didn't request this, please ignore this email.

Best regards,
ConcreteTHings Team
            """
            
            try:
                send_email(
                    to_email=user.email,
                    subject="Reset Your Password - ConcreteTHings",
                    html_body=email_body
                )
                logger.info(f"Password reset email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
                # Don't reveal email sending failure to prevent enumeration
            
            return jsonify({
                'message': 'If that email exists, a password reset link has been sent'
            }), 200
            
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again later'}), 500


@password_reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token.
    
    POST /api/auth/reset-password
    {
        "token": "reset_token_from_email",
        "new_password": "newSecurePassword123"
    }
    """
    try:
        data = request.json
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # Validate password strength
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        token_hash_value = hash_token(token)
        
        with session_scope() as session:
            # Find valid token
            reset_token = session.query(PasswordResetToken).filter_by(
                token_hash=token_hash_value,
                used=False
            ).first()
            
            if not reset_token:
                return jsonify({'error': 'Invalid or expired reset token'}), 400
            
            # Check if token expired
            if datetime.utcnow() > reset_token.expires_at:
                return jsonify({'error': 'Reset token has expired'}), 400
            
            # Get user
            user = session.query(User).filter_by(id=reset_token.user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Update password
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)
            
            # Mark token as used
            reset_token.used = True
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.account_locked_until = None
            
            session.flush()
            
            logger.info(f"Password reset successful for user: {user.email}")
            
            return jsonify({
                'message': 'Password reset successful. You can now login with your new password'
            }), 200
            
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again later'}), 500


@password_reset_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """
    Verify if a reset token is valid (for frontend validation).
    
    POST /api/auth/verify-reset-token
    {
        "token": "reset_token_from_email"
    }
    """
    try:
        data = request.json
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        token_hash_value = hash_token(token)
        
        with session_scope() as session:
            reset_token = session.query(PasswordResetToken).filter_by(
                token_hash=token_hash_value,
                used=False
            ).first()
            
            if not reset_token:
                return jsonify({'valid': False, 'error': 'Invalid token'}), 200
            
            if datetime.utcnow() > reset_token.expires_at:
                return jsonify({'valid': False, 'error': 'Token expired'}), 200
            
            # Get user email for display
            user = session.query(User).filter_by(id=reset_token.user_id).first()
            
            return jsonify({
                'valid': True,
                'email': user.email if user else None
            }), 200
            
    except Exception as e:
        logger.error(f"Verify token error: {str(e)}")
        return jsonify({'valid': False, 'error': 'An error occurred'}), 200
