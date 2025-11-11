"""Configuration management for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Server
    PORT = int(os.environ.get('PORT', '8000'))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/data.sqlite3')
    
    # File Upload
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = set(os.environ.get(
        'ALLOWED_EXTENSIONS', 
        'pdf,jpg,jpeg,png,gif,doc,docx,txt'
    ).split(','))
    
    UPLOAD_DIR = BASE_DIR / 'uploads'
    STATIC_DIR = BASE_DIR / 'static'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/data.sqlite3')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # In production, ensure SECRET_KEY is set via environment variable


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
