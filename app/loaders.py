from pathlib import Path
import streamlit as st
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POKEMON_CSV = DATA_DIR / "pokemon.csv"
DAMAGE_CSV = DATA_DIR / "damage_relations.csv"


@st.cache_data
def load_pokemon_data():
    """Load Pokémon data and merge in damage relations."""
    if not POKEMON_CSV.exists():
        return pd.DataFrame()

    # Read Pokémon CSV as strings (safe), then fix numeric columns
    poke_df = pd.read_csv(POKEMON_CSV, dtype=str)

    if "id" not in poke_df.columns:
        # Hard fail if header is still wrong
        raise RuntimeError("pokemon.csv is missing 'id' column. Check header line.")

    # Cast id to int for proper sorting
    poke_df["id"] = poke_df["id"].astype(int)

    # Optionally cast generation to int if present
    if "generation" in poke_df.columns:
        with pd.option_context("mode.chained_assignment", None):
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
