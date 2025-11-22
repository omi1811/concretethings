"""
Reports API Blueprint

This module provides API endpoints for generating reports.
"""

from flask import Blueprint, request, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import csv
import io

try:
    from .db import session_scope
    from .models import CubeTestRegister, BatchRegister, Project, ProjectMembership
except ImportError:
    from db import session_scope
    from models import CubeTestRegister, BatchRegister, Project, ProjectMembership

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/reports/cube-tests/export', methods=['GET'])
@jwt_required()
def export_cube_tests():
    """
    Export cube tests to CSV.
    
    Query Parameters:
    - project_id (required)
    - date_from (optional)
    - date_to (optional)
    """
    user_id = int(get_jwt_identity())
    project_id = request.args.get('project_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not project_id:
        return {"error": "project_id is required"}, 400
        
    # Check access
    with session_scope() as session:
        membership = session.query(ProjectMembership).filter_by(
            user_id=user_id,
            project_id=project_id
        ).first()
        
        if not membership:
            return {"error": "Access denied"}, 403
            
        # Query tests
        query = session.query(CubeTestRegister).filter_by(
            project_id=project_id,
            is_deleted=False
        )
        
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(CubeTestRegister.casting_date >= date_from_dt)
            except ValueError:
                pass
                
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(CubeTestRegister.casting_date <= date_to_dt)
            except ValueError:
                pass
                
        tests = query.order_by(CubeTestRegister.casting_date.desc()).all()
        
        # Generate CSV
        def generate():
            data = io.StringIO()
            writer = csv.writer(data)
            
            # Header
            writer.writerow([
                'Test ID', 'Batch No', 'Casting Date', 'Testing Date', 
                'Age (Days)', 'Grade', 'Concrete Type',
                'Cube 1 (MPa)', 'Cube 2 (MPa)', 'Cube 3 (MPa)', 
                'Avg Strength (MPa)', 'Result', 'Remarks'
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
            for test in tests:
                batch_no = "Planned"
                if test.batch_id:
                    batch = session.query(BatchRegister).filter_by(id=test.batch_id).first()
                    if batch:
                        batch_no = batch.batch_number
                
                writer.writerow([
                    test.id,
                    batch_no,
                    test.casting_date.strftime('%Y-%m-%d'),
                    test.testing_date.strftime('%Y-%m-%d') if test.testing_date else 'Pending',
                    test.test_age_days,
                    test.concrete_grade,
                    test.concrete_type,
                    test.cube_1_strength_mpa or '-',
                    test.cube_2_strength_mpa or '-',
                    test.cube_3_strength_mpa or '-',
                    test.average_strength_mpa or '-',
                    test.pass_fail_status.upper(),
                    test.remarks or ''
                ])
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

    response = Response(stream_with_context(generate()), mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename=f'cube_tests_project_{project_id}.csv')
    return response
