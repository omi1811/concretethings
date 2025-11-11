#!/usr/bin/env python3
"""Quick test script to verify the API works."""
import requests
import json

def test_api():
    """Test the Mix Design API."""
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test GET /api/mix-designs
        response = requests.get(f"{base_url}/api/mix-designs", timeout=5)
        response.raise_for_status()
        designs = response.json()
        
        print(f"✓ API is working!")
        print(f"✓ Found {len(designs)} mix design(s) in database")
        
        if designs:
            print("\nSample mix design:")
            first = designs[0]
            print(f"  - Project: {first['projectName']}")
            print(f"  - Mix ID: {first['mixDesignId']}")
            print(f"  - Strength: {first['specifiedStrengthPsi']} PSI")
            print(f"  - Slump: {first['slumpInches']} inches")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = test_api()
    sys.exit(0 if success else 1)
