"""
Script to run the Streamlit GRI Extractor application.
"""

import subprocess
import sys
import os

def run_streamlit_app():
    """Run the Streamlit application."""
    try:
        # Change to the directory containing the app
        app_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(app_dir)
        
        print("🚀 Starting GRI Extractor Streamlit App...")
        print("📊 Opening in your default browser...")
        print("🛑 Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"]
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit app: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_streamlit_app()
