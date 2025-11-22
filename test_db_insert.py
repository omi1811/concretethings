from datetime import datetime
from server.db import db, SessionLocal

# Simple test to insert a cube test
try:
    from server.models import CubeTestRegister, Project
    
    with SessionLocal() as session:
        # Check if project exists
        project = session.query(Project).first()
        if not project:
            print("No project found")
        else:
            print(f"Found project: {project.id}")
            
            # Try to create a cube test
            cube_test = CubeTestRegister(
                project_id=project.id,
                batch_id=None,
                set_number=1,
                test_age_days=7,
                casting_date=datetime.now(),
                cast_by=1,
                concrete_type="Normal",
                concrete_grade="M40",
                number_of_cubes=3,
                pass_fail_status='planned'
            )
            session.add(cube_test)
            session.commit()
            print(f"Successfully created cube test: {cube_test.id}")
            
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
