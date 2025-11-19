"""
Material Management API Blueprint

This module provides API endpoints for managing material categories and approved brands.
Implements ISO 9001:2015 Clause 8.4 (Control of externally provided processes).

Endpoints:
Material Categories:
- GET    /api/material-categories           - List all categories
- GET    /api/material-categories/:id       - Get category details
- POST   /api/material-categories           - Create category (QM only)
- PUT    /api/material-categories/:id       - Update category (QM only)
- DELETE /api/material-categories/:id       - Delete category (QM only)

Approved Brands:
- GET    /api/approved-brands               - List approved brands
- GET    /api/approved-brands/:id           - Get brand details
- GET    /api/approved-brands/:id/certificate - Get type test certificate
- POST   /api/approved-brands               - Create brand (QM only)
- PUT    /api/approved-brands/:id           - Update brand (QM only)
- PUT    /api/approved-brands/:id/approve   - Approve brand (QM only)
- DELETE /api/approved-brands/:id           - Soft delete brand (QM only)

All endpoints require JWT authentication and company-level access control.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps
from io import BytesIO
import traceback

try:
    from .db import session_scope
    from .models import MaterialCategory, ApprovedBrand, User
except ImportError:
    from db import session_scope
    from models import MaterialCategory, ApprovedBrand, User


# Create Blueprint
material_management_bp = Blueprint('material_management', __name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Extract user_id from JWT identity (converts string to int)."""
    return int(get_jwt_identity())





# ============================================================================
# DECORATORS
# ============================================================================

