"""
Non-Conformance (NC) Management API for Safety Module
Handles NC lifecycle with contractor notifications
"""
import logging
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, func

from .auth import jwt_required, get_current_user
from .db import session_scope
from .safety_nc_models import NonConformance, NCComment, ContractorNotification
from .models import User, Company, Project
from .notifications import send_whatsapp_alert
from .email_notifications import send_email

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
nc_bp = Blueprint("nc", __name__, url_prefix="/api/safety/nc")


def generate_nc_number():
    """Generate unique NC number: NC-YYYYMMDD-NNNNN"""
    today = datetime.now().strftime("%Y%m%d")
    with session_scope() as session:
        latest = session.query(NonConformance).filter(
            NonConformance.nc_number.like(f"NC-{today}-%")
        ).order_by(NonConformance.id.desc()).first()
        
        if latest:
            last_seq = int(latest.nc_number.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"NC-{today}-{new_seq:05d}"


def send_nc_notification(nc, notification_type, session):
    """
    Send NC notification to contractor via WhatsApp, Email, and In-App
    
    notification_type: nc_raised, nc_overdue, nc_rejected, nc_approved
    """
    try:
        # Get contractor user info
        if nc.assigned_to_user:
            contractor = session.query(User).filter_by(id=nc.assigned_to_user).first()
        else:
            # Try to find contractor by company name
            contractor = None
        
        # Prepare notification content
        messages = {
            "nc_raised": {
                "subject": f"New NC Raised: {nc.nc_number}",
                "message": f"""
🔴 *Non-Conformance Raised*

*NC Number:* {nc.nc_number}
*Title:* {nc.nc_title}
*Severity:* {nc.severity.upper()}
*Category:* {nc.category or 'General'}
*Location:* {nc.location or 'N/A'}

*Description:*
{nc.nc_description}

*Assigned To:* {nc.assigned_to_contractor}
*Due Date:* {nc.due_date.strftime('%d-%b-%Y %H:%M')}

⚠️ Please submit your corrective action plan ASAP.

_Automated alert from ProSite Safety_
"""
            },
            "nc_overdue": {
                "subject": f"NC Overdue: {nc.nc_number}",
                "message": f"""
⚠️ *Non-Conformance OVERDUE*

*NC Number:* {nc.nc_number}
*Title:* {nc.nc_title}
*Due Date:* {nc.due_date.strftime('%d-%b-%Y %H:%M')}

This NC is now overdue. Please submit corrective actions immediately.

_Automated alert from ProSite Safety_
"""
            },
            "nc_rejected": {
                "subject": f"NC Action Rejected: {nc.nc_number}",
                "message": f"""
❌ *Corrective Action Rejected*

*NC Number:* {nc.nc_number}
*Title:* {nc.nc_title}

*Verification Notes:*
{nc.verification_notes}

Please revise and resubmit your corrective actions.

_Automated alert from ProSite Safety_
"""
            },
            "nc_approved": {
                "subject": f"NC Closed: {nc.nc_number}",
                "message": f"""
✅ *Non-Conformance Closed*

*NC Number:* {nc.nc_number}
*Title:* {nc.nc_title}

Your corrective actions have been verified and approved.

*Closure Remarks:*
{nc.closure_remarks or 'No remarks'}

_Automated alert from ProSite Safety_
"""
            }
        }
        
        notification_content = messages.get(notification_type, messages["nc_raised"])
        
        # Send WhatsApp notification
        if contractor and contractor.phone:
            try:
                send_whatsapp_alert(contractor.phone, notification_content["message"])
                logger.info(f"WhatsApp notification sent to {contractor.phone} for NC {nc.nc_number}")
                
                # Log notification
                notification = ContractorNotification(
                    company_id=nc.company_id,
                    project_id=nc.project_id,
                    notification_type=notification_type,
                    notification_channel="whatsapp",
                    recipient_contractor=nc.assigned_to_contractor,
                    recipient_user=contractor.id if contractor else None,
                    recipient_phone=contractor.phone if contractor else None,
                    nc_id=nc.id,
                    subject=notification_content["subject"],
                    message=notification_content["message"],
                    delivery_status="sent"
                )
                session.add(notification)
            except Exception as e:
                logger.error(f"WhatsApp notification failed for NC {nc.nc_number}: {str(e)}")
        
        # Send Email notification
        if contractor and contractor.email:
            try:
                email_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>{notification_content["subject"]}</h2>
                    <div style="white-space: pre-wrap;">{notification_content["message"]}</div>
                </div>
                """
                send_email(
                    to_email=contractor.email,
                    subject=notification_content["subject"],
                    body=email_html
                )
                logger.info(f"Email notification sent to {contractor.email} for NC {nc.nc_number}")
                
                # Log notification
                notification = ContractorNotification(
                    company_id=nc.company_id,
                    project_id=nc.project_id,
                    notification_type=notification_type,
                    notification_channel="email",
                    recipient_contractor=nc.assigned_to_contractor,
                    recipient_user=contractor.id if contractor else None,
                    recipient_email=contractor.email if contractor else None,
                    nc_id=nc.id,
                    subject=notification_content["subject"],
                    message=notification_content["message"],
                    delivery_status="sent"
                )
                session.add(notification)
            except Exception as e:
                logger.error(f"Email notification failed for NC {nc.nc_number}: {str(e)}")
        
        session.commit()
        
    except Exception as e:
        logger.error(f"Failed to send NC notification: {str(e)}")


@nc_bp.route("", methods=["GET"])
@jwt_required()
def get_ncs():
    """
    Get all NCs with filtering
    Query params: project_id, contractor, severity, status, is_overdue
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        # Base query - filter by company
        query = session.query(NonConformance).filter_by(company_id=current_user.company_id)
        
        # Filters
        if request.args.get("project_id"):
            query = query.filter_by(project_id=int(request.args.get("project_id")))
        
        if request.args.get("contractor"):
            query = query.filter_by(assigned_to_contractor=request.args.get("contractor"))
        
        if request.args.get("severity"):
            query = query.filter_by(severity=request.args.get("severity"))
        
        if request.args.get("status"):
            query = query.filter_by(verification_status=request.args.get("status"))
        
        if request.args.get("is_overdue") == "true":
            query = query.filter_by(is_overdue=True)
        
        # If user is contractor, show only their NCs
        if current_user.role == "contractor":
            query = query.filter_by(assigned_to_user=current_user.id)
        
        ncs = query.order_by(NonConformance.raised_at.desc()).all()
        
        return jsonify({
            "success": True,
            "ncs": [nc.to_dict() for nc in ncs]
        }), 200


@nc_bp.route("", methods=["POST"])
@jwt_required()
def create_nc():
    """
    Create new NC (by safety officer)
    Body: nc_title, nc_description, severity, category, assigned_to_contractor, 
          assigned_to_user, location, due_date, evidence_photos
    """
    current_user = get_current_user()
    data = request.get_json()
    
    # Validation
    if not all(k in data for k in ["nc_title", "nc_description", "severity", "project_id", "due_date"]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    with session_scope() as session:
        # Generate NC number
        nc_number = generate_nc_number()
        
        # Create NC
        nc = NonConformance(
            company_id=current_user.company_id,
            project_id=data["project_id"],
            nc_number=nc_number,
            nc_title=data["nc_title"],
            nc_description=data["nc_description"],
            severity=data["severity"],
            category=data.get("category"),
            assigned_to_contractor=data.get("assigned_to_contractor"),
            assigned_to_user=data.get("assigned_to_user"),
            location=data.get("location"),
            geo_location=data.get("geo_location"),
            evidence_photos=data.get("evidence_photos"),
            evidence_videos=data.get("evidence_videos"),
            due_date=datetime.fromisoformat(data["due_date"]),
            raised_by=current_user.id,
            verification_status="pending_action"
        )
        session.add(nc)
        session.commit()
        
        # Send notification to contractor
        send_nc_notification(nc, "nc_raised", session)
        
        logger.info(f"NC created: {nc_number} by user {current_user.id}")
        
        return jsonify({
            "success": True,
            "message": f"NC {nc_number} created and contractor notified",
            "nc": nc.to_dict()
        }), 201


@nc_bp.route("/<int:nc_id>", methods=["GET"])
@jwt_required()
def get_nc_details(nc_id):
    """Get NC details with comments"""
    current_user = get_current_user()
    
    with session_scope() as session:
        nc = session.query(NonConformance).filter_by(
            id=nc_id,
            company_id=current_user.company_id
        ).first()
        
        if not nc:
            return jsonify({"success": False, "message": "NC not found"}), 404
        
        # Get comments
        comments = session.query(NCComment).filter_by(nc_id=nc_id).order_by(NCComment.created_at).all()
        
        return jsonify({
            "success": True,
            "nc": nc.to_dict(),
            "comments": [c.to_dict() for c in comments]
        }), 200


@nc_bp.route("/<int:nc_id>/action", methods=["POST"])
@jwt_required()
def submit_corrective_action(nc_id):
    """
    Submit corrective action (by contractor)
    Body: proposed_action, action_photos (optional)
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if not data.get("proposed_action"):
        return jsonify({"success": False, "message": "Proposed action is required"}), 400
    
    with session_scope() as session:
        nc = session.query(NonConformance).filter_by(
            id=nc_id,
            company_id=current_user.company_id
        ).first()
        
        if not nc:
            return jsonify({"success": False, "message": "NC not found"}), 404
        
        # Update NC with proposed action
        nc.proposed_action = data["proposed_action"]
        nc.action_photos = data.get("action_photos")
        nc.action_taken = data.get("action_taken")
        nc.action_completion_date = datetime.utcnow()
        nc.verification_status = "action_submitted"
        
        session.commit()
        
        logger.info(f"Corrective action submitted for NC {nc.nc_number} by user {current_user.id}")
        
        return jsonify({
            "success": True,
            "message": "Corrective action submitted for verification",
            "nc": nc.to_dict()
        }), 200


@nc_bp.route("/<int:nc_id>/verify", methods=["POST"])
@jwt_required()
def verify_nc(nc_id):
    """
    Verify/Reject NC closure (by safety officer)
    Body: approved (bool), verification_notes, closure_remarks (optional)
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if "approved" not in data:
        return jsonify({"success": False, "message": "Approval status is required"}), 400
    
    with session_scope() as session:
        nc = session.query(NonConformance).filter_by(
            id=nc_id,
            company_id=current_user.company_id
        ).first()
        
        if not nc:
            return jsonify({"success": False, "message": "NC not found"}), 404
        
        nc.verification_notes = data.get("verification_notes")
        nc.verified_by = current_user.id
        nc.verified_at = datetime.utcnow()
        
        if data["approved"]:
            # Approve and close NC
            nc.verification_status = "verified"
            nc.is_closed = True
            nc.closed_by = current_user.id
            nc.closed_at = datetime.utcnow()
            nc.closure_remarks = data.get("closure_remarks")
            
            # Send approval notification
            send_nc_notification(nc, "nc_approved", session)
            
            message = f"NC {nc.nc_number} verified and closed"
        else:
            # Reject and send back to contractor
            nc.verification_status = "rejected"
            nc.is_closed = False
            
            # Send rejection notification
            send_nc_notification(nc, "nc_rejected", session)
            
            message = f"NC {nc.nc_number} rejected. Contractor notified."
        
        session.commit()
        
        logger.info(f"NC {nc.nc_number} {'approved' if data['approved'] else 'rejected'} by user {current_user.id}")
        
        return jsonify({
            "success": True,
            "message": message,
            "nc": nc.to_dict()
        }), 200


@nc_bp.route("/<int:nc_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(nc_id):
    """
    Add comment to NC (discussion between safety officer and contractor)
    Body: comment_text, attachments (optional)
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if not data.get("comment_text"):
        return jsonify({"success": False, "message": "Comment text is required"}), 400
    
    with session_scope() as session:
        nc = session.query(NonConformance).filter_by(
            id=nc_id,
            company_id=current_user.company_id
        ).first()
        
        if not nc:
            return jsonify({"success": False, "message": "NC not found"}), 404
        
        comment = NCComment(
            nc_id=nc_id,
            comment_text=data["comment_text"],
            attachments=data.get("attachments"),
            created_by=current_user.id
        )
        session.add(comment)
        session.commit()
        
        return jsonify({
            "success": True,
            "message": "Comment added",
            "comment": comment.to_dict()
        }), 201


@nc_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def nc_dashboard():
    """
    Get NC dashboard for contractors
    Shows: pending NCs, overdue NCs, closed NCs count
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        # Base query
        if current_user.role == "contractor":
            query = session.query(NonConformance).filter_by(
                company_id=current_user.company_id,
                assigned_to_user=current_user.id
            )
        else:
            query = session.query(NonConformance).filter_by(
                company_id=current_user.company_id
            )
        
        # Count by status
        pending = query.filter_by(is_closed=False, verification_status="pending_action").count()
        action_submitted = query.filter_by(verification_status="action_submitted").count()
        overdue = query.filter_by(is_overdue=True, is_closed=False).count()
        closed = query.filter_by(is_closed=True).count()
        rejected = query.filter_by(verification_status="rejected").count()
        
        # Get recent NCs
        recent_ncs = query.order_by(NonConformance.raised_at.desc()).limit(10).all()
        
        return jsonify({
            "success": True,
            "dashboard": {
                "pending_action": pending,
                "action_submitted": action_submitted,
                "overdue": overdue,
                "closed": closed,
                "rejected": rejected,
                "recent_ncs": [nc.to_dict() for nc in recent_ncs]
            }
        }), 200


@nc_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Get all notifications for current user/contractor"""
    current_user = get_current_user()
    
    with session_scope() as session:
        query = session.query(ContractorNotification).filter_by(
            company_id=current_user.company_id,
            recipient_user=current_user.id
        ).order_by(ContractorNotification.sent_at.desc()).limit(50)
        
        notifications = query.all()
        
        return jsonify({
            "success": True,
            "notifications": [n.to_dict() for n in notifications]
        }), 200


@nc_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    current_user = get_current_user()
    
    with session_scope() as session:
        notification = session.query(ContractorNotification).filter_by(
            id=notification_id,
            recipient_user=current_user.id
        ).first()
        
        if not notification:
            return jsonify({"success": False, "message": "Notification not found"}), 404
        
        notification.delivery_status = "read"
        notification.read_at = datetime.utcnow()
        session.commit()
        
        return jsonify({"success": True, "message": "Notification marked as read"}), 200


# ============================================================================
# SCORING & REPORTING ENDPOINTS
# ============================================================================

@nc_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_nc_dashboard():
    """
    Get NC dashboard statistics with scoring.
    
    Query params:
    - project_id (optional): Filter by project
    - contractor (optional): Filter by contractor name
    """
    current_user = get_current_user()
    
    with session_scope() as session:
        project_id = request.args.get('project_id', type=int)
        contractor = request.args.get('contractor')
        
        # Base query
        query = session.query(NonConformance).filter_by(company_id=current_user.company_id)
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        if contractor:
            query = query.filter_by(assigned_to_contractor=contractor)
        
        # Status counts
        status_counts = {}
        for status in ['open', 'under_review', 'action_taken', 'verified', 'closed', 'rejected']:
            count = query.filter_by(nc_status=status).count()
            status_counts[status] = count
        
        # Severity counts
        severity_counts = {}
        for severity in ['critical', 'major', 'minor']:
            count = query.filter(func.lower(NonConformance.severity) == severity).count()
            severity_counts[severity] = count
        
        # Open issues (not closed)
        open_count = query.filter(NonConformance.nc_status != 'closed').count()
        
        # Overdue issues (past target date and not closed)
        now = datetime.utcnow()
        overdue_count = query.filter(
            and_(
                NonConformance.target_closure_date < now,
                NonConformance.nc_status != 'closed'
            )
        ).count()
        
        # Average resolution time for closed issues
        closed_issues = query.filter_by(nc_status='closed').all()
        avg_resolution_days = 0
        if closed_issues:
            total_days = sum([nc.actual_resolution_days or 0 for nc in closed_issues])
            avg_resolution_days = total_days / len(closed_issues) if total_days > 0 else 0
        
        # Calculate weighted score based on severity
        all_issues = query.all()
        total_count = len(all_issues)
        closed_count = len([nc for nc in all_issues if nc.nc_status == 'closed'])
        
        # Calculate total severity points
        # Critical=1.5, Major=1.0, Minor=0.5 (but map to High=1.0, Moderate=0.5, Low=0.25)
        severity_map = {'critical': 1.0, 'major': 0.5, 'minor': 0.25}
        
        total_severity_points = sum(
            severity_map.get(nc.severity.lower(), 0.5) for nc in all_issues
        )
        
        closed_severity_points = sum(
            severity_map.get(nc.severity.lower(), 0.5) 
            for nc in all_issues if nc.nc_status == 'closed'
        )
        
        # Score calculation: (closed severity points / total severity points) * 10
        score_out_of_10 = (closed_severity_points / total_severity_points * 10) if total_severity_points > 0 else 10.0
        
        # Count open issues by severity
        open_critical = len([nc for nc in all_issues if nc.severity.lower() == 'critical' and nc.nc_status != 'closed'])
        open_major = len([nc for nc in all_issues if nc.severity.lower() == 'major' and nc.nc_status != 'closed'])
        open_minor = len([nc for nc in all_issues if nc.severity.lower() == 'minor' and nc.nc_status != 'closed'])
        
        return jsonify({
            "status_counts": status_counts,
            "severity_counts": severity_counts,
            "open_by_severity": {
                "critical": open_critical,
                "major": open_major,
                "minor": open_minor
            },
            "total": total_count,
            "open": open_count,
            "closed": closed_count,
            "overdue": overdue_count,
            "avg_resolution_days": round(avg_resolution_days, 1),
            "score": round(score_out_of_10, 1),
            "total_severity_points": round(total_severity_points, 2),
            "closed_severity_points": round(closed_severity_points, 2),
            "performance_grade": calculate_performance_grade(score_out_of_10)
        }), 200


@nc_bp.route("/reports/<report_type>", methods=["GET"])
@jwt_required()
def generate_nc_report(report_type):
    """
    Generate contractor performance report.
    
    report_type: 'monthly' or 'weekly'
    
    Query params:
    - project_id (required): Project to report on
    - contractor (required): Contractor name
    - period (optional): Period in YYYY-MM or YYYY-Wnn format
    """
    current_user = get_current_user()
    
    if report_type not in ['monthly', 'weekly']:
        return jsonify({"error": "Invalid report_type. Use 'monthly' or 'weekly'"}), 400
    
    project_id = request.args.get('project_id', type=int)
    contractor = request.args.get('contractor')
    
    if not project_id or not contractor:
        return jsonify({"error": "project_id and contractor are required"}), 400
    
    # Determine period
    if report_type == 'monthly':
        period = request.args.get('period', datetime.utcnow().strftime('%Y-%m'))
        period_filter = NonConformance.score_month == period
    else:  # weekly
        period = request.args.get('period', datetime.utcnow().strftime('%Y-W%U'))
        period_filter = NonConformance.score_week == period
    
    with session_scope() as session:
        # Get all NCs for this contractor and period
        issues = session.query(NonConformance).filter(
            and_(
                NonConformance.company_id == current_user.company_id,
                NonConformance.project_id == project_id,
                NonConformance.assigned_to_contractor == contractor,
                period_filter
            )
        ).all()
        
        # Calculate scores with severity weighting
        severity_map = {'critical': 1.0, 'major': 0.5, 'minor': 0.25}
        
        critical_count = sum(1 for nc in issues if nc.severity.lower() == 'critical' and nc.nc_status != 'closed')
        major_count = sum(1 for nc in issues if nc.severity.lower() == 'major' and nc.nc_status != 'closed')
        minor_count = sum(1 for nc in issues if nc.severity.lower() == 'minor' and nc.nc_status != 'closed')
        
        closed_count = sum(1 for nc in issues if nc.nc_status == 'closed')
        total_count = len(issues)
        open_count = total_count - closed_count
        
        # Calculate weighted score
        total_severity_points = sum(severity_map.get(nc.severity.lower(), 0.5) for nc in issues)
        closed_severity_points = sum(
            severity_map.get(nc.severity.lower(), 0.5) 
            for nc in issues if nc.nc_status == 'closed'
        )
        
        total_score = (closed_severity_points / total_severity_points * 10) if total_severity_points > 0 else 10.0
        
        # Calculate closure rate
        closure_rate = (closed_count / total_count * 100) if total_count > 0 else 0
        
        # Calculate avg resolution time
        closed_issues = [nc for nc in issues if nc.nc_status == 'closed' and nc.actual_resolution_days]
        avg_resolution_days = sum(nc.actual_resolution_days for nc in closed_issues) / len(closed_issues) if closed_issues else 0
        
        # Determine performance grade
        grade = calculate_performance_grade(total_score)
        
        # Check if report already exists
        from .safety_nc_models import SafetyNCScoreReport
        existing_report = session.query(SafetyNCScoreReport).filter(
            and_(
                SafetyNCScoreReport.company_id == current_user.company_id,
                SafetyNCScoreReport.project_id == project_id,
                SafetyNCScoreReport.contractor_name == contractor,
                SafetyNCScoreReport.report_type == report_type,
                SafetyNCScoreReport.period == period
            )
        ).first()
        
        if existing_report:
            # Update existing report
            existing_report.critical_count = critical_count
            existing_report.major_count = major_count
            existing_report.minor_count = minor_count
            existing_report.total_issues_count = total_count
            existing_report.closed_issues_count = closed_count
            existing_report.open_issues_count = open_count
            existing_report.total_score = total_score
            existing_report.closure_rate = closure_rate
            existing_report.avg_resolution_days = avg_resolution_days
            existing_report.performance_grade = grade
            existing_report.generated_at = datetime.utcnow()
            
            report = existing_report
        else:
            # Create new report
            report = SafetyNCScoreReport(
                company_id=current_user.company_id,
                project_id=project_id,
                contractor_name=contractor,
                report_type=report_type,
                period=period,
                critical_count=critical_count,
                major_count=major_count,
                minor_count=minor_count,
                total_issues_count=total_count,
                closed_issues_count=closed_count,
                open_issues_count=open_count,
                total_score=total_score,
                closure_rate=closure_rate,
                avg_resolution_days=avg_resolution_days,
                performance_grade=grade,
                generated_by_user_id=current_user.id,
                generated_at=datetime.utcnow()
            )
            session.add(report)
        
        session.flush()
        
        return jsonify({
            "report": report.to_dict(),
            "issues": [nc.to_dict() for nc in issues]
        }), 200


def calculate_performance_grade(score_out_of_10: float) -> str:
    """Calculate performance grade based on score out of 10.
    Higher score = better performance (more closures)
    """
    if score_out_of_10 >= 9.0:
        return 'A'
    elif score_out_of_10 >= 7.0:
        return 'B'
    elif score_out_of_10 >= 5.0:
        return 'C'
    elif score_out_of_10 >= 3.0:
        return 'D'
    else:
        return 'F'
