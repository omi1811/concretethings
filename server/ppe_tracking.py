"""
PPE Tracking API
Endpoints for PPE issuance, return, damage reporting, and inventory management
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract
from server.db import db
from server.models import User, Company, Project
from server.safety_models import Worker
from server.ppe_tracking_models import PPEIssuance, PPEInventory, PPEType, IssuanceStatus, PPECondition, get_ppe_expiry_date, PPE_LIFESPAN_DAYS
from flask_jwt_extended import jwt_required, get_jwt_identity

ppe_bp = Blueprint('ppe_tracking', __name__)

def get_current_user_id():
    """Extract user ID from JWT token"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('id')
    return identity

def generate_issuance_number(project_id):
    """Generate unique issuance number: PPE-{project_id}-{year}-{seq}"""
    year = datetime.now().year
    existing = PPEIssuance.query.filter(
        PPEIssuance.project_id == project_id,
        extract('year', PPEIssuance.issue_date) == year,
        PPEIssuance.is_deleted == False
    ).count()
    seq = existing + 1
    return f"PPE-{project_id}-{year}-{seq:05d}"

# ========================================
# 1. ISSUE PPE TO WORKER
# ========================================

@ppe_bp.route('/api/ppe/issue', methods=['POST'])
@jwt_required()
def issue_ppe():
    """
    Issue PPE to worker
    Body: {
        project_id, worker_id, ppe_type, ppe_description,
        ppe_brand, ppe_model, ppe_size, serial_number,
        issue_date, expected_return_date (optional),
        isi_marked, ce_marked, ansi_compliant,
        unit_cost, issue_remarks
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        required = ['project_id', 'worker_id', 'ppe_type', 'ppe_description']
        if not all(field in data for field in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400
        
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        worker = Worker.query.get(data['worker_id'])
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        
        # Parse dates
        issue_date_obj = datetime.fromisoformat(data.get('issue_date', datetime.now().isoformat())).date()
        ppe_type_enum = PPEType[data['ppe_type']]
        
        # Calculate expiry date
        expiry_date = get_ppe_expiry_date(ppe_type_enum, issue_date_obj)
        
        # Generate issuance number
        issuance_number = generate_issuance_number(data['project_id'])
        
        # Create issuance record
        issuance = PPEIssuance(
            company_id=project.company_id,
            project_id=data['project_id'],
            issuance_number=issuance_number,
            worker_id=data['worker_id'],
            ppe_type=ppe_type_enum,
            ppe_description=data['ppe_description'],
            ppe_brand=data.get('ppe_brand'),
            ppe_model=data.get('ppe_model'),
            ppe_size=data.get('ppe_size'),
            serial_number=data.get('serial_number'),
            barcode=data.get('barcode'),
            issue_date=issue_date_obj,
            issued_by_id=user_id,
            issue_remarks=data.get('issue_remarks'),
            expected_return_date=datetime.fromisoformat(data['expected_return_date']).date() if data.get('expected_return_date') else None,
            expiry_date=expiry_date,
            isi_marked=data.get('isi_marked', False),
            ce_marked=data.get('ce_marked', False),
            ansi_compliant=data.get('ansi_compliant', False),
            test_certificate_url=data.get('test_certificate_url'),
            unit_cost=data.get('unit_cost', 0),
            status=IssuanceStatus.ISSUED,
            created_by=user_id
        )
        
        db.session.add(issuance)
        
        # Update inventory (decrease available stock)
        inventory = PPEInventory.query.filter_by(
            project_id=data['project_id'],
            ppe_type=ppe_type_enum,
            ppe_description=data['ppe_description'],
            ppe_size=data.get('ppe_size'),
            is_deleted=False
        ).first()
        
        if inventory:
            inventory.issued_quantity += 1
            inventory.update_stock_levels()
            inventory.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'PPE issued successfully',
            'issuance': issuance.to_dict(),
            'issuance_number': issuance_number,
            'expiry_date': expiry_date.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 2. RETURN PPE
# ========================================

@ppe_bp.route('/api/ppe/return/<int:issuance_id>', methods=['POST'])
@jwt_required()
def return_ppe(issuance_id):
    """
    Return PPE
    Body: {
        return_date, return_condition: "NEW|GOOD|FAIR|DAMAGED|EXPIRED",
        return_remarks
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        issuance = PPEIssuance.query.get(issuance_id)
        if not issuance or issuance.is_deleted:
            return jsonify({'error': 'Issuance record not found'}), 404
        
        if issuance.status != IssuanceStatus.ISSUED:
            return jsonify({'error': f'PPE already returned/damaged/lost. Current status: {issuance.status.value}'}), 400
        
        # Update issuance
        issuance.return_date = datetime.fromisoformat(data.get('return_date', datetime.now().isoformat())).date()
        issuance.returned_to_id = user_id
        issuance.return_condition = PPECondition[data.get('return_condition', 'GOOD')]
        issuance.return_remarks = data.get('return_remarks')
        issuance.status = IssuanceStatus.RETURNED
        issuance.updated_by = user_id
        
        # Update inventory (increase available stock if condition is good)
        if issuance.return_condition in [PPECondition.NEW, PPECondition.GOOD]:
            inventory = PPEInventory.query.filter_by(
                project_id=issuance.project_id,
                ppe_type=issuance.ppe_type,
                ppe_description=issuance.ppe_description,
                ppe_size=issuance.ppe_size,
                is_deleted=False
            ).first()
            
            if inventory:
                inventory.issued_quantity = max(0, inventory.issued_quantity - 1)
                inventory.update_stock_levels()
                inventory.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'PPE returned successfully',
            'issuance': issuance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 3. REPORT DAMAGE
# ========================================

@ppe_bp.route('/api/ppe/damage/<int:issuance_id>', methods=['POST'])
@jwt_required()
def report_damage(issuance_id):
    """
    Report PPE damage
    Body: {
        damage_description, damage_photos: [{url, description}],
        replacement_required: true/false
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        issuance = PPEIssuance.query.get(issuance_id)
        if not issuance or issuance.is_deleted:
            return jsonify({'error': 'Issuance record not found'}), 404
        
        # Update damage details
        issuance.damage_reported_date = date.today()
        issuance.damage_description = data.get('damage_description')
        issuance.damage_photos = data.get('damage_photos', [])
        issuance.replacement_required = data.get('replacement_required', False)
        issuance.status = IssuanceStatus.DAMAGED
        issuance.updated_by = user_id
        
        # Update inventory (decrease issued if still with worker)
        if issuance.return_date is None:
            inventory = PPEInventory.query.filter_by(
                project_id=issuance.project_id,
                ppe_type=issuance.ppe_type,
                ppe_description=issuance.ppe_description,
                ppe_size=issuance.ppe_size,
                is_deleted=False
            ).first()
            
            if inventory:
                inventory.issued_quantity = max(0, inventory.issued_quantity - 1)
                inventory.update_stock_levels()
                inventory.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Damage reported successfully',
            'issuance': issuance.to_dict(),
            'replacement_required': issuance.replacement_required
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 4. REPORT LOSS
# ========================================

@ppe_bp.route('/api/ppe/loss/<int:issuance_id>', methods=['POST'])
@jwt_required()
def report_loss(issuance_id):
    """
    Report PPE loss
    Body: {
        loss_remarks, penalty_amount (optional)
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        issuance = PPEIssuance.query.get(issuance_id)
        if not issuance or issuance.is_deleted:
            return jsonify({'error': 'Issuance record not found'}), 404
        
        # Update loss details
        issuance.loss_reported_date = date.today()
        issuance.loss_remarks = data.get('loss_remarks')
        issuance.penalty_amount = data.get('penalty_amount', 0)
        issuance.status = IssuanceStatus.LOST
        issuance.updated_by = user_id
        
        # Update inventory (decrease issued)
        inventory = PPEInventory.query.filter_by(
            project_id=issuance.project_id,
            ppe_type=issuance.ppe_type,
            ppe_description=issuance.ppe_description,
            ppe_size=issuance.ppe_size,
            is_deleted=False
        ).first()
        
        if inventory:
            inventory.issued_quantity = max(0, inventory.issued_quantity - 1)
            inventory.total_stock = max(0, inventory.total_stock - 1)
            inventory.update_stock_levels()
            inventory.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Loss reported successfully',
            'issuance': issuance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 5. LIST ISSUANCES
# ========================================

@ppe_bp.route('/api/ppe/issuances', methods=['GET'])
@jwt_required()
def list_issuances():
    """
    List PPE issuances with filters
    Query params: project_id, worker_id, ppe_type, status, expiring_soon
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = PPEIssuance.query.filter(
            PPEIssuance.company_id == user.company_id,
            PPEIssuance.is_deleted == False
        )
        
        if request.args.get('project_id'):
            query = query.filter(PPEIssuance.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('worker_id'):
            query = query.filter(PPEIssuance.worker_id == request.args.get('worker_id', type=int))
        
        if request.args.get('ppe_type'):
            query = query.filter(PPEIssuance.ppe_type == PPEType[request.args.get('ppe_type')])
        
        if request.args.get('status'):
            query = query.filter(PPEIssuance.status == IssuanceStatus[request.args.get('status')])
        
        if request.args.get('expiring_soon') == 'true':
            expiry_threshold = date.today() + timedelta(days=30)
            query = query.filter(
                PPEIssuance.expiry_date <= expiry_threshold,
                PPEIssuance.status == IssuanceStatus.ISSUED
            )
        
        query = query.order_by(PPEIssuance.issue_date.desc())
        issuances = query.all()
        
        return jsonify({
            'issuances': [i.to_dict() for i in issuances],
            'count': len(issuances)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 6. GET WORKER PPE HISTORY
# ========================================

@ppe_bp.route('/api/ppe/worker/<int:worker_id>', methods=['GET'])
@jwt_required()
def get_worker_ppe_history(worker_id):
    """Get complete PPE issuance history for a worker"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        worker = Worker.query.get(worker_id)
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        
        issuances = PPEIssuance.query.filter(
            PPEIssuance.worker_id == worker_id,
            PPEIssuance.company_id == user.company_id,
            PPEIssuance.is_deleted == False
        ).order_by(PPEIssuance.issue_date.desc()).all()
        
        # Currently issued items
        current = [i for i in issuances if i.status == IssuanceStatus.ISSUED]
        
        # Expiring soon (30 days)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring = [i for i in current if i.expiry_date and i.expiry_date <= expiry_threshold]
        
        return jsonify({
            'worker': {
                'id': worker.id,
                'name': worker.name,
                'company': worker.company,
                'trade': worker.trade
            },
            'current_ppe': [i.to_dict() for i in current],
            'expiring_soon': [i.to_dict() for i in expiring],
            'history': [i.to_dict() for i in issuances],
            'total_issued': len(issuances),
            'currently_issued': len(current)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 7. INVENTORY MANAGEMENT
# ========================================

@ppe_bp.route('/api/ppe/inventory', methods=['GET'])
@jwt_required()
def list_inventory():
    """
    List inventory with filters
    Query params: project_id, ppe_type, low_stock_only
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = PPEInventory.query.filter(
            PPEInventory.company_id == user.company_id,
            PPEInventory.is_deleted == False
        )
        
        if request.args.get('project_id'):
            query = query.filter(PPEInventory.project_id == request.args.get('project_id', type=int))
        
        if request.args.get('ppe_type'):
            query = query.filter(PPEInventory.ppe_type == PPEType[request.args.get('ppe_type')])
        
        if request.args.get('low_stock_only') == 'true':
            query = query.filter(PPEInventory.low_stock_alert == True)
        
        inventory_items = query.all()
        
        # Calculate summary
        total_value = sum(
            (item.total_stock * float(item.last_purchase_cost or 0))
            for item in inventory_items
        )
        
        low_stock_count = sum(1 for item in inventory_items if item.low_stock_alert)
        
        return jsonify({
            'inventory': [i.to_dict() for i in inventory_items],
            'count': len(inventory_items),
            'low_stock_count': low_stock_count,
            'total_inventory_value': round(total_value, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ppe_bp.route('/api/ppe/inventory', methods=['POST'])
@jwt_required()
def add_inventory():
    """
    Add new inventory item
    Body: {
        project_id, ppe_type, ppe_description, ppe_brand, ppe_model, ppe_size,
        total_stock, minimum_stock_level,
        storage_location, storage_bin,
        isi_marked, ce_marked, ansi_compliant,
        last_purchase_date, last_purchase_quantity, last_purchase_cost,
        supplier_name, supplier_contact
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        ppe_type_enum = PPEType[data['ppe_type']]
        
        # Create inventory
        inventory = PPEInventory(
            company_id=project.company_id,
            project_id=data['project_id'],
            ppe_type=ppe_type_enum,
            ppe_description=data['ppe_description'],
            ppe_brand=data.get('ppe_brand'),
            ppe_model=data.get('ppe_model'),
            ppe_size=data.get('ppe_size'),
            total_stock=data.get('total_stock', 0),
            issued_quantity=0,
            minimum_stock_level=data.get('minimum_stock_level', 10),
            last_purchase_date=datetime.fromisoformat(data['last_purchase_date']).date() if data.get('last_purchase_date') else None,
            last_purchase_quantity=data.get('last_purchase_quantity'),
            last_purchase_cost=data.get('last_purchase_cost'),
            supplier_name=data.get('supplier_name'),
            supplier_contact=data.get('supplier_contact'),
            storage_location=data.get('storage_location'),
            storage_bin=data.get('storage_bin'),
            isi_marked=data.get('isi_marked', False),
            ce_marked=data.get('ce_marked', False),
            ansi_compliant=data.get('ansi_compliant', False),
            test_certificate_url=data.get('test_certificate_url'),
            typical_lifespan_days=PPE_LIFESPAN_DAYS.get(ppe_type_enum, 365),
            created_by=user_id
        )
        
        inventory.update_stock_levels()
        
        db.session.add(inventory)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item added successfully',
            'inventory': inventory.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ppe_bp.route('/api/ppe/inventory/<int:inventory_id>/restock', methods=['POST'])
@jwt_required()
def restock_inventory(inventory_id):
    """
    Restock inventory
    Body: {
        quantity, purchase_cost, supplier_name, supplier_contact
    }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        inventory = PPEInventory.query.get(inventory_id)
        if not inventory or inventory.is_deleted:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        # Update stock
        inventory.total_stock += data.get('quantity', 0)
        inventory.last_purchase_date = date.today()
        inventory.last_purchase_quantity = data.get('quantity')
        inventory.last_purchase_cost = data.get('purchase_cost')
        
        if data.get('supplier_name'):
            inventory.supplier_name = data['supplier_name']
        if data.get('supplier_contact'):
            inventory.supplier_contact = data['supplier_contact']
        
        inventory.update_stock_levels()
        inventory.updated_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory restocked successfully',
            'inventory': inventory.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# 9. EXPIRY ALERTS
# ========================================

@ppe_bp.route('/api/ppe/expiring', methods=['GET'])
@jwt_required()
def get_expiring_ppe():
    """
    Get PPE items expiring soon (30 days)
    Query params: project_id, days_threshold (default 30)
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        days = request.args.get('days_threshold', default=30, type=int)
        expiry_threshold = date.today() + timedelta(days=days)
        
        query = PPEIssuance.query.filter(
            PPEIssuance.company_id == user.company_id,
            PPEIssuance.expiry_date <= expiry_threshold,
            PPEIssuance.expiry_date >= date.today(),
            PPEIssuance.status == IssuanceStatus.ISSUED,
            PPEIssuance.is_deleted == False
        )
        
        if request.args.get('project_id'):
            query = query.filter(PPEIssuance.project_id == request.args.get('project_id', type=int))
        
        expiring = query.order_by(PPEIssuance.expiry_date).all()
        
        return jsonify({
            'expiring_ppe': [i.to_dict() for i in expiring],
            'count': len(expiring),
            'days_threshold': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 10. PPE STATISTICS
# ========================================

@ppe_bp.route('/api/ppe/statistics', methods=['GET'])
@jwt_required()
def get_ppe_statistics():
    """
    Get PPE statistics
    Query params: project_id
    """
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        query = PPEIssuance.query.filter(
            PPEIssuance.company_id == user.company_id,
            PPEIssuance.is_deleted == False
        )
        
        if request.args.get('project_id'):
            project_id = request.args.get('project_id', type=int)
            query = query.filter(PPEIssuance.project_id == project_id)
        
        issuances = query.all()
        
        # Count by status
        total = len(issuances)
        issued = sum(1 for i in issuances if i.status == IssuanceStatus.ISSUED)
        returned = sum(1 for i in issuances if i.status == IssuanceStatus.RETURNED)
        damaged = sum(1 for i in issuances if i.status == IssuanceStatus.DAMAGED)
        lost = sum(1 for i in issuances if i.status == IssuanceStatus.LOST)
        expired = sum(1 for i in issuances if i.status == IssuanceStatus.EXPIRED)
        
        # Count by PPE type
        type_counts = {}
        for ppe_type in PPEType:
            type_counts[ppe_type.value] = sum(1 for i in issuances if i.ppe_type == ppe_type)
        
        # Expiring soon (30 days)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring_soon = sum(
            1 for i in issuances
            if i.status == IssuanceStatus.ISSUED and i.expiry_date and i.expiry_date <= expiry_threshold
        )
        
        # Total cost
        total_cost = sum(float(i.unit_cost or 0) for i in issuances)
        
        return jsonify({
            'total_issuances': total,
            'by_status': {
                'issued': issued,
                'returned': returned,
                'damaged': damaged,
                'lost': lost,
                'expired': expired
            },
            'by_type': type_counts,
            'expiring_soon_count': expiring_soon,
            'total_cost': round(total_cost, 2),
            'damage_rate': round((damaged / total * 100), 2) if total > 0 else 0,
            'loss_rate': round((lost / total * 100), 2) if total > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
