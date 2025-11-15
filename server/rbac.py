"""
Role-Based Access Control (RBAC) System
Comprehensive user roles and permissions for multi-industry platform
"""

from enum import Enum
from typing import List, Dict, Set


class UserRole(Enum):
    """
    Comprehensive user roles for ProSite platform
    Covers construction, manufacturing, facilities management, and other industries
    """
    # Level 1 - Full System Access
    SYSTEM_ADMIN = "system_admin"
    
    # Level 2 - Project Leadership
    PROJECT_MANAGER = "project_manager"
    
    # Level 3 - Department Managers
    QUALITY_MANAGER = "quality_manager"
    SAFETY_MANAGER = "safety_manager"
    
    # Level 4 - Engineers & Specialists
    QUALITY_ENGINEER = "quality_engineer"
    SAFETY_ENGINEER = "safety_engineer"
    BUILDING_ENGINEER = "building_engineer"
    
    # Level 5 - Supervisors & Operations
    CONTRACTOR_SUPERVISOR = "contractor_supervisor"
    WATCHMAN = "watchman"
    
    # External Roles
    CLIENT = "client"
    AUDITOR = "auditor"
    SUPPLIER = "supplier"


class Permission(Enum):
    """
    Granular permissions for module access control
    """
    # Dashboard & Analytics
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"
    
    # Project Management
    VIEW_PROJECT = "view_project"
    CREATE_PROJECT = "create_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    
    # Batch Management
    VIEW_BATCH = "view_batch"
    CREATE_BATCH = "create_batch"
    EDIT_BATCH = "edit_batch"
    DELETE_BATCH = "delete_batch"
    APPROVE_BATCH = "approve_batch"
    REJECT_BATCH = "reject_batch"
    
    # Cube Tests
    VIEW_CUBE_TEST = "view_cube_test"
    CREATE_CUBE_TEST = "create_cube_test"
    EDIT_CUBE_TEST = "edit_cube_test"
    DELETE_CUBE_TEST = "delete_cube_test"
    
    # Material Tests
    VIEW_MATERIAL_TEST = "view_material_test"
    CREATE_MATERIAL_TEST = "create_material_test"
    EDIT_MATERIAL_TEST = "edit_material_test"
    DELETE_MATERIAL_TEST = "delete_material_test"
    
    # Non-Conformance Reports (Quality)
    VIEW_NCR = "view_ncr"
    CREATE_NCR = "create_ncr"
    EDIT_NCR = "edit_ncr"
    RESPOND_NCR = "respond_ncr"  # Respond to NCRs with corrective actions
    APPROVE_NCR = "approve_ncr"
    CLOSE_NCR = "close_ncr"
    
    # Safety Non-Conformance
    VIEW_SAFETY_NC = "view_safety_nc"
    CREATE_SAFETY_NC = "create_safety_nc"
    EDIT_SAFETY_NC = "edit_safety_nc"
    APPROVE_SAFETY_NC = "approve_safety_nc"
    CLOSE_SAFETY_NC = "close_safety_nc"
    
    # Permit to Work (PTW)
    VIEW_PTW = "view_ptw"
    CREATE_PTW = "create_ptw"
    APPROVE_PTW = "approve_ptw"
    CLOSE_PTW = "close_ptw"
    
    # Training & Safety
    VIEW_TRAINING = "view_training"
    CREATE_TRAINING = "create_training"
    SCHEDULE_TRAINING = "schedule_training"
    MARK_ATTENDANCE = "mark_attendance"
    
    # Pour Activities
    VIEW_POUR_ACTIVITY = "view_pour_activity"
    CREATE_POUR_ACTIVITY = "create_pour_activity"
    EDIT_POUR_ACTIVITY = "edit_pour_activity"
    DELETE_POUR_ACTIVITY = "delete_pour_activity"
    
    # Labs
    VIEW_LAB = "view_lab"
    CREATE_LAB = "create_lab"
    EDIT_LAB = "edit_lab"
    DELETE_LAB = "delete_lab"
    
    # Handovers
    VIEW_HANDOVER = "view_handover"
    CREATE_HANDOVER = "create_handover"
    APPROVE_HANDOVER = "approve_handover"
    
    # Gate Register / Security
    VIEW_GATE_LOG = "view_gate_log"
    CREATE_GATE_LOG = "create_gate_log"
    EDIT_GATE_LOG = "edit_gate_log"
    
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    ASSIGN_ROLES = "assign_roles"
    
    # System Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    
    # Documents & Uploads
    UPLOAD_DOCUMENTS = "upload_documents"
    DELETE_DOCUMENTS = "delete_documents"
    
    # Financial
    VIEW_COSTS = "view_costs"
    EDIT_BUDGET = "edit_budget"


