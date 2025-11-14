# Platform-Specific Notes

## Windows

### Running the Application
- Double-click `start_standalone.bat` for the easiest launch
- Or double-click `pokedex_standalone.py` (if Python is associated with .py files)
- The application will open in a native window

### Requirements
- Python 3.7 or higher
- Windows 10 or later recommended
- pywebview uses Edge WebView2 (automatically installed with Windows 10/11) or falls back to MSHTML

### Troubleshooting
- If double-clicking doesn't work, run from Command Prompt:
  ```cmd
  python pokedex_standalone.py
  ```
- If you get "Python not found", add Python to your PATH or use the full path to python.exe

## macOS

### Running the Application
- **Easiest:** Double-click `start_standalone.command`
- **Alternative:** Double-click `pokedex_standalone.py` (may require setting Python as default)
- **Terminal:** Run `./start_standalone.sh` or `python3 pokedex_standalone.py`

### First-Time Setup
1. If you get a security warning when double-clicking:
   - Right-click the file → Open → Click "Open" in the dialog
   - Or go to System Preferences → Security & Privacy → Allow the app

2. Make scripts executable (if needed):
   ```bash
   chmod +x start_standalone.sh
   chmod +x start_standalone.command
   ```

### Requirements
- Python 3.7 or higher (usually pre-installed on macOS)
- Xcode Command Line Tools (install with: `xcode-select --install`)
- pywebview uses Cocoa/WebKit (built into macOS)

### Troubleshooting
- If Python 3 is not found, try `python3` instead of `python`
- If you get permission errors, make the script executable:
  ```bash
  chmod +x start_standalone.sh
  ```
- For .command files, ensure they have execute permissions:
  ```bash
  chmod +x start_standalone.command
  ```

## Linux

### Running the Application
- Run `./start_standalone.sh` in Terminal
- Or run `python3 pokedex_standalone.py`

### Requirements
- Python 3.7 or higher
- GTK3 or Qt5 (for pywebview)
- Install dependencies:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk python3-dev
  
  # Fedora
  sudo dnf install python3-tkinter python3-devel
  ```

### Troubleshooting
- Make scripts executable:
  ```bash
  chmod +x start_standalone.sh
  ```
- If webview doesn't work, install GTK:
  ```bash
  sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
  ```

## Cross-Platform Notes

### All Platforms
- The standalone application automatically detects your platform
- All processes are properly cleaned up when you close the window
- No browser is required - it runs in a native window
- First run may take a moment to install dependencies

### Building Standalone Executables
- **Windows:** Run `python build_standalone.py` to create a `.exe` file
- **macOS:** Run `python3 build_standalone.py` to create a macOS app bundle
- **Linux:** Run `python3 build_standalone.py` to create a Linux executable

### Port Conflicts
- The application uses port 5000 by default
- If port 5000 is in use, you'll need to modify `pokedex_standalone.py` to use a different port
- The application will automatically find an available port if 5000 is busy (future enhancement)

