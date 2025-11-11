"""
Support Admin API - Exclusive endpoints for support administrators.
Manage companies, set project limits, view global analytics.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import logging

from .db import session_scope
from .models import User, Company, Project, ProjectMembership, BatchRegister, CubeTestRegister
from .auth import require_support_admin

logger = logging.getLogger(__name__)

support_bp = Blueprint("support", __name__, url_prefix="/api/support")


# ============================================================================
# Dashboard Overview
# ============================================================================

@support_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@require_support_admin
def get_dashboard_overview():
    """
    Get overview statistics for support admin dashboard.
    Returns: total companies, projects, revenue, recent activity.
    """
    try:
        with session_scope() as session:
            # Total companies
            total_companies = session.query(func.count(Company.id)).scalar() or 0
            active_companies = session.query(func.count(Company.id)).filter(
                Company.is_active == 1,
                Company.billing_status == "active"
            ).scalar() or 0
            
            # Total projects
            total_projects = session.query(func.count(Project.id)).scalar() or 0
            active_projects = session.query(func.count(Project.id)).filter(
                Project.is_active == 1
            ).scalar() or 0
            
            # Calculate monthly revenue
            companies_list = session.query(Company).filter(
                Company.is_active == 1,
                Company.billing_status == "active"
            ).all()
            
            monthly_revenue = 0
            for company in companies_list:
                # Count active projects for this company
                active_count = session.query(func.count(Project.id)).filter(
                    Project.company_id == company.id,
                    Project.is_active == 1
                ).scalar() or 0
                monthly_revenue += active_count * company.price_per_project
            
            # Recent signups (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_companies = session.query(func.count(Company.id)).filter(
                Company.created_at >= thirty_days_ago
            ).scalar() or 0
            
            # Suspended companies
            suspended_companies = session.query(func.count(Company.id)).filter(
                Company.billing_status == "suspended"
            ).scalar() or 0
            
            # Top 5 companies by revenue
            top_companies = []
            for company in companies_list:
                active_count = session.query(func.count(Project.id)).filter(
                    Project.company_id == company.id,
                    Project.is_active == 1
                ).scalar() or 0
                revenue = active_count * company.price_per_project
                if revenue > 0:
                    top_companies.append({
                        "id": company.id,
                        "name": company.name,
                        "activeProjects": active_count,
                        "monthlyRevenue": revenue
                    })
            
            top_companies.sort(key=lambda x: x["monthlyRevenue"], reverse=True)
            top_companies = top_companies[:5]
            
            return jsonify({
                "success": True,
                "data": {
                    "totalCompanies": total_companies,
                    "activeCompanies": active_companies,
                    "suspendedCompanies": suspended_companies,
                    "totalProjects": total_projects,
                    "activeProjects": active_projects,
                    "monthlyRevenue": monthly_revenue,
                    "newSignupsThisMonth": new_companies,
                    "topCompanies": top_companies
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Company Management
# ============================================================================

@support_bp.route("/companies", methods=["GET"])
@jwt_required()
@require_support_admin
def get_all_companies():
    """
    Get all companies with their project counts and billing info.
    Query params: page, limit, search, status
    """
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 50, type=int)
        search = request.args.get("search", "", type=str)
        status_filter = request.args.get("status", "", type=str)  # active, suspended, cancelled
        
        with session_scope() as session:
            query = session.query(Company)
            
            # Apply search filter
            if search:
                query = query.filter(
                    Company.name.ilike(f"%{search}%") |
                    Company.company_email.ilike(f"%{search}%")
                )
            
            # Apply status filter
            if status_filter:
                query = query.filter(Company.billing_status == status_filter)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            companies = query.order_by(Company.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
            
            # Format response with project counts
            result = []
            for company in companies:
                active_projects = session.query(func.count(Project.id)).filter(
                    Project.company_id == company.id,
                    Project.is_active == 1
                ).scalar() or 0
                
                total_projects = session.query(func.count(Project.id)).filter(
                    Project.company_id == company.id
                ).scalar() or 0
                
                company_data = company.to_dict()
                company_data["activeProjects"] = active_projects
                company_data["totalProjects"] = total_projects
                company_data["monthlyRevenue"] = active_projects * company.price_per_project
                result.append(company_data)
            
            return jsonify({
                "success": True,
                "data": result,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@support_bp.route("/companies", methods=["POST"])
@jwt_required()
@require_support_admin
def create_company():
    """
    Create a new company with subscription settings.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        with session_scope() as session:
            # Check if company already exists
            existing = session.query(Company).filter(Company.name == data["name"]).first()
            if existing:
                return jsonify({"success": False, "error": "Company with this name already exists"}), 400
            
            # Create company
            company = Company(
                name=data["name"],
                subscription_plan=data.get("subscriptionPlan", "trial"),
                active_projects_limit=data.get("activeProjectsLimit", 1),
                price_per_project=data.get("pricePerProject", 5000.0),
                billing_status=data.get("billingStatus", "active"),
                company_email=data.get("companyEmail"),
                company_phone=data.get("companyPhone"),
                company_address=data.get("companyAddress"),
                gstin=data.get("gstin"),
                is_active=1
            )
            
            # Set subscription dates if provided
            if data.get("subscriptionStartDate"):
                company.subscription_start_date = datetime.fromisoformat(data["subscriptionStartDate"].replace("Z", "+00:00"))
            else:
                company.subscription_start_date = datetime.utcnow()
            
            if data.get("subscriptionEndDate"):
                company.subscription_end_date = datetime.fromisoformat(data["subscriptionEndDate"].replace("Z", "+00:00"))
            
            session.add(company)
            session.flush()
            
            logger.info(f"Company created: {company.name} (ID: {company.id})")
            
            return jsonify({
                "success": True,
                "message": "Company created successfully",
                "data": company.to_dict()
            }), 201
            
    except IntegrityError as e:
        logger.error(f"IntegrityError creating company: {str(e)}")
        return jsonify({"success": False, "error": "Company with this name already exists"}), 400
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@support_bp.route("/companies/<int:company_id>", methods=["PUT"])
@jwt_required()
@require_support_admin
def update_company(company_id):
    """
    Update company settings (limits, pricing, status).
    """
    try:
        data = request.get_json()
        
        with session_scope() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                return jsonify({"success": False, "error": "Company not found"}), 404
            
            # Update fields
            if "name" in data:
                company.name = data["name"]
            if "subscriptionPlan" in data:
                company.subscription_plan = data["subscriptionPlan"]
            if "activeProjectsLimit" in data:
                company.active_projects_limit = data["activeProjectsLimit"]
            if "pricePerProject" in data:
                company.price_per_project = data["pricePerProject"]
            if "billingStatus" in data:
                company.billing_status = data["billingStatus"]
            if "companyEmail" in data:
                company.company_email = data["companyEmail"]
            if "companyPhone" in data:
                company.company_phone = data["companyPhone"]
            if "companyAddress" in data:
                company.company_address = data["companyAddress"]
            if "gstin" in data:
                company.gstin = data["gstin"]
            if "isActive" in data:
                company.is_active = 1 if data["isActive"] else 0
            
            if "subscriptionStartDate" in data and data["subscriptionStartDate"]:
                company.subscription_start_date = datetime.fromisoformat(data["subscriptionStartDate"].replace("Z", "+00:00"))
            if "subscriptionEndDate" in data and data["subscriptionEndDate"]:
                company.subscription_end_date = datetime.fromisoformat(data["subscriptionEndDate"].replace("Z", "+00:00"))
            
            company.updated_at = datetime.utcnow()
            
            logger.info(f"Company updated: {company.name} (ID: {company.id})")
            
            return jsonify({
                "success": True,
                "message": "Company updated successfully",
                "data": company.to_dict()
            }), 200
            
    except IntegrityError as e:
        logger.error(f"IntegrityError updating company: {str(e)}")
        return jsonify({"success": False, "error": "Company name must be unique"}), 400
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@support_bp.route("/companies/<int:company_id>", methods=["GET"])
@jwt_required()
@require_support_admin
def get_company_details(company_id):
    """
    Get detailed information about a company including projects and users.
    """
    try:
        with session_scope() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                return jsonify({"success": False, "error": "Company not found"}), 404
            
            # Get projects
            projects = session.query(Project).filter(Project.company_id == company_id).all()
            active_projects_count = sum(1 for p in projects if p.is_active)
            
            # Get users
            users = session.query(User).filter(User.company_id == company_id).all()
            company_admins = [u for u in users if u.is_company_admin]
            
            # Get statistics
            total_batches = session.query(func.count(BatchRegister.id)).join(
                Project, BatchRegister.project_id == Project.id
            ).filter(Project.company_id == company_id).scalar() or 0
            
            total_tests = session.query(func.count(CubeTestRegister.id)).join(
                Project, CubeTestRegister.project_id == Project.id
            ).filter(Project.company_id == company_id).scalar() or 0
            
            result = company.to_dict()
            result["projects"] = [p.to_dict() for p in projects]
            result["activeProjectsCount"] = active_projects_count
            result["users"] = [u.to_dict() for u in users]
            result["companyAdmins"] = [u.to_dict() for u in company_admins]
            result["statistics"] = {
                "totalBatches": total_batches,
                "totalTests": total_tests,
                "totalUsers": len(users)
            }
            result["monthlyRevenue"] = active_projects_count * company.price_per_project
            
            return jsonify({
                "success": True,
                "data": result
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting company details: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@support_bp.route("/companies/<int:company_id>", methods=["DELETE"])
@jwt_required()
@require_support_admin
def delete_company(company_id):
    """
    Soft delete a company (set is_active = 0).
    """
    try:
        with session_scope() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                return jsonify({"success": False, "error": "Company not found"}), 404
            
            company.is_active = 0
            company.billing_status = "cancelled"
            company.updated_at = datetime.utcnow()
            
            logger.info(f"Company deleted: {company.name} (ID: {company.id})")
            
            return jsonify({
                "success": True,
                "message": "Company deleted successfully"
            }), 200
            
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# User Management (Company Admins)
# ============================================================================

@support_bp.route("/companies/<int:company_id>/admins", methods=["POST"])
@jwt_required()
@require_support_admin
def assign_company_admin(company_id):
    """
    Assign or invite a user as company admin.
    """
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        with session_scope() as session:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                return jsonify({"success": False, "error": "Company not found"}), 404
            
            # Check if user exists
            user = session.query(User).filter(User.email == email).first()
            
            if user:
                # Update existing user
                user.company_id = company_id
                user.is_company_admin = 1
                user.updated_at = datetime.utcnow()
                message = f"User {email} assigned as company admin"
            else:
                # Create invitation (in real implementation, send email)
                message = f"Invitation sent to {email} to join as company admin"
                # For now, return instructions
                return jsonify({
                    "success": True,
                    "message": message,
                    "data": {
                        "email": email,
                        "companyId": company_id,
                        "companyName": company.name,
                        "role": "Company Admin",
                        "instructions": "User needs to register with this email to get admin access"
                    }
                }), 200
            
            logger.info(message)
            
            return jsonify({
                "success": True,
                "message": message,
                "data": user.to_dict()
            }), 200
            
    except Exception as e:
        logger.error(f"Error assigning company admin: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Analytics
# ============================================================================

@support_bp.route("/analytics/revenue", methods=["GET"])
@jwt_required()
@require_support_admin
def get_revenue_analytics():
    """
    Get revenue analytics (monthly breakdown, trends).
    """
    try:
        with session_scope() as session:
            companies = session.query(Company).filter(
                Company.is_active == 1,
                Company.billing_status == "active"
            ).all()
            
            revenue_by_plan = {}
            for company in companies:
                plan = company.subscription_plan
                active_count = session.query(func.count(Project.id)).filter(
                    Project.company_id == company.id,
                    Project.is_active == 1
                ).scalar() or 0
                
                revenue = active_count * company.price_per_project
                
                if plan not in revenue_by_plan:
                    revenue_by_plan[plan] = {"companies": 0, "projects": 0, "revenue": 0}
                
                revenue_by_plan[plan]["companies"] += 1
                revenue_by_plan[plan]["projects"] += active_count
                revenue_by_plan[plan]["revenue"] += revenue
            
            return jsonify({
                "success": True,
                "data": {
                    "revenueByPlan": revenue_by_plan,
                    "totalRevenue": sum(p["revenue"] for p in revenue_by_plan.values()),
                    "totalCompanies": sum(p["companies"] for p in revenue_by_plan.values()),
                    "totalProjects": sum(p["projects"] for p in revenue_by_plan.values())
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