class RBACManager:
    """
    Role-Based Access Control Manager
    Manages permissions for each user role
    """
    
    # Define permissions for each role
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        
        # SYSTEM ADMINISTRATOR - Full Access
        UserRole.SYSTEM_ADMIN: {
            # All permissions
            *Permission.__members__.values()
        },
        
        # PROJECT MANAGER - Project-level full access
        UserRole.PROJECT_MANAGER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.VIEW_PROJECT,
            Permission.EDIT_PROJECT,
            Permission.VIEW_BATCH,
            Permission.CREATE_BATCH,
            Permission.EDIT_BATCH,
            Permission.APPROVE_BATCH,
            Permission.REJECT_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.VIEW_NCR,
            Permission.CREATE_NCR,
            Permission.APPROVE_NCR,
            Permission.VIEW_SAFETY_NC,
            Permission.CREATE_SAFETY_NC,
            Permission.VIEW_PTW,
            Permission.APPROVE_PTW,
            Permission.VIEW_TRAINING,
            Permission.SCHEDULE_TRAINING,
            Permission.VIEW_POUR_ACTIVITY,
            Permission.CREATE_POUR_ACTIVITY,
            Permission.EDIT_POUR_ACTIVITY,
            Permission.VIEW_LAB,
            Permission.VIEW_HANDOVER,
            Permission.APPROVE_HANDOVER,
            Permission.VIEW_GATE_LOG,
            Permission.VIEW_USERS,
            Permission.UPLOAD_DOCUMENTS,
            Permission.VIEW_COSTS,
            Permission.EDIT_BUDGET,
        },
        
        # QUALITY MANAGER - Quality oversight + approvals
        UserRole.QUALITY_MANAGER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.CREATE_BATCH,
            Permission.EDIT_BATCH,
            Permission.APPROVE_BATCH,
            Permission.REJECT_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.CREATE_CUBE_TEST,
            Permission.EDIT_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.CREATE_MATERIAL_TEST,
            Permission.EDIT_MATERIAL_TEST,
            Permission.VIEW_NCR,
            Permission.CREATE_NCR,
            Permission.EDIT_NCR,
            Permission.APPROVE_NCR,
            Permission.CLOSE_NCR,
            Permission.VIEW_LAB,
            Permission.CREATE_LAB,
            Permission.EDIT_LAB,
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # SAFETY MANAGER - Safety oversight + approvals
        UserRole.SAFETY_MANAGER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_SAFETY_NC,
            Permission.CREATE_SAFETY_NC,
            Permission.EDIT_SAFETY_NC,
            Permission.APPROVE_SAFETY_NC,
            Permission.CLOSE_SAFETY_NC,
            Permission.VIEW_PTW,
            Permission.CREATE_PTW,
            Permission.APPROVE_PTW,
            Permission.CLOSE_PTW,
            Permission.VIEW_TRAINING,
            Permission.CREATE_TRAINING,
            Permission.SCHEDULE_TRAINING,
            Permission.MARK_ATTENDANCE,
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # QUALITY ENGINEER - Quality execution
        UserRole.QUALITY_ENGINEER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.CREATE_BATCH,
            Permission.EDIT_BATCH,
            Permission.REJECT_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.CREATE_CUBE_TEST,
            Permission.EDIT_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.CREATE_MATERIAL_TEST,
            Permission.EDIT_MATERIAL_TEST,
            Permission.VIEW_NCR,
            Permission.CREATE_NCR,
            Permission.EDIT_NCR,
            Permission.VIEW_LAB,
            Permission.CREATE_LAB,
            Permission.EDIT_LAB,
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # SAFETY ENGINEER - Safety execution
        UserRole.SAFETY_ENGINEER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_SAFETY_NC,
            Permission.CREATE_SAFETY_NC,
            Permission.EDIT_SAFETY_NC,
            Permission.VIEW_PTW,
            Permission.CREATE_PTW,
            Permission.VIEW_TRAINING,
            Permission.CREATE_TRAINING,
            Permission.MARK_ATTENDANCE,
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # BUILDING ENGINEER - Site execution
        UserRole.BUILDING_ENGINEER: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.CREATE_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.VIEW_POUR_ACTIVITY,
            Permission.CREATE_POUR_ACTIVITY,
            Permission.EDIT_POUR_ACTIVITY,
            Permission.VIEW_HANDOVER,
            Permission.CREATE_HANDOVER,
            Permission.VIEW_GATE_LOG,
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # CONTRACTOR SUPERVISOR - Extended execution (NCs, PTW, TBT)
        UserRole.CONTRACTOR_SUPERVISOR: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.VIEW_MATERIAL_TEST,
            Permission.VIEW_POUR_ACTIVITY,
            Permission.VIEW_NCR,  # Can view Quality NCs
            Permission.RESPOND_NCR,  # Can respond to Quality NCs with corrective actions
            Permission.VIEW_SAFETY_NC,
            Permission.CREATE_SAFETY_NC,
            Permission.EDIT_SAFETY_NC,
            Permission.CLOSE_SAFETY_NC,  # Can close safety NCs
            Permission.VIEW_PTW,
            Permission.CREATE_PTW,  # Can create/fill safety work permits
            Permission.VIEW_TRAINING,
            Permission.CREATE_TRAINING,  # Can conduct toolbox talks (TBT)
            Permission.MARK_ATTENDANCE,  # Can mark TBT attendance
            Permission.UPLOAD_DOCUMENTS,
        },
        
        # WATCHMAN - Gate operations, RMC register, Worker attendance
        UserRole.WATCHMAN: {
            Permission.VIEW_GATE_LOG,
            Permission.CREATE_GATE_LOG,
            Permission.EDIT_GATE_LOG,
            Permission.VIEW_BATCH,  # Can view RMC deliveries
            Permission.CREATE_BATCH,  # Can fill RMC register
            Permission.CREATE_SAFETY_NC,  # Can report security incidents
            Permission.MARK_ATTENDANCE,  # Can scan QR for worker entry/exit
        },
        
        # CLIENT - View-only access
        UserRole.CLIENT: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.VIEW_NCR,
            Permission.VIEW_SAFETY_NC,
            Permission.VIEW_POUR_ACTIVITY,
            Permission.VIEW_HANDOVER,
        },
        
        # AUDITOR - Full view-only access
        UserRole.AUDITOR: {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.VIEW_PROJECT,
            Permission.VIEW_BATCH,
            Permission.VIEW_CUBE_TEST,
            Permission.VIEW_MATERIAL_TEST,
            Permission.VIEW_NCR,
            Permission.VIEW_SAFETY_NC,
            Permission.VIEW_PTW,
            Permission.VIEW_TRAINING,
            Permission.VIEW_POUR_ACTIVITY,
            Permission.VIEW_LAB,
            Permission.VIEW_HANDOVER,
            Permission.VIEW_GATE_LOG,
        },
        
        # SUPPLIER - Limited portal access
        UserRole.SUPPLIER: {
            Permission.VIEW_BATCH,  # Their deliveries only
            Permission.VIEW_MATERIAL_TEST,  # Their materials only
            Permission.VIEW_NCR,  # NCRs related to their supplies
            Permission.UPLOAD_DOCUMENTS,  # Certificates, MTCs
        },
    }
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> Set[Permission]:
        """Get all permissions for a specific role"""
        return RBACManager.ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        role_permissions = RBACManager.get_role_permissions(role)
        return permission in role_permissions
    
    @staticmethod
    def can_access_module(role: UserRole, module: str) -> bool:
        """
        Check if role can access a specific module
        
        Args:
            role: User role
            module: Module name (batches, cube_tests, safety_nc, etc.)
        """
        role_permissions = RBACManager.get_role_permissions(role)
        
        # Module to permission mapping
        module_permissions = {
            'batches': [Permission.VIEW_BATCH],
            'cube_tests': [Permission.VIEW_CUBE_TEST],
            'material_tests': [Permission.VIEW_MATERIAL_TEST],
            'ncr': [Permission.VIEW_NCR],
            'safety_nc': [Permission.VIEW_SAFETY_NC],
            'ptw': [Permission.VIEW_PTW],
            'training': [Permission.VIEW_TRAINING],
            'pour_activities': [Permission.VIEW_POUR_ACTIVITY],
            'labs': [Permission.VIEW_LAB],
            'handovers': [Permission.VIEW_HANDOVER],
            'gate_register': [Permission.VIEW_GATE_LOG],
            'analytics': [Permission.VIEW_ANALYTICS],
            'users': [Permission.VIEW_USERS],
            'settings': [Permission.VIEW_SETTINGS],
        }
        
        required_permissions = module_permissions.get(module, [])
        return any(perm in role_permissions for perm in required_permissions)
    
    @staticmethod
    def get_accessible_modules(role: UserRole) -> List[str]:
        """Get list of all modules accessible by a role"""
        modules = [
            'dashboard', 'batches', 'cube_tests', 'material_tests',
            'ncr', 'safety_nc', 'ptw', 'training', 'pour_activities',
            'labs', 'handovers', 'gate_register', 'analytics',
            'users', 'settings'
        ]
        
        return [
            module for module in modules
            if RBACManager.can_access_module(role, module)
        ]


