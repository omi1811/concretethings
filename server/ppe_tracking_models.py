"""
PPE Tracking Models
Database models for PPE issuance, return, damage tracking, and inventory management
"""

from server.db import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Numeric, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

class PPEType(enum.Enum):
    """Standard PPE types with typical lifespans"""
    SAFETY_HELMET = "SAFETY_HELMET"  # 3 years
    SAFETY_SHOES = "SAFETY_SHOES"  # 6 months
    FULL_BODY_HARNESS = "FULL_BODY_HARNESS"  # 5 years
    SAFETY_GOGGLES = "SAFETY_GOGGLES"  # 1 year
    HAND_GLOVES = "HAND_GLOVES"  # 1 month
    REFLECTIVE_JACKET = "REFLECTIVE_JACKET"  # 1 year
    EAR_PLUGS = "EAR_PLUGS"  # Single use
    DUST_MASK = "DUST_MASK"  # Single use
    FACE_SHIELD = "FACE_SHIELD"  # 1 year
    WELDING_HELMET = "WELDING_HELMET"  # 2 years
    CHEMICAL_SUIT = "CHEMICAL_SUIT"  # 6 months
    RUBBER_BOOTS = "RUBBER_BOOTS"  # 1 year
    RAINCOAT = "RAINCOAT"  # 1 year
    LIFELINE_ROPE = "LIFELINE_ROPE"  # 2 years
    DOUBLE_LANYARD = "DOUBLE_LANYARD"  # 5 years

class IssuanceStatus(enum.Enum):
    """PPE issuance status"""
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    DAMAGED = "DAMAGED"
    LOST = "LOST"
    EXPIRED = "EXPIRED"

class PPECondition(enum.Enum):
    """Condition of PPE"""
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"
    DAMAGED = "DAMAGED"
    EXPIRED = "EXPIRED"


