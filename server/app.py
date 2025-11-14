from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from io import BytesIO

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image

from .db import init_db, session_scope
from .models import MixDesign
from .config import get_config
from .auth import auth_bp, init_jwt
from .password_reset import password_reset_bp
from .vendors import vendors_bp
from .batches import batches_bp
from .cube_tests import cube_tests_bp
from .third_party_labs import third_party_labs_bp
from .third_party_cube_tests import third_party_cube_tests_bp
from .material_management import material_management_bp
from .material_tests import material_tests_bp
from .training_register import training_register_bp
from .support_admin import support_bp
from .pour_activities import pour_activities_bp
from .batch_import import batch_import_bp
from .material_vehicle_register import material_vehicle_bp
from .project_settings import project_settings_bp
from .background_jobs import background_jobs_bp
from .bulk_entry import bulk_entry_bp
from .safety import safety_bp
from .safety_nc import nc_bp
from .permit_to_work import ptw_bp
from .tbt import tbt_bp
from .training_qr_attendance import training_qr_bp
from .safety_inductions import safety_induction_bp
from .concrete_nc_api import concrete_nc_bp
from .projects import projects_bp
# TODO: These blueprints need db.session refactoring to use session_scope()
# from .incident_investigation import incident_bp
# from .safety_audits import audit_bp
# from .ppe_tracking import ppe_bp
# from .geofence_api import geofence_bp
# TODO: Handover register needs database migration before enabling
# from .handover_register import handover_bp


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

