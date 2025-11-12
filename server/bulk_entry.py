"""
Bulk Concrete Entry API
Quality engineers can select multiple RMC vehicles from material register
and create batches for all of them with single concrete details entry
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_

from .models import db
from .models import (
    MaterialVehicleRegister, BatchRegister, PourActivity,
    User, ProjectMembership, RMCVendor, MixDesign, Project
)

bulk_entry_bp = Blueprint('bulk_entry', __name__, url_prefix='/api/bulk-entry')


def check_quality_engineer_permission(user_id, project_id):
    """Check if user is quality engineer or higher"""
    membership = db.session.query(ProjectMembership).filter(
        and_(
            ProjectMembership.user_id == user_id,
            ProjectMembership.project_id == project_id,
            ProjectMembership.is_active == True
        )
    ).first()
    
    if not membership:
        return False, "User not assigned to this project"
    
    # Quality Engineer or higher roles can do bulk entry
    allowed_roles = ['ProjectAdmin', 'QualityManager', 'QualityEngineer']
    if membership.role not in allowed_roles:
        return False, "Insufficient permissions. Quality Engineer role or higher required."
    
    return True, membership.role


@bulk_entry_bp.route('/available-vehicles', methods=['GET'])
@jwt_required()
def get_available_vehicles():
    """
    Get available RMC vehicles from material register for bulk entry
    Only shows Concrete vehicles that are not yet linked to batches
    """
    try:
        user_id = get_jwt_identity()
        project_id = request.args.get('projectId', type=int)
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        # Check permissions
        has_permission, role = check_quality_engineer_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Get RMC vehicles (Concrete only) that are on_site or exited and not linked to batches
        vehicles = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete']),
                MaterialVehicleRegister.is_linked_to_batch == False
            )
        ).order_by(MaterialVehicleRegister.entry_time.desc()).all()
        
        # Filter by date range if provided
        date_from = request.args.get('dateFrom')
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00')).date()
            vehicles = [v for v in vehicles if v.entry_time.date() >= date_from_obj]
        
        date_to = request.args.get('dateTo')
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00')).date()
            vehicles = [v for v in vehicles if v.entry_time.date() <= date_to_obj]
        
        return jsonify({
            "success": True,
            "vehicles": [v.to_dict() for v in vehicles],
            "count": len(vehicles)
        }), 200
        
    except Exception as e:
        print(f"Error fetching available vehicles: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bulk_entry_bp.route('/create-batches', methods=['POST'])
@jwt_required()
def create_batches_from_vehicles():
    """
    Create multiple batches from selected vehicles with single concrete details
    
    Request body:
    {
        "projectId": 1,
        "vehicleIds": [123, 124, 125, 126],
        "concreteDetails": {
            "vendorName": "ABC Concrete",
            "grade": "M45FF",
            "totalQuantity": 4.0,
            "location": "A Building / 5th Slab",
            "slump": 100,
            "temperature": 32,
            "remarks": "Slab casting completed"
        },
        "pourActivityId": 1  // Optional
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        project_id = data.get('projectId')
        vehicle_ids = data.get('vehicleIds', [])
        concrete_details = data.get('concreteDetails', {})
        pour_activity_id = data.get('pourActivityId')
        
        if not project_id:
            return jsonify({"error": "Project ID required"}), 400
        
        if not vehicle_ids or len(vehicle_ids) == 0:
            return jsonify({"error": "At least one vehicle must be selected"}), 400
        
        if not concrete_details:
            return jsonify({"error": "Concrete details required"}), 400
        
        # Check permissions
        has_permission, role = check_quality_engineer_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Validate required concrete details
        required_fields = ['vendorName', 'grade']
        for field in required_fields:
            if field not in concrete_details or not concrete_details[field]:
                return jsonify({"error": f"{field} is required in concrete details"}), 400
        
        # Get all vehicles
        vehicles = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.id.in_(vehicle_ids),
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete'])
            )
        ).all()
        
        if len(vehicles) != len(vehicle_ids):
            return jsonify({"error": "Some vehicles not found or not valid RMC vehicles"}), 404
        
        # Check if any vehicle already linked to batch
        already_linked = [v for v in vehicles if v.is_linked_to_batch]
        if already_linked:
            vehicle_numbers = [v.vehicle_number for v in already_linked]
            return jsonify({
                "error": f"Some vehicles already linked to batches: {', '.join(vehicle_numbers)}"
            }), 400
        
        # Validate pour activity if provided
        pour_activity = None
        if pour_activity_id:
            pour_activity = db.session.query(PourActivity).filter(
                and_(
                    PourActivity.id == pour_activity_id,
                    PourActivity.project_id == project_id
                )
            ).first()
            
            if not pour_activity:
                return jsonify({"error": "Pour activity not found"}), 404
        
        # Calculate quantity per vehicle
        total_quantity = float(concrete_details.get('totalQuantity', 0))
        if total_quantity <= 0:
            # If no total quantity, use equal distribution or individual vehicle quantities
            quantity_per_vehicle = None
        else:
            quantity_per_vehicle = total_quantity / len(vehicles)
        
        # Find or create RMC vendor
        vendor_name = concrete_details.get('vendorName', 'Unknown Vendor')
        vendor = db.session.query(RMCVendor).filter(
            and_(
                RMCVendor.project_id == project_id,
                RMCVendor.vendor_name == vendor_name,
                RMCVendor.is_deleted == False
            )
        ).first()
        
        if not vendor:
            # Get project to get company_id
            project = db.session.query(Project).filter_by(id=project_id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
            
            # Create vendor on the fly
            vendor = RMCVendor(
                company_id=project.company_id,
                project_id=project_id,
                vendor_name=vendor_name,
                contact_person_name='Auto-created',
                contact_phone='0000000000',
                contact_email='autocreated@vendor.com',
                is_active=True,
                is_approved=True
            )
            db.session.add(vendor)
            db.session.flush()
        
        # Find or create mix design
        grade = concrete_details.get('grade', 'M25')
        mix_design = db.session.query(MixDesign).filter(
            and_(
                MixDesign.project_id == project_id,
                MixDesign.concrete_grade == grade,
                MixDesign.rmc_vendor_id == vendor.id,
                MixDesign.is_deleted == False
            )
        ).first()
        
        if not mix_design:
            # Create mix design on the fly
            # Extract strength from grade (e.g., M25 -> 25 MPa ≈ 3625 psi)
            try:
                strength_mpa = int(''.join(filter(str.isdigit, grade)))
                strength_psi = int(strength_mpa * 145)  # Convert MPa to psi
            except:
                strength_psi = 3000  # Default
            
            mix_design = MixDesign(
                project_id=project_id,
                rmc_vendor_id=vendor.id,
                project_name=project.name,
                mix_design_id=f"MD-{grade}-AUTO",
                specified_strength_psi=strength_psi,
                concrete_grade=grade,
                is_free_flow='FF' in grade.upper(),
                is_self_compacting='FF' in grade.upper() or 'SCC' in grade.upper(),
                slump_inches=concrete_details.get('slump', 100) / 25.4 if concrete_details.get('slump') else 4.0,  # mm to inches
                uploaded_by=user_id,
                is_approved=True,
                approved_by=user_id,
                approved_at=datetime.utcnow()
            )
            db.session.add(mix_design)
            db.session.flush()
        
        # Parse location string (e.g., "Building A / 5th Floor Slab")
        location_str = concrete_details.get('location', '')
        building_name = None
        floor_level = None
        structural_element = None
        
        if '/' in location_str:
            parts = [p.strip() for p in location_str.split('/')]
            if len(parts) >= 1:
                building_name = parts[0]
            if len(parts) >= 2:
                floor_level = parts[1]
                # Extract structural element type from floor description
                floor_lower = floor_level.lower()
                if 'slab' in floor_lower:
                    structural_element = 'Slab'
                elif 'beam' in floor_lower:
                    structural_element = 'Beam'
                elif 'column' in floor_lower:
                    structural_element = 'Column'
                elif 'wall' in floor_lower:
                    structural_element = 'Wall'
                elif 'footing' in floor_lower:
                    structural_element = 'Footing'
        else:
            building_name = location_str
        
        # Create batches for each vehicle
        created_batches = []
        batch_errors = []
        
        for vehicle in vehicles:
            try:
                # Generate batch number
                year = datetime.utcnow().year
                last_batch = db.session.query(BatchRegister).filter(
                    BatchRegister.project_id == project_id
                ).order_by(BatchRegister.id.desc()).first()
                
                if last_batch and last_batch.batch_number:
                    # Extract sequence number
                    parts = last_batch.batch_number.split('-')
                    if len(parts) >= 3:
                        try:
                            last_seq = int(parts[-1])
                            seq_num = last_seq + 1
                        except:
                            seq_num = len(created_batches) + 1
                    else:
                        seq_num = len(created_batches) + 1
                else:
                    seq_num = len(created_batches) + 1
                
                batch_number = f"BATCH-{year}-{seq_num:04d}"
                
                # Create batch with correct schema
                batch = BatchRegister(
                    project_id=project_id,
                    mix_design_id=mix_design.id,
                    rmc_vendor_id=vendor.id,
                    batch_number=batch_number,
                    vehicle_number=vehicle.vehicle_number,
                    driver_name=vehicle.driver_name,
                    quantity_ordered=quantity_per_vehicle if quantity_per_vehicle else 1.0,
                    quantity_received=quantity_per_vehicle if quantity_per_vehicle else 1.0,
                    delivery_date=vehicle.entry_time if vehicle.entry_time else datetime.utcnow(),
                    delivery_time=vehicle.entry_time.strftime('%H:%M') if vehicle.entry_time else datetime.utcnow().strftime('%H:%M'),
                    temperature_celsius=concrete_details.get('temperature'),
                    slump_tested=concrete_details.get('slump'),
                    building_name=building_name,
                    floor_level=floor_level,
                    structural_element_type=structural_element,
                    pour_location_description=location_str,
                    pour_activity_id=pour_activity_id,
                    entered_by=user_id,
                    verification_status='pending'
                )
                
                db.session.add(batch)
                db.session.flush()  # Get batch ID
                
                # Link vehicle to batch
                vehicle.linked_batch_id = batch.id
                vehicle.is_linked_to_batch = True
                vehicle.updated_by = user_id
                vehicle.updated_at = datetime.utcnow()
                
                created_batches.append({
                    "batchNumber": batch.batch_number,
                    "vehicleNumber": vehicle.vehicle_number,
                    "quantity": batch.quantity_received,
                    "batchId": batch.id,
                    "vehicleId": vehicle.id
                })
                
            except Exception as e:
                batch_errors.append({
                    "vehicleNumber": vehicle.vehicle_number,
                    "error": str(e)
                })
                print(f"Error creating batch for vehicle {vehicle.vehicle_number}: {e}")
        
        # Commit all changes if all batches created successfully
        if len(created_batches) == len(vehicles):
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": f"Successfully created {len(created_batches)} batch(es)",
                "batches": created_batches,
                "summary": {
                    "totalVehicles": len(vehicles),
                    "batchesCreated": len(created_batches),
                    "errors": len(batch_errors)
                }
            }), 201
        else:
            # Partial success or complete failure
            db.session.commit()  # Commit successful ones
            
            return jsonify({
                "success": len(created_batches) > 0,
                "message": f"Created {len(created_batches)} batch(es) with {len(batch_errors)} error(s)",
                "batches": created_batches,
                "errors": batch_errors,
                "summary": {
                    "totalVehicles": len(vehicles),
                    "batchesCreated": len(created_batches),
                    "errors": len(batch_errors)
                }
            }), 207  # Multi-Status
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk batch creation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bulk_entry_bp.route('/preview', methods=['POST'])
@jwt_required()
def preview_bulk_entry():
    """
    Preview what batches will be created before actual creation
    Returns vehicle details and calculated quantities
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        project_id = data.get('projectId')
        vehicle_ids = data.get('vehicleIds', [])
        total_quantity = data.get('totalQuantity', 0)
        
        if not project_id or not vehicle_ids:
            return jsonify({"error": "Project ID and vehicle IDs required"}), 400
        
        # Check permissions
        has_permission, role = check_quality_engineer_permission(user_id, project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        # Get vehicles
        vehicles = db.session.query(MaterialVehicleRegister).filter(
            and_(
                MaterialVehicleRegister.id.in_(vehicle_ids),
                MaterialVehicleRegister.project_id == project_id,
                MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete'])
            )
        ).all()
        
        if len(vehicles) != len(vehicle_ids):
            return jsonify({"error": "Some vehicles not found"}), 404
        
        # Calculate quantity per vehicle
        quantity_per_vehicle = float(total_quantity) / len(vehicles) if total_quantity > 0 else 0
        
        # Prepare preview
        preview = []
        for vehicle in vehicles:
            preview.append({
                "vehicleId": vehicle.id,
                "vehicleNumber": vehicle.vehicle_number,
                "supplierName": vehicle.supplier_name,
                "entryTime": vehicle.entry_time.isoformat() if vehicle.entry_time else None,
                "driverName": vehicle.driver_name,
                "challanNumber": vehicle.challan_number,
                "calculatedQuantity": round(quantity_per_vehicle, 2),
                "isLinked": vehicle.is_linked_to_batch,
                "status": vehicle.status
            })
        
        return jsonify({
            "success": True,
            "preview": preview,
            "summary": {
                "totalVehicles": len(vehicles),
                "totalQuantity": total_quantity,
                "quantityPerVehicle": round(quantity_per_vehicle, 2)
            }
        }), 200
        
    except Exception as e:
        print(f"Error generating preview: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bulk_entry_bp.route('/unlink-vehicle', methods=['POST'])
@jwt_required()
def unlink_vehicle_from_batch():
    """
    Unlink a vehicle from its batch (in case of error)
    Quality Engineer or Admin only
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        vehicle_id = data.get('vehicleId')
        
        if not vehicle_id:
            return jsonify({"error": "Vehicle ID required"}), 400
        
        # Get vehicle
        vehicle = db.session.query(MaterialVehicleRegister).filter(
            MaterialVehicleRegister.id == vehicle_id
        ).first()
        
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404
        
        # Check permissions
        has_permission, role = check_quality_engineer_permission(user_id, vehicle.project_id)
        if not has_permission:
            return jsonify({"error": role}), 403
        
        if not vehicle.is_linked_to_batch:
            return jsonify({"error": "Vehicle is not linked to any batch"}), 400
        
        # Unlink
        old_batch_id = vehicle.linked_batch_id
        vehicle.linked_batch_id = None
        vehicle.is_linked_to_batch = False
        vehicle.updated_by = user_id
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Vehicle {vehicle.vehicle_number} unlinked from batch",
            "vehicleId": vehicle_id,
            "previousBatchId": old_batch_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error unlinking vehicle: {str(e)}")
        return jsonify({"error": str(e)}), 500
