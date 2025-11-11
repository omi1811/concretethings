#!/usr/bin/env python3
"""Direct database test - no HTTP needed."""
from server.db import session_scope
from server.models import MixDesign

def test_database():
    """Check the database has data."""
    with session_scope() as session:
        designs = session.query(MixDesign).all()
        print(f"✓ Database contains {len(designs)} mix design(s)")
        
        if designs:
            print("\nSample data:")
            for design in designs[:3]:
                print(f"  • {design.project_name} ({design.mix_design_id}) - {design.specified_strength_psi} PSI")
        
        return len(designs) > 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_database() else 1)
