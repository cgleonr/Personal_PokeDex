#!/usr/bin/env python3
"""
Build a standalone executable using PyInstaller.
This creates a single .exe file that can run without Python installed.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the standalone executable."""
    print("=" * 50)
    print("Building Standalone Pokédex Executable")
    print("=" * 50)
    print()
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()
        print()
    
    # Get the current directory
    script_dir = Path(__file__).resolve().parent
    
    # Determine path separator for PyInstaller
    if sys.platform == 'win32':
        path_sep = ';'
        console_flag = "--console"
        exe_ext = ".exe"
        exe_name = "Pokédex.exe"
    else:
        path_sep = ':'
        console_flag = "--windowed"
        exe_ext = ""
        exe_name = "Pokédex"
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name=Pokédex",
        "--onefile",
        console_flag,
        f"--add-data=data{path_sep}data",  # Include data directory
        f"--add-data=static{path_sep}static",  # Include static directory
        "--hidden-import=flask",
        "pokedex_standalone.py"
    ]
    
    # Add icon if available (optional)
    icon_path = script_dir / "icon.ico" if sys.platform == 'win32' else script_dir / "icon.icns"
    if icon_path.exists():
        cmd.insert(-1, f"--icon={icon_path}")
    
    print("Running PyInstaller...")
    print("This may take a few minutes...")
    print()
    
    try:
        subprocess.check_call(cmd, cwd=script_dir)
        print()
        print("=" * 50)
        print("Build Complete!")
        print("=" * 50)
        print()
        exe_path = script_dir / 'dist' / exe_name
        print(f"Executable location: {exe_path}")
        print()
        if sys.platform == 'win32':
            print("You can now distribute this .exe file to others!")
        else:
            print("You can now distribute this executable to others!")
        print("They don't need Python installed to run it.")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_executable()

