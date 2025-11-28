#!/usr/bin/env python3
"""
Launcher script for Personal Pokédex.
This script can be double-clicked or run directly to start the app.
"""

import sys
import os
import subprocess
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        import flask_cors
        import pandas
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies")
        return False

def open_browser():
    """Wait for server to start, then open browser."""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main launcher function."""
    print("=" * 50)
    print("Personal Pokédex Launcher")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("ERROR: app.py not found!")
        print("Please run this script from the project directory.")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("Required packages not found.")
        response = input("Install dependencies now? (y/n): ").lower()
        if response == 'y':
            if not install_dependencies():
                input("Press Enter to exit...")
                return
        else:
            print("Cannot start without required packages.")
            input("Press Enter to exit...")
            return
    
    # Start browser opener in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Import and run the app
    print("Starting Pokédex server...")
    print("Browser will open automatically...")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    except Exception as e:
        print(f"\nERROR: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()

