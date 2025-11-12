"""
Background Jobs Module
Handles periodic tasks:
1. Check vehicle time limits and send warnings
2. Check pending cube tests and send reminders
3. Send missed test warnings to admins
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import logging

from .models import db
from .models import (
    MaterialVehicleRegister, CubeTestRegister, TestReminder,
    ProjectSettings, User, ProjectMembership, Project
)
from .notifications import send_time_limit_warning, send_test_reminder, send_missed_test_warning

logger = logging.getLogger(__name__)


def check_vehicle_time_limits():
    """
    Background job: Check all vehicles on site for time limit violations
    Run every 15-30 minutes
    """
    try:
        logger.info("Starting vehicle time limit check...")
        
        # Get all projects with material vehicle addon enabled
        active_settings = db.session.query(ProjectSettings).filter(
            and_(
                ProjectSettings.enable_material_vehicle_addon == True,
                ProjectSettings.send_time_warnings == True
            )
        ).all()
        
        total_warnings = 0
        
        for settings in active_settings:
            project_id = settings.project_id
            allowed_hours = settings.vehicle_allowed_time_hours
            
            # Find RMC vehicles (Concrete only) exceeding time limit
            # Time warnings ONLY for RMC vehicles, not for other materials like Steel, Cement, etc.
            cutoff_time = datetime.utcnow() - timedelta(hours=allowed_hours)
            
            exceeded_vehicles = db.session.query(MaterialVehicleRegister).filter(
                and_(
                    MaterialVehicleRegister.project_id == project_id,
                    MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete']),
                    MaterialVehicleRegister.status == 'on_site',
                    MaterialVehicleRegister.entry_time <= cutoff_time,
                    MaterialVehicleRegister.time_warning_sent == False
                )
            ).all()
            
            if not exceeded_vehicles:
                continue
            
            logger.info(f"Project {project_id}: {len(exceeded_vehicles)} vehicles exceeded time limit")
            
            # Get quality engineers and admins for this project
            recipients = db.session.query(User).join(ProjectMembership).filter(
                and_(
                    ProjectMembership.project_id == project_id,
                    ProjectMembership.role.in_(['QualityEngineer', 'QualityManager', 'ProjectAdmin']),
                    ProjectMembership.is_active == True,
                    User.is_active == True
                )
            ).all()
            
            # Send notifications for each vehicle
            for vehicle in exceeded_vehicles:
                time_on_site = datetime.utcnow() - vehicle.entry_time
                hours_on_site = time_on_site.total_seconds() / 3600
                
                # Mark as exceeded
                vehicle.exceeded_time_limit = True
                vehicle.time_warning_sent = True
                vehicle.time_warning_sent_at = datetime.utcnow()
                
                notification_data = {
                    "vehicleNumber": vehicle.vehicle_number,
                    "materialType": vehicle.material_type,
                    "supplierName": vehicle.supplier_name or "Unknown",
                    "entryTime": vehicle.entry_time.strftime("%Y-%m-%d %H:%M"),
                    "hoursOnSite": round(hours_on_site, 1),
                    "allowedHours": allowed_hours,
                    "projectId": project_id
                }
                
                # Send to all recipients
                for user in recipients:
                    try:
                        send_time_limit_warning(user, notification_data)
                        total_warnings += 1
                    except Exception as e:
                        logger.error(f"Failed to send warning to {user.email}: {e}")
                
                logger.info(f"Sent warnings for vehicle {vehicle.vehicle_number} to {len(recipients)} users")
            
            db.session.commit()
        
        logger.info(f"Vehicle time limit check complete. Sent {total_warnings} warnings.")
        return total_warnings
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in vehicle time limit check: {e}")
        return 0


def check_pending_tests():
    """
    Background job: Check for tests scheduled today and send reminders
    Run once daily at project's configured reminder time (default 9:00 AM)
    """
    try:
        logger.info("Starting pending test reminder check...")
        
        today = datetime.utcnow().date()
        total_reminders = 0
        
        # Get all projects with test reminders enabled
        active_settings = db.session.query(ProjectSettings).filter(
            ProjectSettings.enable_test_reminders == True
        ).all()
        
        for settings in active_settings:
            project_id = settings.project_id
            
            # Find reminders scheduled for today that haven't been sent
            pending_reminders = db.session.query(TestReminder).filter(
                and_(
                    TestReminder.project_id == project_id,
                    TestReminder.reminder_date == today,
                    TestReminder.status == 'pending',
                    or_(
                        TestReminder.notification_sent_at == None,
                        TestReminder.notification_sent_at < datetime.utcnow() - timedelta(hours=23)
                    )
                )
            ).all()
            
            if not pending_reminders:
                continue
            
            logger.info(f"Project {project_id}: {len(pending_reminders)} test reminders to send")
            
            # Get recipients based on settings
            role_filter = []
            if settings.notify_project_admins:
                role_filter.append('ProjectAdmin')
            if settings.notify_quality_engineers:
                role_filter.extend(['QualityEngineer', 'QualityManager'])
            
            recipients = db.session.query(User).join(ProjectMembership).filter(
                and_(
                    ProjectMembership.project_id == project_id,
                    ProjectMembership.role.in_(role_filter),
                    ProjectMembership.is_active == True,
                    User.is_active == True
                )
            ).all()
            
            # Send reminders
            for reminder in pending_reminders:
                cube_test = db.session.query(CubeTestRegister).filter(
                    CubeTestRegister.id == reminder.cube_test_id
                ).first()
                
                if not cube_test:
                    continue
                
                test_data = {
                    "cubeId": cube_test.cube_id,
                    "testAge": reminder.test_age_days,
                    "scheduledDate": reminder.reminder_date.strftime("%Y-%m-%d"),
                    "batchNumber": cube_test.batch_number if cube_test.batch_number else "N/A",
                    "grade": cube_test.design_grade if cube_test.design_grade else "N/A",
                    "location": cube_test.location if cube_test.location else "N/A",
                }
                
                # Send to all recipients
                import json
                notified_users = []
                for user in recipients:
                    try:
                        if send_test_reminder(user, test_data):
                            notified_users.append(user.id)
                            total_reminders += 1
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {user.email}: {e}")
                
                # Update reminder status
                reminder.status = 'sent'
                reminder.notification_sent_at = datetime.utcnow()
                reminder.notified_user_ids = json.dumps(notified_users)
                
                logger.info(f"Sent reminders for cube {cube_test.cube_id} to {len(notified_users)} users")
            
            db.session.commit()
        
        logger.info(f"Test reminder check complete. Sent {total_reminders} reminders.")
        return total_reminders
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in test reminder check: {e}")
        return 0


def check_missed_tests():
    """
    Background job: Check for tests that were scheduled but not performed
    Run once daily in evening (e.g., 6:00 PM) to detect missed tests
    Send warnings to project admins
    """
    try:
        logger.info("Starting missed test check...")
        
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        total_warnings = 0
        
        # Get all projects with test reminders enabled
        active_settings = db.session.query(ProjectSettings).filter(
            and_(
                ProjectSettings.enable_test_reminders == True,
                ProjectSettings.notify_project_admins == True
            )
        ).all()
        
        for settings in active_settings:
            project_id = settings.project_id
            
            # Find reminders from yesterday that weren't completed
            missed_reminders = db.session.query(TestReminder).filter(
                and_(
                    TestReminder.project_id == project_id,
                    TestReminder.reminder_date == yesterday,
                    TestReminder.test_completed == False
                )
            ).all()
            
            if not missed_reminders:
                continue
            
            logger.info(f"Project {project_id}: {len(missed_reminders)} missed tests detected")
            
            # Get project admins
            admins = db.session.query(User).join(ProjectMembership).filter(
                and_(
                    ProjectMembership.project_id == project_id,
                    ProjectMembership.role == 'ProjectAdmin',
                    ProjectMembership.is_active == True,
                    User.is_active == True
                )
            ).all()
            
            if not admins:
                logger.warning(f"No project admins found for project {project_id}")
                continue
            
            # Get project name
            project = db.session.query(Project).filter(Project.id == project_id).first()
            project_name = project.name if project else f"Project {project_id}"
            
            # Prepare missed tests data
            missed_tests = []
            for reminder in missed_reminders:
                cube_test = db.session.query(CubeTestRegister).filter(
                    CubeTestRegister.id == reminder.cube_test_id
                ).first()
                
                if cube_test:
                    missed_tests.append({
                        "cubeId": cube_test.cube_id,
                        "testAge": reminder.test_age_days,
                        "scheduledDate": reminder.reminder_date.strftime("%Y-%m-%d"),
                        "batchNumber": cube_test.batch_number or "N/A",
                        "grade": cube_test.design_grade or "N/A"
                    })
            
            warning_data = {
                "projectName": project_name,
                "missedTests": missed_tests
            }
            
            # Send warnings to all admins
            for admin in admins:
                try:
                    if send_missed_test_warning(admin, warning_data):
                        total_warnings += 1
                except Exception as e:
                    logger.error(f"Failed to send warning to {admin.email}: {e}")
            
            logger.info(f"Sent missed test warnings for project {project_name} to {len(admins)} admins")
        
        logger.info(f"Missed test check complete. Sent {total_warnings} warnings.")
        return total_warnings
        
    except Exception as e:
        logger.error(f"Error in missed test check: {e}")
        return 0


def run_all_background_jobs():
    """
    Run all background jobs
    This can be called by a cron job or scheduler
    """
    logger.info("=" * 60)
    logger.info("Running all background jobs...")
    logger.info("=" * 60)
    
    results = {
        "time_warnings": check_vehicle_time_limits(),
        "test_reminders": check_pending_tests(),
        "missed_tests": check_missed_tests()
    }
    
    logger.info("=" * 60)
    logger.info(f"All jobs complete. Results: {results}")
    logger.info("=" * 60)
    
    return results


# API endpoint to manually trigger jobs (for testing or manual runs)
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

background_jobs_bp = Blueprint('background_jobs', __name__, url_prefix='/api/background-jobs')


@background_jobs_bp.route('/run-vehicle-check', methods=['POST'])
@jwt_required()
def run_vehicle_check():
    """Manually trigger vehicle time limit check (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user or not (user.is_support_admin or user.is_company_admin):
            return jsonify({"error": "Admin access required"}), 403
        
        count = check_vehicle_time_limits()
        
        return jsonify({
            "success": True,
            "message": f"Vehicle time limit check complete",
            "warningsSent": count
        }), 200
        
    except Exception as e:
        logger.error(f"Error running manual vehicle check: {e}")
        return jsonify({"error": str(e)}), 500


@background_jobs_bp.route('/run-test-reminders', methods=['POST'])
@jwt_required()
def run_test_reminders():
    """Manually trigger test reminder check (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user or not (user.is_support_admin or user.is_company_admin):
            return jsonify({"error": "Admin access required"}), 403
        
        count = check_pending_tests()
        
        return jsonify({
            "success": True,
            "message": f"Test reminder check complete",
            "remindersSent": count
        }), 200
        
    except Exception as e:
        logger.error(f"Error running manual test reminder check: {e}")
        return jsonify({"error": str(e)}), 500


@background_jobs_bp.route('/run-missed-test-check', methods=['POST'])
@jwt_required()
def run_missed_test_check():
    """Manually trigger missed test check (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user or not (user.is_support_admin or user.is_company_admin):
            return jsonify({"error": "Admin access required"}), 403
        
        count = check_missed_tests()
        
        return jsonify({
            "success": True,
            "message": f"Missed test check complete",
            "warningsSent": count
        }), 200
        
    except Exception as e:
        logger.error(f"Error running manual missed test check: {e}")
        return jsonify({"error": str(e)}), 500


@background_jobs_bp.route('/run-all', methods=['POST'])
@jwt_required()
def run_all_jobs():
    """Manually trigger all background jobs (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user or not (user.is_support_admin or user.is_company_admin):
            return jsonify({"error": "Admin access required"}), 403
        
        results = run_all_background_jobs()
        
        return jsonify({
            "success": True,
            "message": "All background jobs complete",
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error running all background jobs: {e}")
        return jsonify({"error": str(e)}), 500
