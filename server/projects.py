"""
Projects API endpoints for listing and managing projects.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from .models import Project, User
from .db import SessionLocal
from contextlib import contextmanager

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    """List all projects for the user's company."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Get all projects for user's company
            projects = (
                session.query(Project)
                .filter_by(company_id=user.company_id)
                .order_by(desc(Project.created_at))
                .all()
            )

            # Return enabled modules/features for each project
            return (
                jsonify({'projects': [project.to_dict() for project in projects], 'total': len(projects)}),
                200,
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project details."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            project = (
                session.query(Project)
                .filter_by(id=project_id, company_id=user.company_id)
                .first()
            )

            if not project:
                return jsonify({'error': 'Project not found'}), 404

            # Return enabled modules/features for this project
            return jsonify({'project': project.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project (Admin only)."""
    try:
        with session_scope() as session:
            user_id = get_jwt_identity()
            user = session.query(User).filter_by(id=user_id).first()
            
            if not user or user.role not in ['System Admin', 'Admin']:
                return jsonify({'error': 'Unauthorized'}), 403
            
            data = request.json
            
            # Validate required fields
            if not data.get('project_id') or not data.get('project_name'):
                return jsonify({'error': 'project_id and project_name are required'}), 400
            
            # Check if project_id already exists
            existing = session.query(Project).filter_by(
                company_id=user.company_id,
                project_id=data['project_id']
            ).first()
            
            if existing:
                return jsonify({'error': 'Project ID already exists'}), 400
            
            project = Project(
                company_id=user.company_id,
                project_id=data['project_id'],
                project_name=data['project_name'],
                location=data.get('location'),
                client_name=data.get('client_name'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date')
            )
            
            session.add(project)
            session.flush()
            
            return jsonify({
                'message': 'Project created successfully',
                'project': project.to_dict()
            }), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
