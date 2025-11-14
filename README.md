# Personal PokeDex

I hope nintendo doesn't come after me for this one.

## What is this??

"Personal PokeDex" Aims to emulate the pokedex found in (as far as I can remember) the original Pokemon show. The goal is to be able to look up all the information about all the released pokemon, and display it in a friendly way. This also includes type strengths and weaknesses, information that I myself usually tend to look for when heading into battles underlevelled :thumbsup:.

## What does it look like?
| Landing Page    | Sample Main Page | Sample Details Page |
|-----------------|------------------|---------------------|
| ![landing page](/img/landing_page.png) | ![rayquaza_main](/img/rayquaza_1.png) | ![rayquaza_details](/img/rayquaza_2.png)
## How do I get it to work?

### Prerequisites
- **Python 3.7 or higher** (works on Windows, macOS, and Linux)
- **pip** (Python package manager - usually included with Python)
- **macOS users:** May need to install Xcode Command Line Tools: `xcode-select --install`

### Installation & Running

1. **Install dependencies:**
After cloning the repository:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**   
   **Standalone Application (Under Development, use web app for now):**
   >**_Use the web app for now, desktop app is under active development_**
   **Windows:**
   - Double-click `start_standalone.bat` or `pokedex_standalone.py`
   
   **macOS:**
   - Double-click `start_standalone.command` (or `start_standalone.sh` in Terminal)
   - Or double-click `pokedex_standalone.py`
   - First time: Right-click → Open With → Python Launcher (if double-click doesn't work)
   
   **Features:**
   - Opens in a native window (no browser needed)
   - All processes close automatically when you close the window
   - Works on both Windows and macOS!
   - Perfect for desktop use!
   
   **Web Browser Version:**
   >**_Current working version_**
   
   **Windows:**
   - Double-click `start_pokedex.bat` or `launch_pokedex.py`
   
   **macOS:**
   - Double-click `launch_pokedex.py` or run in Terminal
   
   **Features:**
   - Opens in your default browser
   - The browser will open automatically!
   
   **Command Line (All Platforms):**
   ```bash
   # Standalone version
   python pokedex_standalone.py
   # or
   python3 pokedex_standalone.py
   
   # Browser version
   python run.py
   # or
   python3 run.py
   ```
   
   **Create a Desktop Shortcut:**
   - See `SHORTCUT_INSTRUCTIONS.md` for detailed instructions
   - **Windows:** Right-click `start_standalone.bat` → Create shortcut → Drag to Desktop
   - **macOS:** Right-click `start_standalone.command` → Make Alias → Drag to Desktop

3. **That's it!**
   - Standalone version: A window opens with your Pokédex!
   - Browser version: Your browser opens automatically!

### Features

- **Search**: Search for any Pokémon by name or ID
- **Detailed View**: View comprehensive information about each Pokémon including:
  - Base stats with visual bars
  - Type information
  - Evolution chains
  - Damage relations (weaknesses, resistances, immunities)
  - Pokédex entries
- **Navigation**: Use the D-pad buttons to navigate between Pokémon
- **Classic Design**: Styled to look like the original Pokédex device from the anime













## Future Features
___
[ ] Pokemon Tracking - keep track of what Pokemon you've already caught
 - [ ] Generational/Game Tracking - Be able to keep track of which games you've caught them in


## Credits
- All data has been sourced from [PokeAPI](https://pokeapi.co)