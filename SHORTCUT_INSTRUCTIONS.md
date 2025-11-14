# How to Create a Desktop Shortcut

## Option 1: Standalone Application (Recommended)

**Best for desktop use - runs in its own window, no browser needed!**

1. **Right-click** on `start_standalone.bat` or `pokedex_standalone.py`
2. Select **"Create shortcut"**
3. **Right-click** the shortcut and select **"Properties"**
4. In the **"Shortcut"** tab, you can:
   - Change the icon (click "Change Icon")
   - Rename it to "Pokédex" or whatever you prefer
5. **Drag** the shortcut to your Desktop or Start Menu

Now you can double-click the shortcut to launch the Pokédex in a standalone window!

## Option 2: Browser Version

1. **Right-click** on `start_pokedex.bat`
2. Select **"Create shortcut"**
3. **Right-click** the shortcut and select **"Properties"**
4. In the **"Shortcut"** tab, you can:
   - Change the icon (click "Change Icon")
   - Rename it to "Pokédex" or whatever you prefer
5. **Drag** the shortcut to your Desktop or Start Menu

Now you can double-click the shortcut to launch the Pokédex in your browser!

## Option 3: Create a Custom Shortcut

1. **Right-click** on your Desktop
2. Select **"New" → "Shortcut"**
3. For the location, enter one of these:
   
   **Standalone version:**
   ```
   python.exe "C:\Users\carlo\OneDrive\Desktop\Personal Projects\Personal_Pokedex_Cursor\pokedex_standalone.py"
   ```
   
   **Browser version:**
   ```
   python.exe "C:\Users\carlo\OneDrive\Desktop\Personal Projects\Personal_Pokedex_Cursor\launch_pokedex.py"
   ```
   
   (Adjust the path to match your actual location)
4. Click **"Next"** and name it "Pokédex"
5. Click **"Finish"**

## Notes

### Standalone Version:
- Opens in its own window (no browser needed)
- All processes close automatically when you close the window
- Perfect for desktop use
- No command window visible (runs in background)

### Browser Version:
- Opens in your default browser
- Keep the command window open while using the Pokédex
- To stop the server, close the command window or press Ctrl+C

### Both Versions:
- The first time you run it, it may take a moment to install dependencies
- All processes are properly cleaned up when the application closes

