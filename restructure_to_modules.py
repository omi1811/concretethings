#!/usr/bin/env python3
"""
Restructure ProSite codebase into modular architecture
This script creates the new directory structure and moves files accordingly
"""
import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
SERVER_DIR = BASE_DIR / "server"
MODULES_DIR = SERVER_DIR / "modules"
CORE_DIR = SERVER_DIR / "core"

# File mapping: old_file -> new_location
FILE_MAPPING = {
    # Core files
    "auth.py": "core/auth.py",
    "models.py": "core/models.py",
    "notifications.py": "core/notifications.py",
    "email_notifications.py": "core/email_notifications.py",
    "module_access.py": "core/module_access.py",
    "password_reset.py": "core/password_reset.py",
    "subscription_middleware.py": "core/subscription_middleware.py",
    
    # Safety module
    "safety.py": "modules/safety/routes/safety_api.py",
    "safety_models.py": "modules/safety/models/safety_models.py",
    "tbt.py": "modules/safety/routes/tbt_api.py",
    "tbt_models.py": "modules/safety/models/tbt_models.py",
    "permit_to_work.py": "modules/safety/routes/ptw_api.py",
    "permit_to_work_models.py": "modules/safety/models/ptw_models.py",
    "safety_nc.py": "modules/safety/routes/nc_api.py",
    "safety_nc_models.py": "modules/safety/models/nc_models.py",
    "safety_audits.py": "modules/safety/routes/audits_api.py",
    "safety_audit_models.py": "modules/safety/models/audit_models.py",
    "safety_inductions.py": "modules/safety/routes/induction_api.py",
    "safety_induction_models.py": "modules/safety/models/induction_models.py",
    "incident_investigation.py": "modules/safety/routes/incidents_api.py",
    "incident_investigation_models.py": "modules/safety/models/incident_models.py",
    "ppe_tracking.py": "modules/safety/routes/ppe_api.py",
    "ppe_tracking_models.py": "modules/safety/models/ppe_models.py",
    
    # Concrete module
    "batches.py": "modules/concrete/routes/batches_api.py",
    "cube_tests.py": "modules/concrete/routes/tests_api.py",
    "concrete_nc_api.py": "modules/concrete/routes/nc_api.py",
    "concrete_nc_models.py": "modules/concrete/models/nc_models.py",
    "vendors.py": "modules/concrete/routes/vendors_api.py",
    "third_party_labs.py": "modules/concrete/routes/labs_api.py",
    "third_party_cube_tests.py": "modules/concrete/routes/third_party_tests_api.py",
    "material_tests.py": "modules/concrete/routes/materials_api.py",
    "pour_activities.py": "modules/concrete/routes/pour_api.py",
    "batch_import.py": "modules/concrete/services/batch_import.py",
    "bulk_entry.py": "modules/concrete/services/bulk_entry.py",
    
    # Materials module
    "material_management.py": "modules/materials/routes/materials_api.py",
    "material_vehicle_register.py": "modules/materials/routes/vehicles_api.py",
    "handover_register.py": "modules/materials/routes/handover_api.py",
    
    # Training module
    "training_register.py": "modules/training/routes/training_api.py",
    "training_attendance_models.py": "modules/training/models/training_models.py",
    "training_qr_attendance.py": "modules/training/routes/qr_attendance_api.py",
    
    # Geofence module
    "geofence_api.py": "modules/geofence/routes/geofence_api.py",
    "geofence_models.py": "modules/geofence/models/geofence_models.py",
    "geofence_middleware.py": "modules/geofence/middleware/geofence_middleware.py",
    
    # Admin module
    "support_admin.py": "modules/admin/routes/support_api.py",
    "projects.py": "modules/admin/routes/projects_api.py",
    "background_jobs.py": "modules/admin/services/background_jobs.py",
    "project_settings.py": "modules/admin/services/project_settings.py",
}

def create_directory_structure():
    """Create the new modular directory structure"""
    print("Creating modular directory structure...")
    
    # Create core directory
    CORE_DIR.mkdir(exist_ok=True)
    (CORE_DIR / "__init__.py").touch()
    
    # Create modules directory
    MODULES_DIR.mkdir(exist_ok=True)
    (MODULES_DIR / "__init__.py").touch()
    
    # Define module structure
    modules = {
        "safety": ["routes", "models", "services"],
        "concrete": ["routes", "models", "services"],
        "materials": ["routes", "models"],
        "training": ["routes", "models"],
        "geofence": ["routes", "models", "middleware"],
        "admin": ["routes", "services"],
    }
    
    # Create module directories
    for module_name, subdirs in modules.items():
        module_dir = MODULES_DIR / module_name
        module_dir.mkdir(exist_ok=True)
        (module_dir / "__init__.py").touch()
        
        for subdir in subdirs:
            subdir_path = module_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            (subdir_path / "__init__.py").touch()
    
    print("✅ Directory structure created")