config_obj = get_config()
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def create_app() -> Flask:
    app = Flask(
        __name__, static_folder=str(STATIC_DIR), static_url_path="/static"
    )
    
    # Configuration
    app.config['SECRET_KEY'] = config_obj.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config_obj.MAX_UPLOAD_SIZE
    app.config['JWT_SECRET_KEY'] = config_obj.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Handled in auth.py
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'  # Use 'sub' claim for identity
    # Disable sub claim validation since we use dict identity
    app.config['JWT_ENCODE_NBF'] = True
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
    
    # Initialize JWT
    init_jwt(app)
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp)
    
    # Register password reset blueprint
    app.register_blueprint(password_reset_bp)
    
    # Register vendor management blueprint
    app.register_blueprint(vendors_bp)
    
    # Register batch management blueprint
    app.register_blueprint(batches_bp)
    
    # Register cube test management blueprint
    app.register_blueprint(cube_tests_bp)
    
    # Register third-party lab management blueprint
    app.register_blueprint(third_party_labs_bp)
    
    # Register third-party cube test blueprint
    app.register_blueprint(third_party_cube_tests_bp)
    
    # Register material management blueprint (categories + brands)
    app.register_blueprint(material_management_bp)
    
    # Register material test blueprint
    app.register_blueprint(material_tests_bp)
    
    # Register training register blueprint
    app.register_blueprint(training_register_bp)
    
    # Register support admin blueprint
    app.register_blueprint(support_bp)
    
    # Register pour activity blueprint (batch consolidation)
    app.register_blueprint(pour_activities_bp)
    
    # Register batch import blueprint (for sites where security manages vehicle entry)
    app.register_blueprint(batch_import_bp)
    
    # Register material vehicle register blueprint (for watchmen/security)
    app.register_blueprint(material_vehicle_bp)
    
    # Register bulk entry blueprint (quality engineer bulk batch creation from vehicles)
    app.register_blueprint(bulk_entry_bp)
    
    # Register project settings blueprint
    app.register_blueprint(project_settings_bp)
    
    # Register background jobs blueprint (time limits, test reminders)
    app.register_blueprint(background_jobs_bp)
    
    # Register safety module blueprint
    app.register_blueprint(safety_bp)
    
    # Register NC management blueprint
    app.register_blueprint(nc_bp)
    
    # Register Permit-to-Work blueprint
    app.register_blueprint(ptw_bp)
    
    # Register TBT (Toolbox Talk) blueprint
    app.register_blueprint(tbt_bp)
    
    # Register Training QR Attendance blueprint (cross-app feature - requires both Safety + Concrete)
    app.register_blueprint(training_qr_bp)
    
    # Register Safety Inductions blueprint (worker onboarding with Aadhar verification)
    app.register_blueprint(safety_induction_bp)
    
    # Register Concrete NC (Non-Conformance) blueprint
    app.register_blueprint(concrete_nc_bp)
    
    # Register Projects blueprint (listing and management)
    app.register_blueprint(projects_bp)
    
    # TODO: These blueprints temporarily disabled - need db.session refactoring to use session_scope()
    # Register Incident Investigation blueprint (OSHA compliant incident reporting)
    # app.register_blueprint(incident_bp)
    
    # TODO: These blueprints temporarily disabled - need db.session refactoring to use session_scope()
    # Register Safety Audits blueprint (ISO 45001 compliant audits)
    # app.register_blueprint(audit_bp)
    
    # Register PPE Tracking blueprint (PPE issuance, return, damage, inventory)
    # app.register_blueprint(ppe_bp)
    
    # Register Geo-fencing blueprint (location-based access control)
    # app.register_blueprint(geofence_bp)
    
    # TODO: Register handover register blueprint after database migration
    # app.register_blueprint(handover_bp)
    
    # Enable CORS for commercial deployment
    CORS(app, resources={
        r"/api/*": {
            "origins": config_obj.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Database session cleanup
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database sessions at the end of the request or when the application shuts down."""
        from .db import SessionLocal
        SessionLocal.remove()
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({"error": "Bad request", "message": str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"error": "File too large. Maximum size is 10MB."}), 413

    # Only initialize database in development mode
    # In production, tables are created via migration scripts
    if os.environ.get('FLASK_ENV') == 'development':
        init_db()

    @app.route("/")
    def index() -> Any:
        # Serve the frontend index
        return send_from_directory(app.static_folder, "index.html")
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "prosite-api"})
    
    # Multi-app subscription endpoint
    @app.route('/api/user/app-access', methods=['GET'])
    @jwt_required()
    def get_user_app_access():
        """Get current user's subscribed apps and available features"""
        try:
            from .subscription_middleware import get_user_app_access
            access_info = get_user_app_access()
            return jsonify(access_info), 200
        except Exception as e:
            logger.error(f"Error getting app access: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # -------- API: Mix Designs --------
    @app.get("/api/mix-designs")
    @jwt_required()
    def list_mix_designs():
        try:
            with session_scope() as s:
                items = s.query(MixDesign).order_by(MixDesign.created_at.desc()).all()
                return jsonify([m.to_dict() for m in items])
        except Exception as e:
            logger.error(f"Error listing mix designs: {e}")
            return jsonify({"error": "Failed to fetch mix designs"}), 500

    def _parse_payload() -> Dict[str, Any]:
        """Accept JSON or multipart/form-data (for file upload)."""
        data: Dict[str, Any] = {}
        if request.content_type and request.content_type.startswith("multipart/form-data"):
            form = request.form
            data = {
                "projectName": form.get("projectName", "").strip(),
                "mixDesignId": form.get("mixDesignId", "").strip(),
                "specifiedStrengthPsi": int(form.get("specifiedStrengthPsi", 0) or 0),
                "slumpInches": _to_optional_float(form.get("slumpInches")),
                "airContentPercent": _to_optional_float(form.get("airContentPercent")),
                "batchVolume": _to_optional_float(form.get("batchVolume")),
                "volumeUnit": form.get("volumeUnit") or None,
                "materials": form.get("materials") or None,
                "notes": form.get("notes") or None,
                "ocrText": form.get("ocrText") or None,
            }
        else:
            data = request.get_json(silent=True) or {}
        return data

    def _handle_upload(existing_name: Optional[str] = None) -> Optional[str]:
        """Handle document file uploads."""
        file = request.files.get("document") if request.files else None
        if not file or not file.filename:
            return existing_name
        
        # Validate file extension
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in config_obj.ALLOWED_EXTENSIONS:
            return existing_name
        
        dest = UPLOAD_DIR / filename
        # Avoid overwriting by adding a suffix if needed
        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            i = 1
            while True:
                candidate = UPLOAD_DIR / f"{stem}-{i}{suffix}"
                if not candidate.exists():
                    dest = candidate
                    filename = dest.name
                    break
                i += 1
        file.save(dest)
        logger.info(f"Uploaded file: {filename}")
        return filename
    
    def _handle_image_upload() -> tuple[Optional[str], Optional[bytes], Optional[str]]:
        """Handle image file uploads and store in database."""
        file = request.files.get("image") if request.files else None
        if not file or not file.filename:
            return None, None, None
        
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext not in {'jpg', 'jpeg', 'png', 'gif'}:
            return None, None, None
        
        try:
            # Read and validate image
            image = Image.open(file.stream)
            
            # Create thumbnail (max 800x800) to save space
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_io = BytesIO()
            img_format = 'JPEG' if ext in {'jpg', 'jpeg'} else 'PNG'
            image.save(img_io, img_format, quality=85, optimize=True)
            img_data = img_io.getvalue()
            
            mimetype = f'image/{ext if ext != "jpg" else "jpeg"}'
            logger.info(f"Processed image: {filename} ({len(img_data)} bytes)")
            
            return filename, img_data, mimetype
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None, None, None

    @app.post("/api/mix-designs")
    @jwt_required()
    def create_mix_design():
        try:
            payload = _parse_payload()
            document_name = _handle_upload()
            image_name, image_data, image_mimetype = _handle_image_upload()
            
            with session_scope() as s:
                m = MixDesign(
                    project_name=payload.get("projectName", ""),
                    mix_design_id=payload.get("mixDesignId", ""),
                    specified_strength_psi=int(payload.get("specifiedStrengthPsi", 0) or 0),
                    slump_inches=_to_optional_float(payload.get("slumpInches")),
                    air_content_percent=_to_optional_float(payload.get("airContentPercent")),
                    batch_volume=_to_optional_float(payload.get("batchVolume")),
                    volume_unit=payload.get("volumeUnit"),
                    materials=payload.get("materials"),
                    notes=payload.get("notes"),
                    document_name=document_name,
                    ocr_text=payload.get("ocrText"),
                    image_name=image_name,
                    image_data=image_data,
                    image_mimetype=image_mimetype,
                )
                s.add(m)
                s.flush()
                logger.info(f"Created mix design: {m.mix_design_id}")
                return jsonify(m.to_dict()), 201
        except Exception as e:
            logger.error(f"Error creating mix design: {e}")
            return jsonify({"error": "Failed to create mix design"}), 500

    @app.put("/api/mix-designs/<int:item_id>")
    @jwt_required()
    def update_mix_design(item_id: int):
        try:
            payload = _parse_payload()
            with session_scope() as s:
                m: Optional[MixDesign] = s.get(MixDesign, item_id)
                if not m:
                    return jsonify({"error": "Not found"}), 404
                m.project_name = payload.get("projectName", m.project_name)
                m.mix_design_id = payload.get("mixDesignId", m.mix_design_id)
                if payload.get("specifiedStrengthPsi") is not None:
                    m.specified_strength_psi = int(payload.get("specifiedStrengthPsi") or 0)
                m.slump_inches = _to_optional_float(payload.get("slumpInches")) if "slumpInches" in payload else m.slump_inches
                m.air_content_percent = _to_optional_float(payload.get("airContentPercent")) if "airContentPercent" in payload else m.air_content_percent
                m.batch_volume = _to_optional_float(payload.get("batchVolume")) if "batchVolume" in payload else m.batch_volume
                m.volume_unit = payload.get("volumeUnit", m.volume_unit)
                m.materials = payload.get("materials", m.materials)
                m.notes = payload.get("notes", m.notes)
                m.ocr_text = payload.get("ocrText", m.ocr_text)
                
                # Handle file uploads
                new_doc_name = _handle_upload(existing_name=m.document_name)
                m.document_name = new_doc_name
                
                image_name, image_data, image_mimetype = _handle_image_upload()
                if image_name:
                    m.image_name = image_name
                    m.image_data = image_data
                    m.image_mimetype = image_mimetype
                
                s.flush()
                logger.info(f"Updated mix design: {m.mix_design_id}")
                return jsonify(m.to_dict())
        except Exception as e:
            logger.error(f"Error updating mix design: {e}")
            return jsonify({"error": "Failed to update mix design"}), 500

    @app.delete("/api/mix-designs/<int:item_id>")
    @jwt_required()
    def delete_mix_design(item_id: int):
        try:
            with session_scope() as s:
                m: Optional[MixDesign] = s.get(MixDesign, item_id)
                if not m:
                    return jsonify({"error": "Not found"}), 404
                s.delete(m)
                logger.info(f"Deleted mix design: {m.mix_design_id}")
                return jsonify({"ok": True})
        except Exception as e:
            logger.error(f"Error deleting mix design: {e}")
            return jsonify({"error": "Failed to delete mix design"}), 500
    
    @app.get("/api/mix-designs/<int:item_id>/image")
    @jwt_required()
    def get_mix_design_image(item_id: int):
        """Serve image stored in database."""
        try:
            with session_scope() as s:
                m: Optional[MixDesign] = s.get(MixDesign, item_id)
                if not m or not m.image_data:
                    return jsonify({"error": "Image not found"}), 404
                
                return send_file(
                    BytesIO(m.image_data),
                    mimetype=m.image_mimetype or 'image/jpeg',
                    as_attachment=False
                )
        except Exception as e:
            logger.error(f"Error serving image: {e}")
            return jsonify({"error": "Failed to serve image"}), 500

    @app.get("/uploads/<path:filename>")
    def get_upload(filename: str):
        """Serve uploaded documents."""
        try:
            return send_from_directory(str(UPLOAD_DIR), filename, as_attachment=False)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404

    return app


def _to_optional_float(val: Any) -> Optional[float]:
    if val is None or val == "" or val == "null":
        return None
    try:
        return float(val)
    except Exception:
        return None


# Create app instance at module level for WSGI servers (gunicorn, uwsgi, etc.)
app = create_app()

if __name__ == "__main__":
    config = get_config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