class PPEIssuance(Base):
    """
    PPE Issuance/Return Record
    Tracks individual PPE items issued to workers
    """
    __tablename__ = 'ppe_issuances'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Issuance Details
    issuance_number = Column(String(50), unique=True, nullable=False)  # PPE-{project}-{year}-{seq}
    worker_id = Column(Integer, ForeignKey('safety_workers.id'), nullable=False)
    
    # PPE Item
    ppe_type = Column(Enum(PPEType), nullable=False)
    ppe_description = Column(String(200))  # "Red Safety Helmet - ISI Marked"
    ppe_brand = Column(String(100))  # "Karam", "Honeywell"
    ppe_model = Column(String(100))
    ppe_size = Column(String(20))  # "L", "42", "Free Size"
    
    # Identification
    serial_number = Column(String(100))  # For tracked items (helmets, harnesses)
    barcode = Column(String(100))  # QR/Barcode for quick scanning
    
    # Issuance
    issue_date = Column(Date, nullable=False)
    issued_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    issue_remarks = Column(Text)
    
    # Lifecycle
    expected_return_date = Column(Date)  # For temporary issuance
    expiry_date = Column(Date)  # Based on PPE type lifespan
    
    # Return
    return_date = Column(Date)
    returned_to_id = Column(Integer, ForeignKey('users.id'))
    return_condition = Column(Enum(PPECondition))
    return_remarks = Column(Text)
    
    # Damage/Loss
    damage_reported_date = Column(Date)
    damage_description = Column(Text)
    damage_photos = Column(JSON)  # [{url, description, timestamp}]
    replacement_required = Column(Boolean, default=False)
    replacement_issuance_id = Column(Integer, ForeignKey('ppe_issuances.id'))  # Link to replacement
    
    # Loss
    loss_reported_date = Column(Date)
    loss_remarks = Column(Text)
    penalty_amount = Column(Numeric(10, 2))  # Deduction from worker
    
    # Status
    status = Column(Enum(IssuanceStatus), default=IssuanceStatus.ISSUED)
    is_expired = Column(Boolean, default=False)
    
    # Compliance
    isi_marked = Column(Boolean, default=False)  # Indian Standards Institute
    ce_marked = Column(Boolean, default=False)  # European Conformity
    ansi_compliant = Column(Boolean, default=False)  # American National Standards
    test_certificate_url = Column(String(500))  # S3 path to compliance certificate
    
    # Cost
    unit_cost = Column(Numeric(10, 2))
    
    # Audit Trail
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='ppe_issuances')
    project = relationship('Project', backref='ppe_issuances')
    worker = relationship('Worker', backref='ppe_issued')
    issued_by = relationship('User', foreign_keys=[issued_by_id])
    returned_to = relationship('User', foreign_keys=[returned_to_id])
    replacement = relationship('PPEIssuance', remote_side=[id], backref='replaced_item')
    
    def check_expiry(self):
        """Check if PPE has expired"""
        if self.expiry_date and self.expiry_date < datetime.now().date():
            self.is_expired = True
            if self.status == IssuanceStatus.ISSUED:
                self.status = IssuanceStatus.EXPIRED
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        self.check_expiry()
        
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'issuance_number': self.issuance_number,
            
            'worker': {
                'id': self.worker_id,
                'name': self.worker.name if self.worker else None,
                'company': self.worker.company if self.worker else None,
                'trade': self.worker.trade if self.worker else None
            } if self.worker else None,
            
            'ppe': {
                'type': self.ppe_type.value if self.ppe_type else None,
                'description': self.ppe_description,
                'brand': self.ppe_brand,
                'model': self.ppe_model,
                'size': self.ppe_size,
                'serial_number': self.serial_number,
                'barcode': self.barcode
            },
            
            'issuance': {
                'issue_date': self.issue_date.isoformat() if self.issue_date else None,
                'issued_by_id': self.issued_by_id,
                'issued_by_name': self.issued_by.name if self.issued_by else None,
                'issue_remarks': self.issue_remarks
            },
            
            'lifecycle': {
                'expected_return_date': self.expected_return_date.isoformat() if self.expected_return_date else None,
                'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
                'is_expired': self.is_expired,
                'days_until_expiry': (self.expiry_date - datetime.now().date()).days if self.expiry_date and not self.is_expired else None
            },
            
            'return': {
                'return_date': self.return_date.isoformat() if self.return_date else None,
                'returned_to_id': self.returned_to_id,
                'returned_to_name': self.returned_to.name if self.returned_to else None,
                'return_condition': self.return_condition.value if self.return_condition else None,
                'return_remarks': self.return_remarks
            },
            
            'damage': {
                'damage_reported_date': self.damage_reported_date.isoformat() if self.damage_reported_date else None,
                'damage_description': self.damage_description,
                'damage_photos': self.damage_photos or [],
                'replacement_required': self.replacement_required,
                'replacement_issuance_id': self.replacement_issuance_id
            },
            
            'loss': {
                'loss_reported_date': self.loss_reported_date.isoformat() if self.loss_reported_date else None,
                'loss_remarks': self.loss_remarks,
                'penalty_amount': float(self.penalty_amount) if self.penalty_amount else 0
            },
            
            'status': self.status.value if self.status else None,
            
            'compliance': {
                'isi_marked': self.isi_marked,
                'ce_marked': self.ce_marked,
                'ansi_compliant': self.ansi_compliant,
                'test_certificate_url': self.test_certificate_url
            },
            
            'cost': {
                'unit_cost': float(self.unit_cost) if self.unit_cost else 0
            },
            
            'audit_trail': {
                'created_by': self.created_by,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_by': self.updated_by,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }


class PPEInventory(Base):
    """
    PPE Stock Inventory
    Tracks available PPE stock at project level
    """
    __tablename__ = 'ppe_inventory'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Organization
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # PPE Item
    ppe_type = Column(Enum(PPEType), nullable=False)
    ppe_description = Column(String(200), nullable=False)
    ppe_brand = Column(String(100))
    ppe_model = Column(String(100))
    ppe_size = Column(String(20))
    
    # Stock Levels
    total_stock = Column(Integer, default=0)
    issued_quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)  # total - issued
    minimum_stock_level = Column(Integer, default=10)  # Reorder level
    
    # Procurement
    last_purchase_date = Column(Date)
    last_purchase_quantity = Column(Integer)
    last_purchase_cost = Column(Numeric(10, 2))
    supplier_name = Column(String(200))
    supplier_contact = Column(String(100))
    
    # Storage
    storage_location = Column(String(200))  # "Store Room A - Shelf 3"
    storage_bin = Column(String(50))
    
    # Compliance
    isi_marked = Column(Boolean, default=False)
    ce_marked = Column(Boolean, default=False)
    ansi_compliant = Column(Boolean, default=False)
    test_certificate_url = Column(String(500))
    
    # Lifecycle (typical for this PPE type)
    typical_lifespan_days = Column(Integer)  # Auto-set based on PPE type
    
    # Alerts
    low_stock_alert = Column(Boolean, default=False)  # available < minimum
    expiry_alert = Column(Boolean, default=False)  # Items expiring soon
    
    # Audit Trail
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', backref='ppe_inventory')
    project = relationship('Project', backref='ppe_inventory')
    
    def update_stock_levels(self):
        """Recalculate available quantity and alerts"""
        self.available_quantity = self.total_stock - self.issued_quantity
        self.low_stock_alert = self.available_quantity < self.minimum_stock_level
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        self.update_stock_levels()
        
        return {
            'id': self.id,
            'company_id': self.company_id,
            'project_id': self.project_id,
            
            'ppe': {
                'type': self.ppe_type.value if self.ppe_type else None,
                'description': self.ppe_description,
                'brand': self.ppe_brand,
                'model': self.ppe_model,
                'size': self.ppe_size
            },
            
            'stock': {
                'total_stock': self.total_stock,
                'issued_quantity': self.issued_quantity,
                'available_quantity': self.available_quantity,
                'minimum_stock_level': self.minimum_stock_level,
                'low_stock_alert': self.low_stock_alert,
                'reorder_quantity': max(0, self.minimum_stock_level * 2 - self.available_quantity)
            },
            
            'procurement': {
                'last_purchase_date': self.last_purchase_date.isoformat() if self.last_purchase_date else None,
                'last_purchase_quantity': self.last_purchase_quantity,
                'last_purchase_cost': float(self.last_purchase_cost) if self.last_purchase_cost else 0,
                'supplier_name': self.supplier_name,
                'supplier_contact': self.supplier_contact
            },
            
            'storage': {
                'location': self.storage_location,
                'bin': self.storage_bin
            },
            
            'compliance': {
                'isi_marked': self.isi_marked,
                'ce_marked': self.ce_marked,
                'ansi_compliant': self.ansi_compliant,
                'test_certificate_url': self.test_certificate_url
            },
            
            'lifecycle': {
                'typical_lifespan_days': self.typical_lifespan_days
            },
            
            'alerts': {
                'low_stock_alert': self.low_stock_alert,
                'expiry_alert': self.expiry_alert
            },
            
            'audit_trail': {
                'created_by': self.created_by,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_by': self.updated_by,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }


# ========================================
# PPE LIFESPAN MAPPING
# ========================================

PPE_LIFESPAN_DAYS = {
    PPEType.SAFETY_HELMET: 1095,  # 3 years
    PPEType.SAFETY_SHOES: 180,  # 6 months
    PPEType.FULL_BODY_HARNESS: 1825,  # 5 years
    PPEType.SAFETY_GOGGLES: 365,  # 1 year
    PPEType.HAND_GLOVES: 30,  # 1 month
    PPEType.REFLECTIVE_JACKET: 365,  # 1 year
    PPEType.EAR_PLUGS: 1,  # Single use
    PPEType.DUST_MASK: 1,  # Single use
    PPEType.FACE_SHIELD: 365,  # 1 year
    PPEType.WELDING_HELMET: 730,  # 2 years
    PPEType.CHEMICAL_SUIT: 180,  # 6 months
    PPEType.RUBBER_BOOTS: 365,  # 1 year
    PPEType.RAINCOAT: 365,  # 1 year
    PPEType.LIFELINE_ROPE: 730,  # 2 years
    PPEType.DOUBLE_LANYARD: 1825,  # 5 years
}

def get_ppe_expiry_date(ppe_type, issue_date):
    """Calculate expiry date based on PPE type and issue date"""
    lifespan_days = PPE_LIFESPAN_DAYS.get(ppe_type, 365)
    return issue_date + timedelta(days=lifespan_days)
