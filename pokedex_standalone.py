#!/usr/bin/env python3
"""
Standalone Pokédex Application
Runs Flask in the background and displays in a native window.
All processes are cleaned up when the window is closed.
"""

import sys
import threading
import time
import atexit
import signal
import os
from pathlib import Path

# Import Flask app
from app import app
from werkzeug.serving import make_server

# Try to import webview, install if not available
try:
    import webview
except ImportError:
    print("pywebview not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
    import webview

# Global variables for cleanup
server_thread = None
http_server = None
window = None
shutdown_event = threading.Event()
server_port = 5000  # Default port, may change if port is in use

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
    
    print("Cleaning up...")
    
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
        print("Waiting for server thread to finish...")
        server_thread.join(timeout=2.0)
        if server_thread.is_alive():
            print("Warning: Server thread did not stop gracefully")
    
    shutdown_event.set()

# on_closed callback removed - pywebview doesn't support it as a parameter
# Cleanup will happen in the finally block when webview.start() returns

def main():
    """Main application entry point."""
    global server_thread, window
    
    try:
        print("=" * 50)
        print("Personal Pokédex - Standalone Application")
        print("=" * 50)
        print()
        
        # Check if data files exist
        data_dir = Path(__file__).resolve().parent / "data"
        pokemon_csv = data_dir / "pokemon.csv"
        
        print(f"Checking for data files in: {data_dir}")
        if not pokemon_csv.exists():
            print("ERROR: Pokemon data not found!")
            print(f"Expected: {pokemon_csv}")
            print("\nPlease make sure the data files are in the 'data' directory.")
            # Only wait for input if running in a terminal (not when double-clicked)
            if sys.stdin.isatty():
                try:
                    input("Press Enter to exit...")
                except (EOFError, KeyboardInterrupt):
                    pass
            sys.exit(1)
        
        print("Data files found!")
        print()
    
        # Register cleanup handlers
        atexit.register(cleanup)
        
        # Handle Ctrl+C gracefully (works on both Windows and Unix-like systems)
        def signal_handler(sig, frame):
            print("\nShutting down...")
            cleanup()
            sys.exit(0)
        
        # Register signal handlers for graceful shutdown
        if sys.platform == 'win32':
            # Windows
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        else:
            # macOS and Linux
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        
        # Start Flask server in background thread
        print("Starting Flask server...")
        global server_port
        server_thread = threading.Thread(target=start_flask_server, args=(server_port,), daemon=True)
        server_thread.start()
        
        # Wait for server to be ready
        print("Waiting for server to start...")
        actual_port = wait_for_server(server_port)
        if actual_port is None:
            print("ERROR: Server failed to start!")
            print("This might be due to:")
            print("  - Port 5000 and 5001 are both in use")
            print("  - Firewall blocking the connection")
            print("  - Another application using the port")
            if sys.stdin.isatty():
                try:
                    input("\nPress Enter to exit...")
                except (EOFError, KeyboardInterrupt):
                    pass
            sys.exit(1)
        
        if actual_port != server_port:
            print(f"Note: Using port {actual_port} instead of {server_port}")
            server_port = actual_port
        
        print("Server ready!")
        print("Opening Pokédex window...")
        print("Close the window to exit the application.")
        print()
        
        # Create and show the webview window
        try:
            # Platform-specific window settings
            window_kwargs = {
                'title': 'Personal Pokédex',
                'url': f'http://127.0.0.1:{server_port}',
                'width': 1200,
                'height': 800,
                'min_size': (800, 600),
                'resizable': True,
                'fullscreen': False
            }
            
            # macOS-specific settings
            if sys.platform == 'darwin':
                window_kwargs['on_top'] = False
                # macOS uses Cocoa, which handles window management differently
            else:
                # Windows and Linux
                window_kwargs['on_top'] = False
            
            print("Creating window...")
            window = webview.create_window(**window_kwargs)
            
            print("Starting webview...")
            print("(Window will open shortly...)")
            # Start webview (this blocks until window is closed)
            # On macOS, this uses Cocoa/WebKit
            # On Windows, this uses Edge WebView2 or MSHTML
            # When the window is closed, webview.start() will return
            webview.start(debug=False)
            
            # This code runs after the window is closed
            print("Window closed. Shutting down...")
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            cleanup()
        except ImportError as e:
            print(f"\nERROR: Import error - {e}")
            print("This usually means a required package is missing.")
            print("Try running: pip install -r requirements.txt")
            import traceback
            traceback.print_exc()
            if sys.stdin.isatty():
                try:
                    input("\nPress Enter to exit...")
                except (EOFError, KeyboardInterrupt):
                    pass
            sys.exit(1)
        except Exception as e:
            print(f"\nERROR: {e}")
            print("\nFull error details:")
            import traceback
            traceback.print_exc()
            cleanup()
            if sys.stdin.isatty():
                try:
                    input("\nPress Enter to exit...")
                except (EOFError, KeyboardInterrupt):
                    pass
            sys.exit(1)
        finally:
            # Final cleanup
            cleanup()
            print("Application closed.")
            # Force exit to ensure all threads are terminated
            os._exit(0)
    
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        if sys.stdin.isatty():
            try:
                input("\nPress Enter to exit...")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)

if __name__ == '__main__':
    main()

