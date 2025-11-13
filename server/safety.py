"""
Safety Module API - Flexible, User-Configurable Platform
Inspired by DigiQC's approach: Platform provides framework, users create their content
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import logging

from .db import session_scope
from .safety_models import (
    SafetyModule, FormTemplate, FormSubmission,
    Worker, WorkerAttendance, SafetyAction
)
from .models import User, Company, Project
from .auth import require_company_admin

logger = logging.getLogger(__name__)

# Create blueprint
safety_bp = Blueprint("safety", __name__, url_prefix="/api/safety")


# ============================================================================
# Module Management
# ============================================================================

@safety_bp.get("/modules")
@jwt_required()
def get_modules():
    """Get all safety modules for the company"""
    try:
        user_id = int(get_jwt_identity())
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Get modules for user's company
            modules = session.query(SafetyModule).filter(
                SafetyModule.company_id == user.company_id,
                SafetyModule.is_active == True
            ).order_by(SafetyModule.display_order).all()
            
            return jsonify({
                "modules": [m.to_dict() for m in modules]
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching modules: {e}")
        return jsonify({"error": "Failed to fetch modules"}), 500


@safety_bp.post("/modules")
@jwt_required()
@require_company_admin
def create_module():
    """Create a new safety module (admin only)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        required = ["module_type", "module_name"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            module = SafetyModule(
                company_id=user.company_id,
                project_id=data.get("project_id"),
                module_type=data["module_type"],
                module_name=data["module_name"],
                description=data.get("description"),
                icon=data.get("icon", "shield"),
                display_order=data.get("display_order", 0),
                created_by=user_id
            )
            
            session.add(module)
            session.flush()
            
            logger.info(f"Module created: {module.module_name} by user {user_id}")
            return jsonify({"message": "Module created", "module": module.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error creating module: {e}")
        return jsonify({"error": "Failed to create module"}), 500


# ============================================================================
# Form Template Management (DigiQC-style)
# ============================================================================

@safety_bp.get("/templates")
@jwt_required()
def get_templates():
    """Get all form templates for the company"""
    try:
        user_id = int(get_jwt_identity())
        module_id = request.args.get("module_id", type=int)
        category = request.args.get("category")
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            query = session.query(FormTemplate).filter(
                FormTemplate.company_id == user.company_id,
                FormTemplate.is_latest == True,
                FormTemplate.is_active == True
            )
            
            if module_id:
                query = query.filter(FormTemplate.module_id == module_id)
            
            if category:
                query = query.filter(FormTemplate.category == category)
            
            templates = query.all()
            
            return jsonify({
                "templates": [t.to_dict() for t in templates]
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        return jsonify({"error": "Failed to fetch templates"}), 500


@safety_bp.post("/templates")
@jwt_required()
def create_template():
    """Create a new form template"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        required = ["module_id", "template_name", "form_fields"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        if not isinstance(data["form_fields"], list):
            return jsonify({"error": "form_fields must be an array"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Check if module exists and belongs to user's company
            module = session.query(SafetyModule).filter(
                SafetyModule.id == data["module_id"],
                SafetyModule.company_id == user.company_id
            ).first()
            
            if not module:
                return jsonify({"error": "Module not found"}), 404
            
            template = FormTemplate(
                company_id=user.company_id,
                project_id=data.get("project_id"),
                module_id=data["module_id"],
                template_name=data["template_name"],
                template_code=data.get("template_code"),
                description=data.get("description"),
                category=data.get("category"),
                form_fields=data["form_fields"],
                has_scoring=data.get("has_scoring", False),
                scoring_config=data.get("scoring_config"),
                requires_approval=data.get("requires_approval", False),
                approval_levels=data.get("approval_levels"),
                auto_assign=data.get("auto_assign", False),
                assignment_rules=data.get("assignment_rules"),
                is_recurring=data.get("is_recurring", False),
                recurrence_config=data.get("recurrence_config"),
                created_by=user_id
            )
            
            session.add(template)
            session.flush()
            
            logger.info(f"Template created: {template.template_name} by user {user_id}")
            return jsonify({"message": "Template created", "template": template.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.put("/templates/<int:template_id>")
@jwt_required()
def update_template(template_id):
    """Update form template (creates new version)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Get existing template
            old_template = session.query(FormTemplate).filter(
                FormTemplate.id == template_id,
                FormTemplate.company_id == user.company_id
            ).first()
            
            if not old_template:
                return jsonify({"error": "Template not found"}), 404
            
            # Mark old version as not latest
            old_template.is_latest = False
            
            # Create new version
            new_template = FormTemplate(
                company_id=old_template.company_id,
                project_id=old_template.project_id,
                module_id=old_template.module_id,
                template_name=data.get("template_name", old_template.template_name),
                template_code=old_template.template_code,
                description=data.get("description", old_template.description),
                category=data.get("category", old_template.category),
                form_fields=data.get("form_fields", old_template.form_fields),
                has_scoring=data.get("has_scoring", old_template.has_scoring),
                scoring_config=data.get("scoring_config", old_template.scoring_config),
                requires_approval=data.get("requires_approval", old_template.requires_approval),
                approval_levels=data.get("approval_levels", old_template.approval_levels),
                version=old_template.version + 1,
                is_latest=True,
                parent_template_id=template_id,
                created_by=user_id
            )
            
            session.add(new_template)
            session.flush()
            
            logger.info(f"Template updated: {new_template.template_name} v{new_template.version}")
            return jsonify({"message": "Template updated", "template": new_template.to_dict()}), 200
            
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Form Submissions
# ============================================================================

@safety_bp.get("/submissions")
@jwt_required()
def get_submissions():
    """Get form submissions with filtering"""
    try:
        user_id = int(get_jwt_identity())
        
        # Filters
        project_id = request.args.get("project_id", type=int)
        template_id = request.args.get("template_id", type=int)
        status = request.args.get("status")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            query = session.query(FormSubmission).filter(
                FormSubmission.company_id == user.company_id
            )
            
            if project_id:
                query = query.filter(FormSubmission.project_id == project_id)
            
            if template_id:
                query = query.filter(FormSubmission.template_id == template_id)
            
            if status:
                query = query.filter(FormSubmission.status == status)
            
            if from_date:
                query = query.filter(FormSubmission.submitted_at >= datetime.fromisoformat(from_date))
            
            if to_date:
                query = query.filter(FormSubmission.submitted_at <= datetime.fromisoformat(to_date))
            
            submissions = query.order_by(desc(FormSubmission.submitted_at)).all()
            
            return jsonify({
                "submissions": [s.to_dict() for s in submissions],
                "total": len(submissions)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching submissions: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.post("/submissions")
@jwt_required()
def create_submission():
    """Submit a form"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        required = ["project_id", "template_id", "form_data"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Verify template exists
            template = session.query(FormTemplate).filter(
                FormTemplate.id == data["template_id"],
                FormTemplate.company_id == user.company_id
            ).first()
            
            if not template:
                return jsonify({"error": "Template not found"}), 404
            
            # Generate submission number
            count = session.query(FormSubmission).filter(
                FormSubmission.company_id == user.company_id
            ).count()
            submission_number = f"SF-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
            
            # Calculate score if applicable
            score = None
            score_percentage = None
            if template.has_scoring and template.scoring_config:
                # Implement scoring logic based on template.scoring_config
                pass  # TODO: Implement dynamic scoring
            
            submission = FormSubmission(
                company_id=user.company_id,
                project_id=data["project_id"],
                template_id=data["template_id"],
                submission_number=submission_number,
                form_data=data["form_data"],
                location=data.get("location"),
                geo_location=data.get("geo_location"),
                photos=data.get("photos"),
                videos=data.get("videos"),
                documents=data.get("documents"),
                score=score,
                score_percentage=score_percentage,
                priority=data.get("priority", "medium"),
                due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
                submitted_by=user_id
            )
            
            session.add(submission)
            session.flush()
            
            logger.info(f"Form submitted: {submission_number} by user {user_id}")
            return jsonify({"message": "Form submitted", "submission": submission.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.get("/submissions/<int:submission_id>")
@jwt_required()
def get_submission(submission_id):
    """Get submission details"""
    try:
        user_id = int(get_jwt_identity())
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            submission = session.query(FormSubmission).filter(
                FormSubmission.id == submission_id,
                FormSubmission.company_id == user.company_id
            ).first()
            
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            return jsonify({"submission": submission.to_dict()}), 200
            
    except Exception as e:
        logger.error(f"Error fetching submission: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Worker Management
# ============================================================================

@safety_bp.get("/workers")
@jwt_required()
def get_workers():
    """Get all workers"""
    try:
        user_id = int(get_jwt_identity())
        project_id = request.args.get("project_id", type=int)
        contractor = request.args.get("contractor")
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            query = session.query(Worker).filter(
                Worker.company_id == user.company_id,
                Worker.is_active == True
            )
            
            if project_id:
                query = query.filter(Worker.project_id == project_id)
            
            if contractor:
                query = query.filter(Worker.contractor == contractor)
            
            workers = query.all()
            
            return jsonify({
                "workers": [w.to_dict() for w in workers],
                "total": len(workers)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching workers: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.post("/workers")
@jwt_required()
def create_worker():
    """Add new worker"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        required = ["worker_code", "full_name"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Check duplicate worker_code
            existing = session.query(Worker).filter(
                Worker.worker_code == data["worker_code"]
            ).first()
            
            if existing:
                return jsonify({"error": "Worker code already exists"}), 409
            
            worker = Worker(
                company_id=user.company_id,
                project_id=data.get("project_id"),
                worker_code=data["worker_code"],
                full_name=data["full_name"],
                phone=data.get("phone"),
                email=data.get("email"),
                photo=data.get("photo"),
                contractor=data.get("contractor"),
                skill_category=data.get("skill_category"),
                designation=data.get("designation"),
                training_records=data.get("training_records"),
                certifications=data.get("certifications"),
                qr_code=data.get("qr_code"),
                nfc_tag=data.get("nfc_tag"),
                joined_date=datetime.fromisoformat(data["joined_date"]) if data.get("joined_date") else None
            )
            
            session.add(worker)
            session.flush()
            
            logger.info(f"Worker created: {worker.worker_code}")
            return jsonify({"message": "Worker created", "worker": worker.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error creating worker: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Attendance Management
# ============================================================================

@safety_bp.post("/attendance/check-in")
@jwt_required()
def check_in_worker():
    """Check in worker"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        required = ["worker_id", "project_id"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Check if already checked in today
            today = datetime.utcnow().date()
            existing = session.query(WorkerAttendance).filter(
                WorkerAttendance.worker_id == data["worker_id"],
                WorkerAttendance.project_id == data["project_id"],
                WorkerAttendance.date >= datetime.combine(today, datetime.min.time())
            ).first()
            
            if existing and existing.check_in_time:
                return jsonify({"error": "Already checked in today"}), 409
            
            attendance = WorkerAttendance(
                company_id=user.company_id,
                project_id=data["project_id"],
                worker_id=data["worker_id"],
                date=datetime.utcnow(),
                check_in_time=datetime.utcnow(),
                check_in_method=data.get("check_in_method", "manual"),
                check_in_location=data.get("check_in_location"),
                ppe_verified=data.get("ppe_verified", False),
                ppe_items_checked=data.get("ppe_items_checked"),
                ppe_photo=data.get("ppe_photo")
            )
            
            session.add(attendance)
            session.flush()
            
            logger.info(f"Worker check-in: {data['worker_id']}")
            return jsonify({"message": "Check-in successful", "attendance": attendance.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error checking in worker: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Safety Actions & Follow-ups
# ============================================================================

@safety_bp.get("/actions")
@jwt_required()
def get_actions():
    """Get safety actions"""
    try:
        user_id = int(get_jwt_identity())
        status = request.args.get("status")
        assigned_to_me = request.args.get("assigned_to_me", type=bool)
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            query = session.query(SafetyAction).filter(
                SafetyAction.company_id == user.company_id
            )
            
            if status:
                query = query.filter(SafetyAction.status == status)
            
            if assigned_to_me:
                query = query.filter(SafetyAction.assigned_to == user_id)
            
            actions = query.order_by(desc(SafetyAction.due_date)).all()
            
            return jsonify({
                "actions": [a.to_dict() for a in actions],
                "total": len(actions)
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching actions: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.post("/actions")
@jwt_required()
def create_action():
    """Create safety action"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        required = ["project_id", "submission_id", "action_description", "assigned_to", "due_date"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Generate action number
            count = session.query(SafetyAction).filter(
                SafetyAction.company_id == user.company_id
            ).count()
            action_number = f"ACT-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
            
            action = SafetyAction(
                company_id=user.company_id,
                project_id=data["project_id"],
                submission_id=data["submission_id"],
                action_number=action_number,
                action_description=data["action_description"],
                assigned_to=data["assigned_to"],
                priority=data.get("priority", "medium"),
                due_date=datetime.fromisoformat(data["due_date"]),
                created_by=user_id
            )
            
            session.add(action)
            session.flush()
            
            logger.info(f"Action created: {action_number}")
            return jsonify({"message": "Action created", "action": action.to_dict()}), 201
            
    except Exception as e:
        logger.error(f"Error creating action: {e}")
        return jsonify({"error": str(e)}), 500


@safety_bp.put("/actions/<int:action_id>/complete")
@jwt_required()
def complete_action(action_id):
    """Mark action as completed"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        with session_scope() as session:
            action = session.query(SafetyAction).filter(
                SafetyAction.id == action_id
            ).first()
            
            if not action:
                return jsonify({"error": "Action not found"}), 404
            
            # Check if user is assigned to this action
            if action.assigned_to != user_id:
                return jsonify({"error": "Not authorized to complete this action"}), 403
            
            action.status = "completed"
            action.completion_notes = data.get("completion_notes")
            action.completion_photos = data.get("completion_photos")
            action.completed_at = datetime.utcnow()
            
            session.flush()
            
            logger.info(f"Action completed: {action.action_number}")
            return jsonify({"message": "Action completed", "action": action.to_dict()}), 200
            
    except Exception as e:
        logger.error(f"Error completing action: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Analytics & Reports
# ============================================================================

@safety_bp.get("/analytics/summary")
@jwt_required()
def get_safety_summary():
    """Get safety analytics summary"""
    try:
        user_id = int(get_jwt_identity())
        project_id = request.args.get("project_id", type=int)
        
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            # Base query filter
            base_filter = [FormSubmission.company_id == user.company_id]
            if project_id:
                base_filter.append(FormSubmission.project_id == project_id)
            
            # Get counts
            total_submissions = session.query(FormSubmission).filter(*base_filter).count()
            pending_approvals = session.query(FormSubmission).filter(
                *base_filter,
                FormSubmission.status == "submitted"
            ).count()
            
            overdue_actions = session.query(SafetyAction).filter(
                SafetyAction.company_id == user.company_id,
                SafetyAction.status != "completed",
                SafetyAction.due_date < datetime.utcnow()
            ).count()
            
            active_workers = session.query(Worker).filter(
                Worker.company_id == user.company_id,
                Worker.is_active == True
            ).count()
            
            return jsonify({
                "summary": {
                    "total_submissions": total_submissions,
                    "pending_approvals": pending_approvals,
                    "overdue_actions": overdue_actions,
                    "active_workers": active_workers
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({"error": str(e)}), 500