def company_access_required(f):
    """Decorator to check if user has access to the company."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        if request.method == 'GET':
            company_id = request.args.get('company_id', type=int)
        else:
            # Handle both JSON and form data
            if request.content_type and 'multipart/form-data' in request.content_type:
                company_id = int(request.form.get('company_id')) if request.form.get('company_id') else None
            else:
                data = request.get_json() if request.is_json else None
                company_id = data.get('company_id') if data else None
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        # Check if user belongs to this company
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user or user.company_id != company_id:
                return jsonify({"error": "Access denied. You don't belong to this company"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def quality_manager_required(f):
    """Decorator to check if user is a Quality Manager."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        
        with session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user or user.role != 'Quality Manager':
                return jsonify({"error": "Access denied. Only Quality Managers can perform this action"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# MATERIAL CATEGORY ENDPOINTS
# ============================================================================

@material_management_bp.route('/api/material-categories', methods=['GET'])
@jwt_required()
@company_access_required
def get_material_categories():
    """Get list of material categories for a company."""
    try:
        company_id = request.args.get('company_id', type=int)
        
        with session_scope() as session:
            categories = session.query(MaterialCategory).filter_by(
                company_id=company_id
            ).order_by(MaterialCategory.category_name).all()
            
            return jsonify({
                "success": True,
                "count": len(categories),
                "categories": [cat.to_dict() for cat in categories]
            }), 200
    
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch categories: {str(e)}"}), 500


@material_management_bp.route('/api/material-categories/<int:category_id>', methods=['GET'])
@jwt_required()
@company_access_required
def get_material_category(category_id):
    """Get details of a specific material category."""
    try:
        company_id = request.args.get('company_id', type=int)
        
        with session_scope() as session:
            category = session.query(MaterialCategory).filter_by(
                id=category_id,
                company_id=company_id
            ).first()
            
            if not category:
                return jsonify({"error": "Category not found"}), 404
            
            return jsonify({
                "success": True,
                "category": category.to_dict()
            }), 200
    
    except Exception as e:
        print(f"Error fetching category: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch category: {str(e)}"}), 500


@material_management_bp.route('/api/material-categories', methods=['POST'])
@jwt_required()
@quality_manager_required
@company_access_required
def create_material_category():
    """
    Create a new material category.
    Only Quality Managers can create categories.
    
    Request Body:
    {
        "company_id": int (required),
        "category_name": str (required, e.g., "Steel", "Glass"),
        "category_code": str (optional),
        "description": str (optional),
        "applicable_standards": str (optional, e.g., "IS 1786, IS 2062"),
        "requires_testing": bool (optional, default: true),
        "test_frequency": str (optional, e.g., "Per delivery", "Monthly")
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        if not data.get('category_name'):
            return jsonify({"error": "category_name is required"}), 400
        
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        with session_scope() as session:
            category = MaterialCategory(
                company_id=company_id,
                category_name=data['category_name'],
                category_code=data.get('category_code'),
                description=data.get('description'),
                applicable_standards=data.get('applicable_standards'),
                requires_testing=data.get('requires_testing', True),
                test_frequency=data.get('test_frequency'),
                created_by=user_id
            )
            
            session.add(category)
            session.flush()
            
            category_dict = category.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Material category created successfully",
            "category": category_dict
        }), 201
    
    except Exception as e:
        print(f"Error creating category: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create category: {str(e)}"}), 500


@material_management_bp.route('/api/material-categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@quality_manager_required
@company_access_required
def update_material_category(category_id):
    """Update material category details (QM only)."""
    try:
        data = request.get_json()
        company_id = data.get('company_id')
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        with session_scope() as session:
            category = session.query(MaterialCategory).filter_by(
                id=category_id,
                company_id=company_id
            ).first()
            
            if not category:
                return jsonify({"error": "Category not found"}), 404
            
            # Update fields
            if 'category_name' in data:
                category.category_name = data['category_name']
            if 'category_code' in data:
                category.category_code = data['category_code']
            if 'description' in data:
                category.description = data['description']
            if 'applicable_standards' in data:
                category.applicable_standards = data['applicable_standards']
            if 'requires_testing' in data:
                category.requires_testing = data['requires_testing']
            if 'test_frequency' in data:
                category.test_frequency = data['test_frequency']
            
            category.updated_at = datetime.utcnow()
            session.flush()
            
            category_dict = category.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Category updated successfully",
            "category": category_dict
        }), 200
    
    except Exception as e:
        print(f"Error updating category: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update category: {str(e)}"}), 500


@material_management_bp.route('/api/material-categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@quality_manager_required
@company_access_required
def delete_material_category(category_id):
    """Delete material category (QM only)."""
    try:
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        with session_scope() as session:
            category = session.query(MaterialCategory).filter_by(
                id=category_id,
                company_id=company_id
            ).first()
            
            if not category:
                return jsonify({"error": "Category not found"}), 404
            
            session.delete(category)
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Category deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting category: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete category: {str(e)}"}), 500


# ============================================================================
# APPROVED BRAND ENDPOINTS
# ============================================================================

@material_management_bp.route('/api/approved-brands', methods=['GET'])
@jwt_required()
@company_access_required
def get_approved_brands():
    """
    Get list of approved brands.
    
    Query Parameters:
    - company_id (required): Filter by company
    - category_id (optional): Filter by material category
    - approved_only (optional): If true, return only approved brands (default: true)
    """
    try:
        company_id = request.args.get('company_id', type=int)
        category_id = request.args.get('category_id', type=int)
        approved_only = request.args.get('approved_only', 'true').lower() == 'true'
        
        with session_scope() as session:
            query = session.query(ApprovedBrand).filter_by(
                company_id=company_id,
                is_active=True
            )
            
            if category_id:
                query = query.filter_by(material_category_id=category_id)
            
            if approved_only:
                query = query.filter_by(is_approved=True)
            
            brands = query.order_by(ApprovedBrand.brand_name).all()
            
            # Enrich with category name
            result = []
            for brand in brands:
                brand_dict = brand.to_dict()
                if brand.material_category_id:
                    category = session.query(MaterialCategory).filter_by(id=brand.material_category_id).first()
                    brand_dict['category_name'] = category.category_name if category else None
                result.append(brand_dict)
            
            return jsonify({
                "success": True,
                "count": len(result),
                "brands": result
            }), 200
    
    except Exception as e:
        print(f"Error fetching brands: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch brands: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands/<int:brand_id>', methods=['GET'])
@jwt_required()
@company_access_required
def get_approved_brand(brand_id):
    """Get details of a specific approved brand."""
    try:
        company_id = request.args.get('company_id', type=int)
        
        with session_scope() as session:
            brand = session.query(ApprovedBrand).filter_by(
                id=brand_id,
                company_id=company_id,
                is_active=True
            ).first()
            
            if not brand:
                return jsonify({"error": "Brand not found"}), 404
            
            brand_dict = brand.to_dict()
            
            # Add category name
            if brand.material_category_id:
                category = session.query(MaterialCategory).filter_by(id=brand.material_category_id).first()
                brand_dict['category_name'] = category.category_name if category else None
            
            # Add user names
            if brand.approved_by:
                approver = session.query(User).filter_by(id=brand.approved_by).first()
                brand_dict['approved_by_name'] = approver.full_name if approver else None
            
            return jsonify({
                "success": True,
                "brand": brand_dict
            }), 200
    
    except Exception as e:
        print(f"Error fetching brand: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch brand: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands/<int:brand_id>/certificate', methods=['GET'])
@jwt_required()
@company_access_required
def get_brand_certificate(brand_id):
    """Get brand's type test certificate."""
    try:
        company_id = request.args.get('company_id', type=int)
        
        with session_scope() as session:
            brand = session.query(ApprovedBrand).filter_by(
                id=brand_id,
                company_id=company_id,
                is_active=True
            ).first()
            
            if not brand:
                return jsonify({"error": "Brand not found"}), 404
            
            if not brand.type_test_certificate_data:
                return jsonify({"error": "No certificate available"}), 404
            
            return send_file(
                BytesIO(brand.type_test_certificate_data),
                mimetype=brand.type_test_certificate_mimetype or 'application/pdf',
                as_attachment=False,
                download_name=brand.type_test_certificate_name or f'certificate_{brand_id}.pdf'
            )
    
    except Exception as e:
        print(f"Error fetching certificate: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch certificate: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands', methods=['POST'])
@jwt_required()
@quality_manager_required
@company_access_required
def create_approved_brand():
    """
    Create a new approved brand.
    Only Quality Managers can create brands.
    
    Request: multipart/form-data
    - company_id (required): int
    - material_category_id (required): int
    - brand_name (required): string
    - manufacturer_name (optional): string
    - grade_specification (optional): string
    - compliance_standards (optional): string
    - type_test_certificate (optional): file upload
    """
    try:
        user_id = get_current_user_id()
        
        # Validate required fields
        if not request.form.get('brand_name'):
            return jsonify({"error": "brand_name is required"}), 400
        
        company_id = int(request.form['company_id'])
        material_category_id = int(request.form['material_category_id'])
        brand_name = request.form['brand_name']
        manufacturer_name = request.form.get('manufacturer_name')
        grade_specification = request.form.get('grade_specification')
        compliance_standards = request.form.get('compliance_standards')
        
        # Handle certificate upload
        cert_name = None
        cert_data = None
        cert_mimetype = None
        
        if 'type_test_certificate' in request.files:
            cert_file = request.files['type_test_certificate']
            if cert_file.filename != '':
                cert_data = cert_file.read()
                if len(cert_data) > 10 * 1024 * 1024:
                    return jsonify({"error": "Certificate exceeds 10MB limit"}), 400
                cert_name = cert_file.filename
                cert_mimetype = cert_file.mimetype or 'application/pdf'
        
        with session_scope() as session:
            # Validate category exists
            category = session.query(MaterialCategory).filter_by(
                id=material_category_id,
                company_id=company_id
            ).first()
            if not category:
                return jsonify({"error": "Material category not found"}), 404
            
            # Create brand
            brand = ApprovedBrand(
                company_id=company_id,
                material_category_id=material_category_id,
                brand_name=brand_name,
                manufacturer_name=manufacturer_name,
                grade_specification=grade_specification,
                compliance_standards=compliance_standards,
                type_test_certificate_name=cert_name,
                type_test_certificate_data=cert_data,
                type_test_certificate_mimetype=cert_mimetype,
                is_approved=False,  # Requires approval
                created_by=user_id
            )
            
            session.add(brand)
            session.flush()
            
            brand_dict = brand.to_dict()
            brand_dict['category_name'] = category.category_name
        
        return jsonify({
            "success": True,
            "message": "Brand created successfully. Pending approval.",
            "brand": brand_dict
        }), 201
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating brand: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to create brand: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands/<int:brand_id>', methods=['PUT'])
@jwt_required()
@quality_manager_required
@company_access_required
def update_approved_brand(brand_id):
    """Update approved brand details (QM only)."""
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            company_id = int(request.form.get('company_id'))
            data = request.form
        else:
            data = request.get_json()
            company_id = data.get('company_id')
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        with session_scope() as session:
            brand = session.query(ApprovedBrand).filter_by(
                id=brand_id,
                company_id=company_id,
                is_active=True
            ).first()
            
            if not brand:
                return jsonify({"error": "Brand not found"}), 404
            
            # Update fields
            if 'brand_name' in data:
                brand.brand_name = data['brand_name']
            if 'manufacturer_name' in data:
                brand.manufacturer_name = data['manufacturer_name']
            if 'grade_specification' in data:
                brand.grade_specification = data['grade_specification']
            if 'compliance_standards' in data:
                brand.compliance_standards = data['compliance_standards']
            
            # Update certificate if provided
            if 'type_test_certificate' in request.files:
                cert_file = request.files['type_test_certificate']
                if cert_file.filename != '':
                    cert_data = cert_file.read()
                    if len(cert_data) > 10 * 1024 * 1024:
                        return jsonify({"error": "Certificate exceeds 10MB limit"}), 400
                    
                    brand.type_test_certificate_name = cert_file.filename
                    brand.type_test_certificate_data = cert_data
                    brand.type_test_certificate_mimetype = cert_file.mimetype or 'application/pdf'
            
            brand.updated_at = datetime.utcnow()
            session.flush()
            
            brand_dict = brand.to_dict()
        
        return jsonify({
            "success": True,
            "message": "Brand updated successfully",
            "brand": brand_dict
        }), 200
    
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error updating brand: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to update brand: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands/<int:brand_id>/approve', methods=['PUT'])
@jwt_required()
@quality_manager_required
@company_access_required
def approve_brand(brand_id):
    """
    Approve or reject a brand.
    Only Quality Managers can approve brands.
    
    Request Body:
    {
        "company_id": int (required),
        "approved": bool (required),
        "approval_validity": str (ISO date, optional - when approval expires),
        "remarks": str (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        if 'approved' not in data:
            return jsonify({"error": "approved field is required"}), 400
        
        approved = data['approved']
        remarks = data.get('remarks', '')
        
        # Parse approval validity
        approval_validity = None
        if data.get('approval_validity'):
            try:
                approval_validity = datetime.fromisoformat(data['approval_validity'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid approval_validity format"}), 400
        
        with session_scope() as session:
            brand = session.query(ApprovedBrand).filter_by(
                id=brand_id,
                company_id=company_id,
                is_active=True
            ).first()
            
            if not brand:
                return jsonify({"error": "Brand not found"}), 404
            
            brand.is_approved = approved
            brand.approved_by = user_id
            brand.approved_at = datetime.utcnow()
            brand.approval_validity = approval_validity
            brand.approval_remarks = remarks
            brand.updated_at = datetime.utcnow()
            
            session.flush()
            brand_dict = brand.to_dict()
        
        status_text = "approved" if approved else "rejected"
        return jsonify({
            "success": True,
            "message": f"Brand {status_text} successfully",
            "brand": brand_dict
        }), 200
    
    except Exception as e:
        print(f"Error approving brand: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to approve brand: {str(e)}"}), 500


@material_management_bp.route('/api/approved-brands/<int:brand_id>', methods=['DELETE'])
@jwt_required()
@quality_manager_required
@company_access_required
def delete_approved_brand(brand_id):
    """Soft delete approved brand (QM only)."""
    try:
        user_id = get_current_user_id()
        company_id = request.args.get('company_id', type=int)
        
        if not company_id:
            return jsonify({"error": "company_id is required"}), 400
        
        with session_scope() as session:
            brand = session.query(ApprovedBrand).filter_by(
                id=brand_id,
                company_id=company_id,
                is_active=True
            ).first()
            
            if not brand:
                return jsonify({"error": "Brand not found"}), 404
            
            brand.is_deleted = True
            brand.deleted_at = datetime.utcnow()
            brand.deleted_by = user_id
            
            session.flush()
        
        return jsonify({
            "success": True,
            "message": "Brand deleted successfully"
        }), 200
    
    except Exception as e:
        print(f"Error deleting brand: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete brand: {str(e)}"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@material_management_bp.route('/api/material-management/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Material Management API",
        "version": "1.0.0",
        "compliance": "ISO 9001:2015 Clause 8.4"
    }), 200
