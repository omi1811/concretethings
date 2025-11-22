import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import server.models...")
    import server.models
    print("Success importing server.models")
    
    print("Attempting to import server.pour_activities...")
    import server.pour_activities
    print("Success importing server.pour_activities")
    
except Exception as e:
    import traceback
    print(f"Import failed: {e}")
    print(traceback.format_exc())
