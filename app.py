from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import csv
import json
import random

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

DATA_DIR = Path(__file__).resolve().parent / "data"
POKEMON_CSV = DATA_DIR / "pokemon.csv"
DAMAGE_CSV = DATA_DIR / "damage_relations.csv"

def load_pokemon_data():
    """Load Pokémon data and merge in damage relations using standard csv module."""
    if not POKEMON_CSV.exists():
        return []

    pokemon_list = []
    
    # Read Pokemon Data
    with open(POKEMON_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Type conversion
            try:
                row['id'] = int(row['id'])
            except (ValueError, TypeError):
                continue # Skip invalid rows
                
            if 'generation' in row and row['generation']:
                try:
                    row['generation'] = int(row['generation'])
                except ValueError:
                    row['generation'] = None
            
            # Handle numeric fields that might be empty strings
            for field in ['height_m', 'weight_kg']:
                if field in row and row[field]:
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        row[field] = None
                else:
                    row[field] = None

            # Handle stats
            for field in ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'base_stat_total']:
                if field in row and row[field]:
                    try:
                        row[field] = int(row[field])
                    except ValueError:
                        row[field] = None
                else:
                    row[field] = None
            
            # Handle booleans
            for field in ['is_legendary', 'is_mythical']:
                if field in row:
                    try:
                        row[field] = bool(int(row[field]))
                    except ValueError:
                        row[field] = False

            pokemon_list.append(row)

    # Read Damage Relations
    damage_map = {}
    if DAMAGE_CSV.exists():
        with open(DAMAGE_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    p_id = int(row['id'])
                    # Keep only relevant columns
                    damage_map[p_id] = {
                        "double_damage_from": row.get("double_damage_from", ""),
                        "half_damage_from": row.get("half_damage_from", ""),
                        "no_damage_from": row.get("no_damage_from", "")
                    }
                except (ValueError, TypeError):
                    continue

    # Merge Data
    for p in pokemon_list:
        p_id = p['id']
        if p_id in damage_map:
            p.update(damage_map[p_id])
        else:
            p["double_damage_from"] = ""
            p["half_damage_from"] = ""
            p["no_damage_from"] = ""

    # Sort by ID
    pokemon_list.sort(key=lambda x: x['id'])
    
    return pokemon_list

# Cache the data
pokemon_data = None

def get_pokemon_list():
    global pokemon_data
    if pokemon_data is None:
        pokemon_data = load_pokemon_data()
    return pokemon_data

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/pokemon')
def get_all_pokemon():
    """Get all Pokémon data."""
    data = get_pokemon_list()
    return jsonify(data)

@app.route('/api/pokemon/<int:pokemon_id>')
def get_pokemon_by_id(pokemon_id):
    """Get a specific Pokémon by ID."""
    data = get_pokemon_list()
    # Binary search could be faster but linear is fine for < 2000 items
    for p in data:
        if p['id'] == pokemon_id:
            return jsonify(p)
    
    return jsonify({'error': 'Pokémon not found'}), 404

@app.route('/api/pokemon/search/<query>')
def search_pokemon(query):
    """Search Pokémon by name or ID."""
    data = get_pokemon_list()
    query_lower = query.lower().strip()
    
    results = []
    for p in data:
        name_match = query_lower in p['name'].lower()
        id_match = query_lower in str(p['id'])
        if name_match or id_match:
            results.append(p)
    
    return jsonify(results)

@app.route('/api/pokemon/random/<int:count>')
def get_random_pokemon(count):
    """Get random Pokémon."""
    data = get_pokemon_list()
    if not data:
        return jsonify([])
    
    count = min(count, len(data))
    random_pokemon = random.sample(data, count)
    return jsonify(random_pokemon)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
