"""
Batch Import API - For sites where vehicle entry is managed by security team
Allows quality engineers to import batch data from Excel/CSV files or use quick entry form.

Use Cases:
1. Security team maintains vehicle register → QC team imports CSV
2. Security WhatsApp/shares vehicle details → QC team does quick entry
3. Gate register maintained separately → Periodic bulk import
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from datetime import datetime
import pandas as pd
import io
from server.models import BatchRegister, Project, RMCVendor, db
from flask_jwt_extended import jwt_required, get_jwt_identity

batch_import_bp = Blueprint('batch_import', __name__, url_prefix='/api/batches')


@batch_import_bp.route('/quick-entry', methods=['POST'])
@jwt_required()
def quick_entry_batch(current_user):
    """
    Quick batch entry for sites where vehicle entry is managed by security.
    Minimal fields - focuses only on QC-relevant data.
    
    Request Body:
    {
        "projectId": 1,
        "pourActivityId": 1,  // Optional
        "vehicleNumber": "MH-01-1234",
        "vendorName": "ABC Concrete",
        "grade": "M30",
        "quantityReceived": 1.5,
        "deliveryDate": "2025-11-12",
        "deliveryTime": "10:30",
        "slump": 100,
        "temperature": 32,
        "location": "Grid A-12, Slab",
        "remarks": "From security register"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['projectId', 'vehicleNumber', 'vendorName', 'grade', 'quantityReceived']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
        
        # Verify project exists
        project = db.session.query(Project).filter_by(id=data['projectId']).first()
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Auto-generate batch number
        last_batch = db.session.query(BatchRegister)\
            .filter_by(project_id=data['projectId'])\
            .order_by(BatchRegister.id.desc())\
            .first()
        
        next_number = 1
        if last_batch and last_batch.batch_number:
            parts = last_batch.batch_number.split('-')
            if len(parts) >= 3 and parts[-1].isdigit():
                next_number = int(parts[-1]) + 1
        
        year = datetime.now().year
        batch_number = f"BATCH-{year}-{next_number:04d}"
        
        # Parse delivery datetime
        delivery_date = data.get('deliveryDate', datetime.now().date().isoformat())
        delivery_time = data.get('deliveryTime', datetime.now().strftime('%H:%M'))
        delivery_datetime = datetime.fromisoformat(f"{delivery_date}T{delivery_time}:00")
        
        # Create batch
        batch = BatchRegister(
            project_id=data['projectId'],
            batch_number=batch_number,
            pour_activity_id=data.get('pourActivityId'),
            
            # Vendor details
            vendor_name=data['vendorName'],
            
            # Delivery details
            vehicle_number=data['vehicleNumber'],
            quantity_received=data['quantityReceived'],
            delivery_date=delivery_datetime,
            
            # Concrete details
            concrete_grade=data['grade'],
            slump_value=data.get('slump'),
            temperature=data.get('temperature'),
            
            # Location
            location_description=data.get('location'),
            
            # Status
            status='received',
            received_by=current_user.id,
            
            # Remarks
            remarks=data.get('remarks', 'Quick entry - vehicle register maintained by security')
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            "message": "Batch created successfully via quick entry",
            "batch": batch.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@batch_import_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_batches(current_user):
    """
    Bulk import batches from Excel/CSV file.
    For sites where security maintains vehicle register.
    
    Request: multipart/form-data
    - file: Excel (.xlsx) or CSV file
    - projectId: Project ID
    - pourActivityId: (Optional) Link all batches to this pour
    
    Excel/CSV Format:
    vehicleNumber, vendorName, grade, quantity, deliveryDate, deliveryTime, slump, temperature, location, remarks
    MH-01-1234, ABC Concrete, M30, 1.5, 2025-11-12, 10:30, 100, 32, Grid A-12, From gate register
    MH-01-5678, ABC Concrete, M30, 1.5, 2025-11-12, 11:00, 95, 33, Grid A-12, From gate register
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get parameters
        project_id = request.form.get('projectId')
        pour_activity_id = request.form.get('pourActivityId')
        
        if not project_id:
            return jsonify({"error": "projectId is required"}), 400
        
        # Verify project exists
        project = db.session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Read file
        file_content = file.read()
        
        # Detect file type and parse
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            return jsonify({"error": "Unsupported file format. Use .csv or .xlsx"}), 400
        
        # Validate required columns
        required_columns = ['vehicleNumber', 'vendorName', 'grade', 'quantity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                "error": f"Missing required columns: {', '.join(missing_columns)}",
                "requiredColumns": required_columns,
                "foundColumns": list(df.columns)
            }), 400
        
        # Get last batch number for auto-increment
        last_batch = db.session.query(BatchRegister)\
            .filter_by(project_id=project_id)\
            .order_by(BatchRegister.id.desc())\
            .first()
        
        next_number = 1
        if last_batch and last_batch.batch_number:
            parts = last_batch.batch_number.split('-')
            if len(parts) >= 3 and parts[-1].isdigit():
                next_number = int(parts[-1]) + 1
        
        # Process each row
        batches_created = []
        errors = []
        year = datetime.now().year
        
        for index, row in df.iterrows():
            try:
                # Auto-generate batch number
                batch_number = f"BATCH-{year}-{next_number:04d}"
                next_number += 1
                
                # Parse delivery datetime
                delivery_date = row.get('deliveryDate', datetime.now().date().isoformat())
                delivery_time = row.get('deliveryTime', '10:00')
                
                # Handle date parsing
                if pd.notna(delivery_date):
                    if isinstance(delivery_date, str):
                        delivery_date_str = delivery_date
                    else:
                        delivery_date_str = delivery_date.strftime('%Y-%m-%d')
                else:
                    delivery_date_str = datetime.now().date().isoformat()
                
                delivery_datetime = datetime.fromisoformat(f"{delivery_date_str}T{delivery_time}:00")
                
                # Create batch
                batch = BatchRegister(
                    project_id=project_id,
                    batch_number=batch_number,
                    pour_activity_id=pour_activity_id,
                    
                    # From CSV
                    vendor_name=str(row['vendorName']),
                    vehicle_number=str(row['vehicleNumber']),
                    quantity_received=float(row['quantity']),
                    concrete_grade=str(row['grade']),
                    delivery_date=delivery_datetime,
                    
                    # Optional fields
                    slump_value=float(row['slump']) if pd.notna(row.get('slump')) else None,
                    temperature=float(row['temperature']) if pd.notna(row.get('temperature')) else None,
                    location_description=str(row['location']) if pd.notna(row.get('location')) else None,
                    remarks=str(row['remarks']) if pd.notna(row.get('remarks')) else 'Imported from security register',
                    
                    # Status
                    status='received',
                    received_by=current_user.id
                )
                
                db.session.add(batch)
                batches_created.append({
                    "row": index + 1,
                    "batchNumber": batch_number,
                    "vehicleNumber": str(row['vehicleNumber']),
                    "quantity": float(row['quantity'])
                })
                
            except Exception as e:
                errors.append({
                    "row": index + 1,
                    "error": str(e),
                    "data": row.to_dict()
                })
        
        # Commit if any batches created
        if batches_created:
            db.session.commit()
        
        return jsonify({
            "message": f"Bulk import completed",
            "summary": {
                "total_rows": len(df),
                "success": len(batches_created),
                "errors": len(errors)
            },
            "batches_created": batches_created,
            "errors": errors if errors else None
        }), 201 if batches_created else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@batch_import_bp.route('/import-template', methods=['GET'])
@jwt_required()
def download_import_template(current_user):
    """
    Download Excel/CSV template for batch import.
    Provides sample data and column headers.
    """
    try:
        format_type = request.args.get('format', 'xlsx')  # xlsx or csv
        
        # Sample data
        sample_data = {
            'vehicleNumber': ['MH-01-1234', 'MH-01-5678', 'GJ-05-9012'],
            'vendorName': ['ABC Concrete', 'ABC Concrete', 'XYZ RMC'],
            'grade': ['M30', 'M30', 'M40'],
            'quantity': [1.5, 1.5, 1.0],
            'deliveryDate': ['2025-11-12', '2025-11-12', '2025-11-12'],
            'deliveryTime': ['10:30', '11:00', '11:30'],
            'slump': [100, 95, 110],
            'temperature': [32, 33, 31],
            'location': ['Grid A-12, Slab', 'Grid A-12, Slab', 'Grid B-5, Column'],
            'remarks': ['From security gate register', 'From security gate register', 'From security gate register']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create file in memory
        output = io.BytesIO()
        
        if format_type == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=batch_import_template.csv'
            }
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Batches', index=False)
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename=batch_import_template.xlsx'
            }
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
