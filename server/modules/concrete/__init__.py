"""
Concrete Quality Management Module
Handles batches, tests, NC, vendors, labs, and pour activities
"""
from .routes.batches_api import batch_bp
from .routes.tests_api import cube_test_bp
from .routes.nc_api import concrete_nc_bp
from .routes.vendors_api import vendor_bp
from .routes.labs_api import lab_bp
from .routes.pour_api import pour_bp

__all__ = [
    'batch_bp', 'cube_test_bp', 'concrete_nc_bp',
    'vendor_bp', 'lab_bp', 'pour_bp'
]