def move_files(dry_run=True):
    """Move files to new locations"""
    print(f"\n{'DRY RUN - ' if dry_run else ''}Moving files...")
    
    moved_count = 0
    skipped_count = 0
    
    for old_file, new_location in FILE_MAPPING.items():
        old_path = SERVER_DIR / old_file
        new_path = SERVER_DIR / new_location
        
        if not old_path.exists():
            print(f"⚠️  SKIP: {old_file} (not found)")
            skipped_count += 1
            continue
        
        if dry_run:
            print(f"📄 WOULD MOVE: {old_file} → {new_location}")
        else:
            # Create parent directory if needed
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file (don't delete original yet for safety)
            shutil.copy2(old_path, new_path)
            print(f"✅ COPIED: {old_file} → {new_location}")
        
        moved_count += 1
    
    print(f"\n{'Would move' if dry_run else 'Moved'}: {moved_count} files")
    print(f"Skipped: {skipped_count} files")

def update_imports_in_file(file_path, dry_run=True):
    """Update import statements in a Python file"""
    if not file_path.suffix == ".py":
        return
    
    try:
        content = file_path.read_text()
        original_content = content
        
        # Update common imports
        replacements = {
            "from .auth import": "from server.core.auth import",
            "from .models import": "from server.core.models import",
            "from .notifications import": "from server.core.notifications import",
            "from .email_notifications import": "from server.core.email_notifications import",
            "from .module_access import": "from server.core.module_access import",
            "from .db import": "from server.db import",
            "from .config import": "from server.config import",
        }
        
        for old_import, new_import in replacements.items():
            content = content.replace(old_import, new_import)
        
        if content != original_content and not dry_run:
            file_path.write_text(content)
            print(f"  ✏️  Updated imports in {file_path.name}")
    
    except Exception as e:
        print(f"  ⚠️  Error updating {file_path}: {e}")

def create_module_init_files():
    """Create __init__.py files that export module contents"""
    print("\nCreating module __init__.py files...")
    
    # Safety module init
    safety_init = MODULES_DIR / "safety" / "__init__.py"
    safety_init.write_text('''"""
Safety Management Module
Handles TBT, PTW, NC, Audits, Inductions, Incidents, and PPE
"""
from .routes.safety_api import safety_bp
from .routes.tbt_api import tbt_bp
from .routes.ptw_api import ptw_bp
from .routes.nc_api import nc_bp
from .routes.audits_api import audits_bp
from .routes.induction_api import induction_bp
from .routes.incidents_api import incident_bp
from .routes.ppe_api import ppe_bp

__all__ = [
    'safety_bp', 'tbt_bp', 'ptw_bp', 'nc_bp',
    'audits_bp', 'induction_bp', 'incident_bp', 'ppe_bp'
]
''')
    
    # Concrete module init
    concrete_init = MODULES_DIR / "concrete" / "__init__.py"
    concrete_init.write_text('''"""
Concrete Quality Management Module
Handles batches, tests, NC, vendors, labs, and pour activities
"""
from .routes.batches_api import batch_bp
from .routes.tests_api import cube_test_bp
from .routes.nc_api import concrete_nc_bp
from .routes.vendors_api import vendor_bp
from .routes.labs_api import lab_bp
from .routes.pour_api import pour_bp

__all__ = [
    'batch_bp', 'cube_test_bp', 'concrete_nc_bp',
    'vendor_bp', 'lab_bp', 'pour_bp'
]
''')
    
    print("✅ Module __init__.py files created")

def create_new_app_py():
    """Create updated app.py with modular imports"""
    new_app_content = '''"""
ProSite - Main Flask Application
Modular architecture with clean separation of concerns
"""
from flask import Flask
from flask_cors import CORS

from .config import Config
from .db import init_db

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    
    # Register core blueprints
    from .core.password_reset import password_reset_bp
    app.register_blueprint(password_reset_bp)
    
    # Register Safety module
    from .modules.safety import (
        safety_bp, tbt_bp, ptw_bp, nc_bp,
        audits_bp, induction_bp, incident_bp, ppe_bp
    )
    app.register_blueprint(safety_bp)
    app.register_blueprint(tbt_bp)
    app.register_blueprint(ptw_bp)
    app.register_blueprint(nc_bp)
    app.register_blueprint(audits_bp)
    app.register_blueprint(induction_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(ppe_bp)
    
    # Register Concrete module
    from .modules.concrete import (
        batch_bp, cube_test_bp, concrete_nc_bp,
        vendor_bp, lab_bp, pour_bp
    )
    app.register_blueprint(batch_bp)
    app.register_blueprint(cube_test_bp)
    app.register_blueprint(concrete_nc_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(pour_bp)
    
    # Register other modules
    from .modules.materials.routes.materials_api import material_bp
    from .modules.training.routes.training_api import training_bp
    from .modules.geofence.routes.geofence_api import geofence_bp
    from .modules.admin.routes.support_api import support_bp
    from .modules.admin.routes.projects_api import project_bp
    
    app.register_blueprint(material_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(geofence_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(project_bp)
    
    return app

app = create_app()
'''
    
    app_file = SERVER_DIR / "app_modular.py"
    app_file.write_text(new_app_content)
    print(f"✅ Created {app_file}")

def main():
    """Main restructuring process"""
    print("=" * 80)
    print("ProSite Modular Restructuring")
    print("=" * 80)
    
    # Ask for confirmation
    print("\n⚠️  This will restructure the codebase into a modular architecture")
    print("Files will be COPIED (not moved) to preserve originals")
    
    response = input("\nProceed with DRY RUN? (y/n): ").lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Step 1: Create directories
    create_directory_structure()
    
    # Step 2: Move files (dry run first)
    move_files(dry_run=True)
    
    # Step 3: Create module init files
    create_module_init_files()
    
    # Step 4: Create new app.py
    create_new_app_py()
    
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE")
    print("=" * 80)
    print("\nTo actually perform the restructuring:")
    print("1. Review the changes above")
    print("2. Modify this script: change dry_run=False in move_files()")
    print("3. Run again to perform actual file operations")
    print("4. Update all import statements across the codebase")
    print("5. Test thoroughly before committing")
    print("\n⚠️  Remember to backup your database and code before proceeding!")

if __name__ == "__main__":
    main()
