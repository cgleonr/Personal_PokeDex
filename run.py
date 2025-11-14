#!/usr/bin/env python3
"""
Simple script to run the Pokédex Flask application.
Automatically opens the browser when the server starts.
"""

import webbrowser
import threading
import time
from app import app

def open_browser():
    """Wait a moment for the server to start, then open the browser."""
    time.sleep(1.5)  # Give the server time to start
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("=" * 50)
    print("Personal Pokédex - Starting Server")
    print("=" * 50)
    print("\nOpening browser automatically...")
    print("Press Ctrl+C to stop the server\n")
    
    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)

