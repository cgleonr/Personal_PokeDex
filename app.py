from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import pandas as pd
import json

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

DATA_DIR = Path(__file__).resolve().parent / "data"
POKEMON_CSV = DATA_DIR / "pokemon.csv"
DAMAGE_CSV = DATA_DIR / "damage_relations.csv"

def load_pokemon_data():
    """Load Pokémon data and merge in damage relations."""
    if not POKEMON_CSV.exists():
        return pd.DataFrame()

    # Read Pokémon CSV as strings (safe), then fix numeric columns
    poke_df = pd.read_csv(POKEMON_CSV, dtype=str)

    if "id" not in poke_df.columns:
        raise RuntimeError("pokemon.csv is missing 'id' column. Check header line.")

    # Cast id to int for proper sorting
    poke_df["id"] = poke_df["id"].astype(int)

    # Optionally cast generation to int if present
    if "generation" in poke_df.columns:
        poke_df["generation"] = pd.to_numeric(poke_df["generation"], errors="coerce")

    # Merge in damage relations if file exists
    if DAMAGE_CSV.exists():
        dmg_df = pd.read_csv(DAMAGE_CSV, dtype=str)

        if "id" not in dmg_df.columns:
            raise RuntimeError("damage_relations.csv is missing 'id' column. Check header line.")

        dmg_df["id"] = dmg_df["id"].astype(int)

        # We only care about damage TO this Pokémon
        cols = ["id", "double_damage_from", "half_damage_from", "no_damage_from"]
        dmg_df = dmg_df[cols]

        # Merge on id
        df = poke_df.merge(dmg_df, on="id", how="left")
    else:
        # If damage file is missing, just add empty columns
        df = poke_df.copy()
        df["double_damage_from"] = ""
        df["half_damage_from"] = ""
        df["no_damage_from"] = ""

    # Make sure missing damage fields are empty strings, not NaN
    df["double_damage_from"] = df["double_damage_from"].fillna("")
    df["half_damage_from"] = df["half_damage_from"].fillna("")
    df["no_damage_from"] = df["no_damage_from"].fillna("")

    # Sort by id
    df = df.sort_values("id").reset_index(drop=True)

    return df

# Cache the data
pokemon_df = None

def get_pokemon_df():
    global pokemon_df
    if pokemon_df is None:
        pokemon_df = load_pokemon_data()
    return pokemon_df

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/pokemon')
def get_all_pokemon():
    """Get all Pokémon data."""
    df = get_pokemon_df()
    if df.empty:
        return jsonify([])
    
    # Convert to list of dicts
    pokemon_list = df.to_dict('records')
    # Convert NaN to None for JSON serialization
    for pokemon in pokemon_list:
        for key, value in pokemon.items():
            if pd.isna(value):
                pokemon[key] = None
            elif isinstance(value, float) and pd.isna(value):
                pokemon[key] = None
    
    return jsonify(pokemon_list)

@app.route('/api/pokemon/<int:pokemon_id>')
def get_pokemon_by_id(pokemon_id):
    """Get a specific Pokémon by ID."""
    df = get_pokemon_df()
    pokemon = df[df['id'] == pokemon_id]
    
    if pokemon.empty:
        return jsonify({'error': 'Pokémon not found'}), 404
    
    result = pokemon.iloc[0].to_dict()
    # Convert NaN to None
    for key, value in result.items():
        if pd.isna(value):
            result[key] = None
    
    return jsonify(result)

@app.route('/api/pokemon/search/<query>')
def search_pokemon(query):
    """Search Pokémon by name or ID."""
    df = get_pokemon_df()
    query_lower = query.lower().strip()
    
    results = df[
        df["name"].str.contains(query_lower, case=False, na=False) |
        df["id"].astype(str).str.contains(query_lower, na=False)
    ]
    
    if results.empty:
        return jsonify([])
    
    pokemon_list = results.to_dict('records')
    # Convert NaN to None
    for pokemon in pokemon_list:
        for key, value in pokemon.items():
            if pd.isna(value):
                pokemon[key] = None
    
    return jsonify(pokemon_list)

@app.route('/api/pokemon/random/<int:count>')
def get_random_pokemon(count):
    """Get random Pokémon."""
    df = get_pokemon_df()
    if df.empty:
        return jsonify([])
    
    random_pokemon = df.sample(min(count, len(df)))
    pokemon_list = random_pokemon.to_dict('records')
    
    # Convert NaN to None
    for pokemon in pokemon_list:
        for key, value in pokemon.items():
            if pd.isna(value):
                pokemon[key] = None
    
    return jsonify(pokemon_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

