#!/usr/bin/env python3
"""
Standalone Pokédex Application
Runs Flask in the background and opens the system browser.
"""

import sys
import threading
import time
import atexit
import signal
import os
import webbrowser
from pathlib import Path
from werkzeug.serving import make_server

# Import Flask app
from app import app

# Global variables for cleanup
server_thread = None
http_server = None
shutdown_event = threading.Event()
server_port = 5000

def start_flask_server(port=5000):
    """Start Flask server in a separate thread with proper shutdown handling."""
    global http_server, shutdown_event, server_port
    
    try:
        # Create a proper WSGI server that we can shut down
        http_server = make_server('127.0.0.1', port, app, threaded=True)
        
        # Run the server until shutdown is requested
        http_server.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            new_port = port + 1
            print(f"Port {port} is already in use. Trying port {new_port}...")
            # Update global port
            server_port = new_port
            # Try next port
            try:
                http_server = make_server('127.0.0.1', new_port, app, threaded=True)
                http_server.serve_forever()
            except Exception as e2:
                print(f"Error starting server on port {new_port}: {e2}")
                raise
        else:
            raise
    except Exception as e:
        print(f"Error in Flask server: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Flask server stopped")

def wait_for_server(port=5000, max_wait=10):
    """Wait for Flask server to be ready."""
    import urllib.request
    import urllib.error
    
    for i in range(max_wait * 10):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}', timeout=0.1)
            return port
        except (urllib.error.URLError, OSError):
            # Try next port if current one fails
            if i > 5:  # After a few attempts, try next port
                try:
                    urllib.request.urlopen(f'http://127.0.0.1:{port + 1}', timeout=0.1)
                    return port + 1
                except:
                    pass
            time.sleep(0.1)
    return None

def cleanup():
    """Clean up all processes and threads."""
    global server_thread, http_server, shutdown_event
    
    print("\nCleaning up...")
    
    # Shutdown Flask server gracefully
    if http_server:
        try:
            print("Stopping Flask server...")
            http_server.shutdown()
            http_server.server_close()
        except Exception as e:
            print(f"Error shutting down server: {e}")
    
    # Wait for server thread to finish (with timeout)
    if server_thread and server_thread.is_alive():
        # print("Waiting for server thread to finish...")
        server_thread.join(timeout=1.0)
    
    shutdown_event.set()

def main():
    """Main application entry point."""
    global server_thread, server_port
    
    try:
        print("=" * 50)
        print("Personal Pokédex - Standalone Application")
        print("=" * 50)
        print()
        
        # Check if data files exist
        data_dir = Path(__file__).resolve().parent / "data"
        pokemon_csv = data_dir / "pokemon.csv"
        
        if not pokemon_csv.exists():
            print("ERROR: Pokemon data not found!")
            print(f"Expected: {pokemon_csv}")
            print("\nPlease make sure the data files are in the 'data' directory.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Register cleanup handlers
        atexit.register(cleanup)
        
        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            print("\nShutting down...")
            cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start Flask server in background thread
        print("Starting Flask server...")
        server_thread = threading.Thread(target=start_flask_server, args=(server_port,), daemon=True)
        server_thread.start()
        
        # Wait for server to be ready
        print("Waiting for server to start...")
        actual_port = wait_for_server(server_port)
        
        if actual_port is None:
            print("ERROR: Server failed to start!")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        if actual_port != server_port:
            server_port = actual_port
        
        print(f"Server running at http://127.0.0.1:{server_port}")
        print("Opening in your default browser...")
        
        # Open browser
        webbrowser.open(f'http://127.0.0.1:{server_port}')
        
        print()
        print("=" * 50)
        print("APP IS RUNNING")
        print("=" * 50)
        print("Do not close this window while using the app.")
        print("Press Ctrl+C or close this window to stop the server.")
        print("=" * 50)
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == '__main__':
    main()

