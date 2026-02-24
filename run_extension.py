"""
Script to run the CopySpell AI Extension Service on port 5001
"""
import subprocess
import sys
import os

def run_extension_service():
    """Run the extension service"""
    print("Starting CopySpell AI Extension Service on port 5001...")
    print("Access the service at: http://localhost:5001")
    print("API endpoint: POST /api/extend")
    
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # Import and run the extension service
        from extension_service import app
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nExtension service stopped.")
    except Exception as e:
        print(f"Error running extension service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_extension_service()