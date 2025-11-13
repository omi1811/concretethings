"""
Permit-to-Work (PTW) Management API
Complete workflow with multi-signature approval

Workflow:
1. Contractor fills permit request → Saves as draft
2. Contractor submits permit → Sends to Site Engineer
3. Site Engineer reviews → Approves/Rejects
4. Safety Officer reviews → Final Approval/Rejection
5. Work proceeds (permit valid for specified hours)
6. Contractor closes permit after work completion
7. Engineer/Safety Officer verifies closure

All actions are digitally signed and logged.
"""
import logging
from datetime import datetime, timedelta
import hashlib

from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, func

from .auth import jwt_required, get_current_user
from .db import session_scope
from .permit_to_work_models import (
    PermitType, WorkPermit, PermitSignature, PermitExtension,
    PermitChecklist, PermitAuditLog
)
from .models import User, Company, Project
from .notifications import send_whatsapp_alert
from .email_notifications import send_email

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
ptw_bp = Blueprint("ptw", __name__, url_prefix="/api/safety/permits")


def generate_permit_number(permit_type_code):
    """Generate unique permit number: PTW-CODE-YYYYMMDD-NNNNN"""
    today = datetime.now().strftime("%Y%m%d")
    with session_scope() as session:
        latest = session.query(WorkPermit).filter(
            WorkPermit.permit_number.like(f"PTW-{permit_type_code}-{today}-%")
        ).order_by(WorkPermit.id.desc()).first()
        
        if latest:
            last_seq = int(latest.permit_number.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"PTW-{permit_type_code}-{today}-{new_seq:05d}"


def send_permit_notification(permit, notification_type, recipient_user, session):
    """
    Send permit notifications via WhatsApp/Email
    
    notification_type: permit_submitted, engineer_approved, safety_approved, 
                      permit_rejected, permit_expires_soon, permit_closed
    """
    try:
        messages = {
            "permit_submitted": {
                "subject": f"New Permit Requires Review: {permit.permit_number}",
                "message": f"""
🟡 *Work Permit Pending Review*

*Permit Number:* {permit.permit_number}
*Work:* {permit.work_description}
*Location:* {permit.work_location}
*Contractor:* {permit.contractor_company}
*Scheduled:* {permit.work_date.strftime('%d-%b-%Y')} {permit.start_time.strftime('%H:%M')}

Please review and approve this permit.

_Automated alert from ProSite Safety_
"""
            },
            "engineer_approved": {
                "subject": f"Permit Approved by Site Engineer: {permit.permit_number}",
                "message": f"""
🟢 *Site Engineer Approval Received*

*Permit Number:* {permit.permit_number}
*Work:* {permit.work_description}

Site Engineer has approved. Awaiting Safety Officer approval.

_Automated alert from ProSite Safety_
"""
            },
            "safety_approved": {
                "subject": f"Work Permit APPROVED: {permit.permit_number}",
                "message": f"""
✅ *Work Permit APPROVED*

*Permit Number:* {permit.permit_number}
*Work:* {permit.work_description}
*Location:* {permit.work_location}
*Valid From:* {permit.valid_from.strftime('%d-%b-%Y %H:%M')}
*Valid Until:* {permit.valid_until.strftime('%d-%b-%Y %H:%M')}

⚠️ Ensure all safety precautions are followed.

_Automated alert from ProSite Safety_
"""
            },
            "permit_rejected": {
                "subject": f"Work Permit REJECTED: {permit.permit_number}",
                "message": f"""
❌ *Work Permit REJECTED*

*Permit Number:* {permit.permit_number}
*Work:* {permit.work_description}

Please review rejection comments and resubmit with necessary corrections.

_Automated alert from ProSite Safety_
"""
            },
            "permit_expires_soon": {
                "subject": f"Permit Expiring Soon: {permit.permit_number}",
                "message": f"""
⏰ *Work Permit Expiring Soon*

*Permit Number:* {permit.permit_number}
*Expires:* {permit.valid_until.strftime('%d-%b-%Y %H:%M')}

If work is incomplete, request extension immediately.

_Automated alert from ProSite Safety_
"""
            },
            "permit_closed": {
                "subject": f"Permit Closed: {permit.permit_number}",
                "message": f"""
✅ *Work Permit Closed*

*Permit Number:* {permit.permit_number}
*Work:* {permit.work_description}
*Completed:* {permit.work_completed_at.strftime('%d-%b-%Y %H:%M')}

Work completed and permit closed.

_Automated alert from ProSite Safety_
"""
            }
        }
        
        notification_content = messages.get(notification_type, messages["permit_submitted"])
        
        # Send WhatsApp
        if recipient_user and recipient_user.phone:
            try:
                send_whatsapp_alert(recipient_user.phone, notification_content["message"])
                logger.info(f"WhatsApp sent to {recipient_user.phone} for permit {permit.permit_number}")
            except Exception as e:
                logger.error(f"WhatsApp failed for permit {permit.permit_number}: {str(e)}")
        
        # Send Email
        if recipient_user and recipient_user.email:
            try:
                email_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>{notification_content["subject"]}</h2>
                    <div style="white-space: pre-wrap;">{notification_content["message"]}</div>
                </div>
                """
                send_email(
                    to_email=recipient_user.email,
                    subject=notification_content["subject"],
                    body=email_html
                )
                logger.info(f"Email sent to {recipient_user.email} for permit {permit.permit_number}")
            except Exception as e:
                logger.error(f"Email failed for permit {permit.permit_number}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Failed to send permit notification: {str(e)}")


def log_permit_action(permit_id, action_type, action_description, performed_by, session, previous_state=None, new_state=None):
    """Log all permit actions for audit trail"""
    audit_log = PermitAuditLog(
        permit_id=permit_id,
        action_type=action_type,
        action_description=action_description,
        performed_by=performed_by,
        previous_state=previous_state,
        new_state=new_state
    )
    session.add(audit_log)


# ============================================================================
# Permit Types Management
# ============================================================================

@ptw_bp.route("/types", methods=["GET"])
@jwt_required
def get_permit_types():
    """Get all permit types for company"""
    current_user = get_current_user()
    
    with session_scope() as session:
        permit_types = session.query(PermitType).filter_by(
            company_id=current_user.company_id,
            is_active=True
        ).all()
        
        return jsonify({
            "success": True,
            "permit_types": [pt.to_dict() for pt in permit_types]
        }), 200


@ptw_bp.route("/types", methods=["POST"])
@jwt_required
def create_permit_type():
    """Create new permit type (Admin only)"""
    current_user = get_current_user()
    data = request.get_json()
    
    required = ["permit_type_name", "permit_code", "description", "risk_level"]
    if not all(k in data for k in required):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    with session_scope() as session:
        permit_type = PermitType(
            company_id=current_user.company_id,
            permit_type_name=data["permit_type_name"],
            permit_code=data["permit_code"],
            description=data["description"],
            risk_level=data["risk_level"],
            required_ppe=data.get("required_ppe"),
            safety_precautions=data.get("safety_precautions"),
            required_equipment=data.get("required_equipment"),
            requires_site_engineer=data.get("requires_site_engineer", True),
            requires_safety_officer=data.get("requires_safety_officer", True),
            max_validity_hours=data.get("max_validity_hours", 8),
            created_by=current_user.id
        )
        session.add(permit_type)
        session.commit()
        
        return jsonify({
            "success": True,
            "message": "Permit type created",
            "permit_type": permit_type.to_dict()
        }), 201


# ============================================================================
# Contractor: Create & Submit Permit
# ============================================================================

@ptw_bp.route("", methods=["POST"])
@jwt_required
def create_permit():
    """
    Contractor creates work permit (saves as draft)
    """
    current_user = get_current_user()
    data = request.get_json()
    
    required = ["project_id", "permit_type_id", "work_description", "work_location",
                "contractor_company", "work_date", "start_time", "end_time",
                "number_of_workers", "identified_hazards", "safety_measures", "ppe_required",
                "emergency_contact_name", "emergency_contact_phone"]
    
    if not all(k in data for k in required):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    with session_scope() as session:
        # Get permit type to generate number
        permit_type = session.query(PermitType).filter_by(id=data["permit_type_id"]).first()
        if not permit_type:
            return jsonify({"success": False, "message": "Invalid permit type"}), 400
        
        # Generate permit number
        permit_number = generate_permit_number(permit_type.permit_code)
        
        # Calculate validity period
        work_date_str = data["work_date"]
        start_time_str = data["start_time"]
        end_time_str = data["end_time"]
        
        valid_from = datetime.fromisoformat(f"{work_date_str}T{start_time_str}")
        valid_until = datetime.fromisoformat(f"{work_date_str}T{end_time_str}")
        
        # Create permit
        permit = WorkPermit(
            company_id=current_user.company_id,
            project_id=data["project_id"],
            permit_type_id=data["permit_type_id"],
            permit_number=permit_number,
            work_description=data["work_description"],
            work_location=data["work_location"],
            geo_location=data.get("geo_location"),
            contractor_company=data["contractor_company"],
            contractor_supervisor=current_user.id,
            contractor_phone=data.get("contractor_phone", current_user.phone),
            number_of_workers=data["number_of_workers"],
            work_date=datetime.fromisoformat(work_date_str).date(),
            start_time=datetime.fromisoformat(f"{work_date_str}T{start_time_str}").time(),
            end_time=datetime.fromisoformat(f"{work_date_str}T{end_time_str}").time(),
            estimated_duration_hours=data.get("estimated_duration_hours", 8),
            valid_from=valid_from,
            valid_until=valid_until,
            identified_hazards=data["identified_hazards"],
            safety_measures=data["safety_measures"],
            ppe_required=data["ppe_required"],
            equipment_checklist=data.get("equipment_checklist"),
            requires_isolation=data.get("requires_isolation", False),
            isolation_details=data.get("isolation_details"),
            emergency_contact_name=data["emergency_contact_name"],
            emergency_contact_phone=data["emergency_contact_phone"],
            nearest_hospital=data.get("nearest_hospital"),
            first_aid_location=data.get("first_aid_location"),
            status="draft",
            workflow_stage="contractor_request",
            attachments=data.get("attachments"),
            photos=data.get("photos")
        )
        session.add(permit)
        session.flush()
        
        # Log action
        log_permit_action(
            permit.id, "created", f"Permit created by {current_user.username}",
            current_user.id, session
        )
        
        session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Permit {permit_number} created as draft",
            "permit": permit.to_dict()
        }), 201


@ptw_bp.route("/<int:permit_id>/submit", methods=["POST"])
@jwt_required
def submit_permit(permit_id):
    """
    Contractor submits permit for approval
    Creates contractor signature and sends to Site Engineer
    """
    current_user = get_current_user()
    data = request.get_json()
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id,
            contractor_supervisor=current_user.id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        if permit.status != "draft":
            return jsonify({"success": False, "message": "Permit already submitted"}), 400
        
        # Update permit status
        permit.status = "submitted"
        permit.workflow_stage = "site_engineer_review"
        permit.submitted_at = datetime.utcnow()
        
        # Create contractor signature
        signature = PermitSignature(
            permit_id=permit.id,
            signer_role="contractor",
            signer_id=current_user.id,
            signer_name=current_user.username,
            signer_designation=data.get("designation", "Contractor Supervisor"),
            signature_type=data.get("signature_type", "digital"),
            signature_data=data.get("signature_data"),
            action="request",
            comments=data.get("comments"),
            ip_address=request.remote_addr
        )
        session.add(signature)
        
        # Log action
        log_permit_action(
            permit.id, "submitted", f"Permit submitted by contractor {current_user.username}",
            current_user.id, session,
            previous_state={"status": "draft"},
            new_state={"status": "submitted"}
        )
        
        session.commit()
        
        # Send notification to site engineer
        # In real implementation, find assigned site engineer for this project
        # For now, we'll notify via general channel
        
        logger.info(f"Permit {permit.permit_number} submitted for approval")
        
        return jsonify({
            "success": True,
            "message": f"Permit {permit.permit_number} submitted for Site Engineer review",
            "permit": permit.to_dict()
        }), 200


# ============================================================================
# Site Engineer: Review & Approve
# ============================================================================

@ptw_bp.route("/<int:permit_id>/engineer-review", methods=["POST"])
@jwt_required
def engineer_review_permit(permit_id):
    """
    Site Engineer approves/rejects permit
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if "approved" not in data:
        return jsonify({"success": False, "message": "Approval status required"}), 400
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        if permit.workflow_stage != "site_engineer_review":
            return jsonify({"success": False, "message": "Permit not in correct stage"}), 400
        
        if data["approved"]:
            # Approve - send to Safety Officer
            permit.workflow_stage = "safety_officer_review"
            
            signature = PermitSignature(
                permit_id=permit.id,
                signer_role="site_engineer",
                signer_id=current_user.id,
                signer_name=current_user.username,
                signer_designation=data.get("designation", "Site Engineer"),
                signature_type=data.get("signature_type", "digital"),
                signature_data=data.get("signature_data"),
                action="approve",
                comments=data.get("comments", "Reviewed and approved"),
                ip_address=request.remote_addr
            )
            session.add(signature)
            
            log_permit_action(
                permit.id, "engineer_approved", f"Approved by Site Engineer {current_user.username}",
                current_user.id, session
            )
            
            message = f"Permit {permit.permit_number} approved by Site Engineer. Sent to Safety Officer."
        else:
            # Reject
            permit.status = "rejected"
            permit.workflow_stage = "contractor_request"
            
            signature = PermitSignature(
                permit_id=permit.id,
                signer_role="site_engineer",
                signer_id=current_user.id,
                signer_name=current_user.username,
                signer_designation=data.get("designation", "Site Engineer"),
                signature_type=data.get("signature_type", "digital"),
                signature_data=data.get("signature_data"),
                action="reject",
                comments=data.get("comments", "Rejected. Please revise."),
                ip_address=request.remote_addr
            )
            session.add(signature)
            
            log_permit_action(
                permit.id, "engineer_rejected", f"Rejected by Site Engineer {current_user.username}",
                current_user.id, session
            )
            
            message = f"Permit {permit.permit_number} rejected by Site Engineer."
        
        session.commit()
        
        return jsonify({
            "success": True,
            "message": message,
            "permit": permit.to_dict()
        }), 200


# ============================================================================
# Safety Officer: Final Approval
# ============================================================================

@ptw_bp.route("/<int:permit_id>/safety-review", methods=["POST"])
@jwt_required
def safety_review_permit(permit_id):
    """
    Safety Officer gives final approval/rejection
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if "approved" not in data:
        return jsonify({"success": False, "message": "Approval status required"}), 400
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        if permit.workflow_stage != "safety_officer_review":
            return jsonify({"success": False, "message": "Permit not in correct stage"}), 400
        
        if data["approved"]:
            # Final approval - permit now active
            permit.status = "approved"
            permit.workflow_stage = "approved"
            permit.approved_at = datetime.utcnow()
            
            signature = PermitSignature(
                permit_id=permit.id,
                signer_role="safety_officer",
                signer_id=current_user.id,
                signer_name=current_user.username,
                signer_designation=data.get("designation", "Safety Officer"),
                signature_type=data.get("signature_type", "digital"),
                signature_data=data.get("signature_data"),
                action="approve",
                comments=data.get("comments", "Final approval granted. Work may proceed."),
                ip_address=request.remote_addr
            )
            session.add(signature)
            
            log_permit_action(
                permit.id, "safety_approved", f"Final approval by Safety Officer {current_user.username}",
                current_user.id, session
            )
            
            # Send approval notification to contractor
            contractor = session.query(User).filter_by(id=permit.contractor_supervisor).first()
            send_permit_notification(permit, "safety_approved", contractor, session)
            
            message = f"Permit {permit.permit_number} APPROVED. Work authorized to proceed."
        else:
            # Reject
            permit.status = "rejected"
            permit.workflow_stage = "contractor_request"
            
            signature = PermitSignature(
                permit_id=permit.id,
                signer_role="safety_officer",
                signer_id=current_user.id,
                signer_name=current_user.username,
                signer_designation=data.get("designation", "Safety Officer"),
                signature_type=data.get("signature_type", "digital"),
                signature_data=data.get("signature_data"),
                action="reject",
                comments=data.get("comments", "Rejected. Safety concerns not addressed."),
                ip_address=request.remote_addr
            )
            session.add(signature)
            
            log_permit_action(
                permit.id, "safety_rejected", f"Rejected by Safety Officer {current_user.username}",
                current_user.id, session
            )
            
            # Send rejection notification
            contractor = session.query(User).filter_by(id=permit.contractor_supervisor).first()
            send_permit_notification(permit, "permit_rejected", contractor, session)
            
            message = f"Permit {permit.permit_number} rejected by Safety Officer."
        
        session.commit()
        
        return jsonify({
            "success": True,
            "message": message,
            "permit": permit.to_dict()
        }), 200


# ============================================================================
# Permit Closure
# ============================================================================

@ptw_bp.route("/<int:permit_id>/close", methods=["POST"])
@jwt_required
def close_permit(permit_id):
    """
    Contractor closes permit after work completion
    Requires verification by engineer/safety officer
    """
    current_user = get_current_user()
    data = request.get_json()
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        if permit.status not in ["approved", "in_progress"]:
            return jsonify({"success": False, "message": "Permit cannot be closed"}), 400
        
        # Update permit
        permit.status = "completed"
        permit.workflow_stage = "closure_verification"
        permit.work_completed_at = datetime.utcnow()
        
        # Contractor closing signature
        signature = PermitSignature(
            permit_id=permit.id,
            signer_role="closing_contractor",
            signer_id=current_user.id,
            signer_name=current_user.username,
            signer_designation=data.get("designation", "Contractor Supervisor"),
            signature_type=data.get("signature_type", "digital"),
            signature_data=data.get("signature_data"),
            action="close",
            comments=data.get("comments", "Work completed. Site cleaned and secured."),
            ip_address=request.remote_addr
        )
        session.add(signature)
        
        log_permit_action(
            permit.id, "closure_requested", f"Closure requested by {current_user.username}",
            current_user.id, session
        )
        
        session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Permit {permit.permit_number} closure requested. Awaiting verification.",
            "permit": permit.to_dict()
        }), 200


@ptw_bp.route("/<int:permit_id>/verify-closure", methods=["POST"])
@jwt_required
def verify_closure(permit_id):
    """
    Engineer/Safety Officer verifies permit closure
    """
    current_user = get_current_user()
    data = request.get_json()
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        if permit.workflow_stage != "closure_verification":
            return jsonify({"success": False, "message": "Permit not ready for closure verification"}), 400
        
        # Final closure
        permit.status = "closed"
        permit.workflow_stage = "closed"
        permit.closed_at = datetime.utcnow()
        
        # Verification signature
        signature = PermitSignature(
            permit_id=permit.id,
            signer_role="closing_engineer",
            signer_id=current_user.id,
            signer_name=current_user.username,
            signer_designation=data.get("designation", "Site Engineer"),
            signature_type=data.get("signature_type", "digital"),
            signature_data=data.get("signature_data"),
            action="verify_closure",
            comments=data.get("comments", "Closure verified. Site inspected and cleared."),
            ip_address=request.remote_addr
        )
        session.add(signature)
        
        log_permit_action(
            permit.id, "closed", f"Permit closed and verified by {current_user.username}",
            current_user.id, session
        )
        
        session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Permit {permit.permit_number} closed successfully.",
            "permit": permit.to_dict()
        }), 200


# ============================================================================
# Get Permits & Details
# ============================================================================

@ptw_bp.route("", methods=["GET"])
@jwt_required
def get_permits():
    """
    Get all permits with filtering
    Filters: status, workflow_stage, project_id, contractor, date_from, date_to
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        query = session.query(WorkPermit).filter_by(company_id=current_user.company_id)
        
        # Filters
        if request.args.get("status"):
            query = query.filter_by(status=request.args.get("status"))
        
        if request.args.get("workflow_stage"):
            query = query.filter_by(workflow_stage=request.args.get("workflow_stage"))
        
        if request.args.get("project_id"):
            query = query.filter_by(project_id=int(request.args.get("project_id")))
        
        if request.args.get("contractor_id"):
            query = query.filter_by(contractor_supervisor=int(request.args.get("contractor_id")))
        
        # Role-based filtering
        if current_user.role == "contractor":
            query = query.filter_by(contractor_supervisor=current_user.id)
        
        permits = query.order_by(WorkPermit.created_at.desc()).all()
        
        return jsonify({
            "success": True,
            "permits": [p.to_dict() for p in permits]
        }), 200


@ptw_bp.route("/<int:permit_id>", methods=["GET"])
@jwt_required
def get_permit_details(permit_id):
    """
    Get complete permit details including signatures and audit log
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        # Get all signatures
        signatures = session.query(PermitSignature).filter_by(
            permit_id=permit_id
        ).order_by(PermitSignature.signed_at).all()
        
        # Get audit log
        audit_logs = session.query(PermitAuditLog).filter_by(
            permit_id=permit_id
        ).order_by(PermitAuditLog.action_timestamp.desc()).limit(20).all()
        
        return jsonify({
            "success": True,
            "permit": permit.to_dict(),
            "signatures": [s.to_dict() for s in signatures],
            "audit_log": [log.to_dict() for log in audit_logs]
        }), 200


@ptw_bp.route("/<int:permit_id>/signboard", methods=["GET"])
@jwt_required
def get_permit_signboard(permit_id):
    """
    Get signature board showing all approvers
    This creates a visual record of who signed
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        permit = session.query(WorkPermit).filter_by(
            id=permit_id,
            company_id=current_user.company_id
        ).first()
        
        if not permit:
            return jsonify({"success": False, "message": "Permit not found"}), 404
        
        # Get all signatures
        signatures = session.query(PermitSignature).filter_by(
            permit_id=permit_id
        ).order_by(PermitSignature.signed_at).all()
        
        # Build signboard
        signboard = {
            "permit_number": permit.permit_number,
            "work_description": permit.work_description,
            "status": permit.status,
            "signatures": []
        }
        
        for sig in signatures:
            signboard["signatures"].append({
                "role": sig.signer_role,
                "name": sig.signer_name,
                "designation": sig.signer_designation,
                "action": sig.action,
                "signed_at": sig.signed_at.isoformat() if sig.signed_at else None,
                "comments": sig.comments
            })
        
        return jsonify({
            "success": True,
            "signboard": signboard
        }), 200


@ptw_bp.route("/dashboard", methods=["GET"])
@jwt_required
def permit_dashboard():
    """
    Permit dashboard with counts
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        if current_user.role == "contractor":
            query = session.query(WorkPermit).filter_by(
                company_id=current_user.company_id,
                contractor_supervisor=current_user.id
            )
        else:
            query = session.query(WorkPermit).filter_by(
                company_id=current_user.company_id
            )
        
        draft = query.filter_by(status="draft").count()
        submitted = query.filter_by(status="submitted").count()
        approved = query.filter_by(status="approved").count()
        in_progress = query.filter_by(status="in_progress").count()
        completed = query.filter_by(status="completed").count()
        closed = query.filter_by(status="closed").count()
        rejected = query.filter_by(status="rejected").count()
        
        # Permits needing action
        engineer_review = query.filter_by(workflow_stage="site_engineer_review").count()
        safety_review = query.filter_by(workflow_stage="safety_officer_review").count()
        closure_verification = query.filter_by(workflow_stage="closure_verification").count()
        
        return jsonify({
            "success": True,
            "dashboard": {
                "draft": draft,
                "submitted": submitted,
                "approved": approved,
                "in_progress": in_progress,
                "completed": completed,
                "closed": closed,
                "rejected": rejected,
                "pending_actions": {
                    "engineer_review": engineer_review,
                    "safety_review": safety_review,
                    "closure_verification": closure_verification
                }
            }
        }), 200
