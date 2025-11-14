"""
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
