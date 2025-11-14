"""
Safety Management Module
Handles TBT, PTW, NC, Audits, Inductions, Incidents, and PPE
"""
from .routes.safety_api import safety_bp
from .routes.tbt_api import tbt_bp
from .routes.ptw_api import ptw_bp
from .routes.nc_api import nc_bp
from .routes.audits_api import audits_bp
from .routes.induction_api import induction_bp
from .routes.incidents_api import incident_bp
from .routes.ppe_api import ppe_bp

__all__ = [
    'safety_bp', 'tbt_bp', 'ptw_bp', 'nc_bp',
    'audits_bp', 'induction_bp', 'incident_bp', 'ppe_bp'
]
