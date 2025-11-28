# Personal PokeDex

A standalone Pokedex application that runs in your local browser, styled after the original device.

![landing page](/img/landing_page.png)

## Quick Start

### Option 1: Standalone Executable (Recommended)
No Python installation required!

1.  Go to the `dist` folder.
2.  Double-click `Pokédex.exe`.
3.  A black console window will open (this is the server), and your default browser will open the app.
4.  **To close:** Simply close the console window.

### Option 2: Run from Source

**Prerequisites:**
- Python 3.7+
- pip

**Installation:**
```bash
pip install -r requirements.txt
```

**Running:**
```bash
python pokedex_standalone.py
```

## Creating a Desktop Shortcut

For easy access to the standalone executable:

1.  Navigate to the `dist` folder.
2.  Right-click `Pokédex.exe`.
3.  Select **Show more options** (Windows 11) -> **Send to** -> **Desktop (create shortcut)**.
4.  (Optional) Rename the shortcut on your desktop to "Pokédex".

## Features

- **Search**: Find Pokémon by name or ID.
- **Detailed Stats**: View base stats, types, and evolution chains.
- **Damage Relations**: See weaknesses, resistances, and immunities.
- **Classic Design**: Authentic retro aesthetic.

## Credits
- Data sourced from [PokeAPI](https://pokeapi.co).