# Role Display Names (Multi-language ready)
ROLE_DISPLAY_NAMES = {
    UserRole.SYSTEM_ADMIN: "System Administrator",
    UserRole.PROJECT_MANAGER: "Project Manager",
    UserRole.QUALITY_MANAGER: "Quality Manager",
    UserRole.SAFETY_MANAGER: "Safety Manager",
    UserRole.QUALITY_ENGINEER: "Quality Engineer",
    UserRole.SAFETY_ENGINEER: "Safety Engineer",
    UserRole.BUILDING_ENGINEER: "Building Engineer / Site Engineer",
    UserRole.CONTRACTOR_SUPERVISOR: "Contractor Supervisor / Foreman",
    UserRole.WATCHMAN: "Watchman / Security Guard",
    UserRole.CLIENT: "Client / Owner Representative",
    UserRole.AUDITOR: "Auditor / Inspector",
    UserRole.SUPPLIER: "Supplier / Vendor",
}

# Role Descriptions
ROLE_DESCRIPTIONS = {
    UserRole.SYSTEM_ADMIN: "Full system access, user management, system configuration",
    UserRole.PROJECT_MANAGER: "Project oversight, team coordination, approvals",
    UserRole.QUALITY_MANAGER: "Quality system oversight, NCR approvals, team management",
    UserRole.SAFETY_MANAGER: "Safety system oversight, PTW approvals, team management",
    UserRole.QUALITY_ENGINEER: "Quality testing, batch recording, NCR creation",
    UserRole.SAFETY_ENGINEER: "Safety inspections, PTW issuance, incident reporting",
    UserRole.BUILDING_ENGINEER: "Site execution, pour activities, material coordination",
    UserRole.CONTRACTOR_SUPERVISOR: "Crew supervision, task execution, progress reporting",
    UserRole.WATCHMAN: "Gate operations, vehicle logging, security incidents",
    UserRole.CLIENT: "View-only access to project progress and reports",
    UserRole.AUDITOR: "View-only access for compliance audits",
    UserRole.SUPPLIER: "Limited access for deliveries and certificates",
}


def get_role_from_string(role_str: str) -> UserRole:
    """Convert string to UserRole enum"""
    try:
        return UserRole(role_str)
    except ValueError:
        # Default to lowest permission role
        return UserRole.WATCHMAN


def get_user_roles_list() -> List[Dict[str, str]]:
    """Get list of all roles with display names and descriptions"""
    return [
        {
            "value": role.value,
            "label": ROLE_DISPLAY_NAMES[role],
            "description": ROLE_DESCRIPTIONS[role]
        }
        for role in UserRole
    ]
