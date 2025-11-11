#!/usr/bin/env python3
"""Fix JWT identity extraction in all API modules."""

import re

FILES_TO_FIX = [
    'server/cube_tests.py',
    'server/third_party_labs.py',
    'server/third_party_cube_tests.py',
    'server/material_management.py',
    'server/material_tests.py'
]

HELPER_FUNCTION = '''

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Extract user_id from JWT identity (supports both dict and int formats)."""
    identity = get_jwt_identity()
    return identity.get("user_id") if isinstance(identity, dict) else identity

'''

for filepath in FILES_TO_FIX:
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the Blueprint creation line
    blueprint_pattern = r'([a-z_]+_bp = Blueprint\([^\)]+\))'
    
    # Check if helper function already exists
    if 'def get_current_user_id():' not in content:
        # Add helper function after blueprint
        content = re.sub(
            blueprint_pattern,
            r'\1' + HELPER_FUNCTION,
            content
        )
    
    # Replace all user_id = get_jwt_identity() with get_current_user_id()
    content = content.replace(
        'user_id = get_jwt_identity()',
        'user_id = get_current_user_id()'
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed {filepath}")

print("\n✅ All files fixed!")
