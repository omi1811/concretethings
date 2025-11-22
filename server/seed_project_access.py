from server.db import session_scope, init_db
from server.models import Project, ProjectMembership, User

def seed_access():
    print("Seeding project access...")
    try:
        with session_scope() as session:
            # Get admin user
            admin = session.query(User).filter_by(email="admin@example.com").first()
            if not admin:
                print("Admin user not found!")
                return

            # Get or create project
            project = session.query(Project).filter_by(id=1).first()
            if not project:
                print("Creating project 1...")
                project = Project(
                    id=1,
                    name="Test Project",
                    code="TP-001",
                    status="active",
                    created_by=admin.id
                )
                session.add(project)
                session.flush()
            
            # Check membership
            membership = session.query(ProjectMembership).filter_by(
                user_id=admin.id,
                project_id=project.id
            ).first()
            
            if not membership:
                print("Adding admin to project...")
                membership = ProjectMembership(
                    user_id=admin.id,
                    project_id=project.id,
                    role="Quality Manager"  # Give high privileges
                )
                session.add(membership)
                print("Added.")
            else:
                print("Already a member.")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    seed_access()
