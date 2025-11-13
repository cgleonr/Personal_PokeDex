#!/usr/bin/env python3
"""
Fetch Pokémon data from PokeAPI and build CSV files for the Pokédex app.

Outputs (relative to project root):
- data/pokemon.csv
- data/damage_relations.csv

Place this file at: scripts/fetch_data.py
"""

import csv
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from functools import lru_cache

import requests


BASE_URL = "https://pokeapi.co/api/v2"
# Basic, polite rate limiting to avoid hammering PokeAPI
REQUEST_DELAY_SECONDS = 0.15  # tweak if you hit rate limits

# For local debugging you can limit how many species to fetch
MAX_SPECIES: Optional[int] = None  # e.g. 151 for Gen 1 only, or None for all


# --------------------------
# HTTP helpers + caching
# --------------------------

def get_json(url: str) -> Dict[str, Any]:
    """GET JSON with simple retry logic and polite delay."""
    for attempt in range(3):
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching {url} (attempt {attempt + 1}/3): {e}")
            if attempt == 2:
                raise
            time.sleep(1.0)


@lru_cache(maxsize=None)
def get_pokemon(name_or_id: str) -> Dict[str, Any]:
    return get_json(f"{BASE_URL}/pokemon/{name_or_id}")


@lru_cache(maxsize=None)
def get_species(name_or_id: str) -> Dict[str, Any]:
    return get_json(f"{BASE_URL}/pokemon-species/{name_or_id}")


@lru_cache(maxsize=None)
def get_evolution_chain(chain_id: int) -> Dict[str, Any]:
    return get_json(f"{BASE_URL}/evolution-chain/{chain_id}")


@lru_cache(maxsize=None)
def get_type(name_or_id: str) -> Dict[str, Any]:
    return get_json(f"{BASE_URL}/type/{name_or_id}")


# --------------------------
# Utility transformations
# --------------------------

def clean_flavor_text(species_data: Dict[str, Any]) -> str:
    """Return first English flavor text, cleaned into a single line."""
    entries = species_data.get("flavor_text_entries", [])
    for entry in entries:
        if entry.get("language", {}).get("name") == "en":
            text = entry.get("flavor_text", "")
            text = text.replace("\n", " ").replace("\f", " ")
            # Normalize spaces
            text = " ".join(text.split())
            return text
    return ""


def get_generation_number(species_data: Dict[str, Any]) -> int:
    """Extract generation number from 'generation-i', 'generation-ii', etc."""
    gen_name = species_data.get("generation", {}).get("name", "")
    # Expect format 'generation-i' ... 'generation-viii'
    if gen_name.startswith("generation-"):
        suffix = gen_name.split("generation-")[-1]
        roman_map = {
            "i": 1,
            "ii": 2,
            "iii": 3,
            "iv": 4,
            "v": 5,
            "vi": 6,
            "vii": 7,
            "viii": 8,
            "ix": 9,  # future-proof-ish
        }
        return roman_map.get(suffix, 0)
    return 0


def extract_sprites(pokemon_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract (official_artwork_url, sprite_url, icon_url) from Pokémon data.
    Fallbacks if some are missing.
    """
    sprites = pokemon_data.get("sprites", {}) or {}

    # Official artwork (high-res)
    official = (
        sprites.get("other", {})
        .get("official-artwork", {})
        .get("front_default")
    )

    # Main front sprite
    sprite = sprites.get("front_default")

    # Icon (small) - often in gen-viii icons, fallback to main sprite
    icon = (
        sprites.get("versions", {})
        .get("generation-viii", {})
        .get("icons", {})
        .get("front_default")
    )
    if icon is None:
        icon = sprite

    return official, sprite, icon


def convert_height_weight(pokemon_data: Dict[str, Any]) -> Tuple[float, float]:
    """
    Convert height (decimeters) -> meters, weight (hectograms) -> kg.
    """
    height_dm = pokemon_data.get("height", 0)
    weight_hg = pokemon_data.get("weight", 0)
    height_m = height_dm / 10.0 if height_dm is not None else 0.0
    weight_kg = weight_hg / 10.0 if weight_hg is not None else 0.0
    return height_m, weight_kg


def extract_types(pokemon_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Return primary and (optional) secondary type names."""
    types = sorted(
        pokemon_data.get("types", []),
        key=lambda t: t.get("slot", 0)
    )
    primary = types[0]["type"]["name"] if len(types) > 0 else None
    secondary = types[1]["type"]["name"] if len(types) > 1 else None
    return primary, secondary


# --------------------------
# Evolution chain handling
# --------------------------

def parse_chain_id_from_url(url: str) -> int:
    """
    evolution_chain URLs look like:
    https://pokeapi.co/api/v2/evolution-chain/1/
    """
    return int(str(url).rstrip("/").split("/")[-1])


def find_evolution_context(
    node: Dict[str, Any],
    target_species_name: str,
    parent: Optional[Dict[str, Any]] = None
) -> Optional[Tuple[Optional[Dict[str, Any]], Dict[str, Any]]]:
    """
    DFS over evolution chain JSON.
    Returns (parent_node, current_node) when species.name == target.
    """
    current_name = node.get("species", {}).get("name")
    if current_name == target_species_name:
        return parent, node

    for child in node.get("evolves_to", []):
        result = find_evolution_context(child, target_species_name, node)
        if result is not None:
            return result

    return None


def parse_evolution_conditions(detail: Dict[str, Any]) -> List[str]:
    """
    Convert an evolution_details entry into a list of 'key:value' conditions,
    e.g. ['trigger:level-up', 'level:16', 'time:day', 'use_item:fire-stone']
    """
    conds = []

    trigger = detail.get("trigger", {}).get("name")
    if trigger:
        conds.append(f"trigger:{trigger}")

    min_level = detail.get("min_level")
    if min_level is not None:
        conds.append(f"level:{min_level}")

    item = detail.get("item", {})
    if item:
        conds.append(f"use_item:{item.get('name')}")

    held_item = detail.get("held_item", {})
    if held_item:
        conds.append(f"held_item:{held_item.get('name')}")

    time_of_day = detail.get("time_of_day")
    if time_of_day:
        conds.append(f"time:{time_of_day}")

    location = detail.get("location", {})
    if location:
        conds.append(f"location:{location.get('name')}")

    known_move = detail.get("known_move", {})
    if known_move:
        conds.append(f"known_move:{known_move.get('name')}")

    known_move_type = detail.get("known_move_type", {})
    if known_move_type:
        conds.append(f"known_move_type:{known_move_type.get('name')}")

    min_happiness = detail.get("min_happiness")
    if min_happiness is not None:
        conds.append(f"min_happiness:{min_happiness}")

    min_affection = detail.get("min_affection")
    if min_affection is not None:
        conds.append(f"min_affection:{min_affection}")

    min_beauty = detail.get("min_beauty")
    if min_beauty is not None:
        conds.append(f"min_beauty:{min_beauty}")

    gender = detail.get("gender")
    if gender is not None:
        conds.append(f"gender:{gender}")

    needs_overworld_rain = detail.get("needs_overworld_rain")
    if needs_overworld_rain:
        conds.append("needs_overworld_rain:true")

    relative_physical_stats = detail.get("relative_physical_stats")
    # -1, 0, 1 correspond to attack<def, attack=def, attack>def
    if relative_physical_stats is not None:
        conds.append(f"relative_physical_stats:{relative_physical_stats}")

    turn_upside_down = detail.get("turn_upside_down")
    if turn_upside_down:
        conds.append("turn_upside_down:true")

    return conds


def get_evolution_info(
    species_data: Dict[str, Any]
) -> Tuple[Optional[str], List[str], str]:
    """
    For a given species, return:
      - previous evolution species name (or None)
      - list of next evolution species names (direct evolutions)
      - comma-separated evolution conditions string for the current -> next(s)
    """
    evo_chain_url = species_data.get("evolution_chain", {}).get("url")
    if not evo_chain_url:
        return None, [], ""

    chain_id = parse_chain_id_from_url(evo_chain_url)
    chain_data = get_evolution_chain(chain_id)
    chain_root = chain_data.get("chain", {})

    target_species_name = species_data.get("name")
    context = find_evolution_context(chain_root, target_species_name)
    if context is None:
        return None, [], ""

    parent_node, current_node = context
    prev_name = parent_node.get("species", {}).get("name") if parent_node else None

    next_nodes = current_node.get("evolves_to", [])
    next_names = [n.get("species", {}).get("name") for n in next_nodes if n.get("species")]

    # Collect conditions from all evolution_details for all "next" nodes
    all_condition_strings: List[str] = []
    for node in next_nodes:
        details_list = node.get("evolution_details", [])
        for det in details_list:
            conds = parse_evolution_conditions(det)
            if conds:
                # join conditions for this branch with '&'
                all_condition_strings.append("&".join(conds))

    # Finally, join branches with ' | ' and overall conditions with commas
    # As requested: comma-separated conditions in a single string
    if all_condition_strings:
        # e.g. 'trigger:level-up&level:16, trigger:use-item&use_item:fire-stone'
        conditions_str = ", ".join(all_condition_strings)
    else:
        conditions_str = ""

    return prev_name, next_names, conditions_str


def species_name_to_pokemon_id(name: str) -> int:
    """
    Given a species name, resolve to the default Pokémon form's numeric ID.
    Uses the /pokemon/{name} endpoint, cached.
    """
    data = get_pokemon(name)
    return int(data["id"])


# --------------------------
# Damage relations handling
# --------------------------

def build_type_damage_tables() -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Set[str]]]]:
    """
    Build:
    - defense_multipliers[type_def][type_att] -> multiplier (0, 0.5, 1, 2, …)
    - offensive_relations[type_name] -> {
        "double_to": set([...]),
        "half_to": set([...]),
        "no_to": set([...]),
      }
    """
    type_list_data = get_json(f"{BASE_URL}/type")
    type_results = type_list_data.get("results", [])
    type_names = [t["name"] for t in type_results]

    # Initialize defense multipliers
    defense_multipliers: Dict[str, Dict[str, float]] = {}
    offensive_relations: Dict[str, Dict[str, Set[str]]] = {}

    for t_name in type_names:
        type_data = get_type(t_name)
        dr = type_data.get("damage_relations", {})

        # Start with all attack types at 1.0 for this defending type
        defense_multipliers[t_name] = {att: 1.0 for att in type_names}

        for rel_type in dr.get("double_damage_from", []):
            att_name = rel_type["name"]
            defense_multipliers[t_name][att_name] *= 2.0

        for rel_type in dr.get("half_damage_from", []):
            att_name = rel_type["name"]
            defense_multipliers[t_name][att_name] *= 0.5

        for rel_type in dr.get("no_damage_from", []):
            att_name = rel_type["name"]
            defense_multipliers[t_name][att_name] *= 0.0

        # Offensive relations: store as sets of type names
        offensive_relations[t_name] = {
            "double_to": set(rel["name"] for rel in dr.get("double_damage_to", [])),
            "half_to": set(rel["name"] for rel in dr.get("half_damage_to", [])),
            "no_to": set(rel["name"] for rel in dr.get("no_damage_to", [])),
        }

    return defense_multipliers, offensive_relations


def compute_pokemon_damage_relations(
    primary_type: Optional[str],
    secondary_type: Optional[str],
    defense_multipliers: Dict[str, Dict[str, float]],
    offensive_relations: Dict[str, Dict[str, Set[str]]]
) -> Dict[str, str]:
    """
    Given a Pokémon's types, compute:
      - double_damage_from, half_damage_from, no_damage_from
        (using multiplicative combination of type weaknesses)
      - double_damage_to, half_damage_to, no_damage_to
        (union of offensive relations of all its types)

    Returns a dict with the final comma-separated string fields.
    """
    # If Pokémon has no type info, return empty strings
    if primary_type is None and secondary_type is None:
        return {
            "double_damage_from": "",
            "half_damage_from": "",
            "no_damage_from": "",
            "double_damage_to": "",
            "half_damage_to": "",
            "no_damage_to": "",
        }

    # --- Defensive multipliers (incoming damage) ---
    # Gather all taking types from defense_multipliers
    all_attack_types = list(defense_multipliers.keys())
    combined: Dict[str, float] = {t: 1.0 for t in all_attack_types}

    types_for_calc = [t for t in [primary_type, secondary_type] if t is not None]

    for ptype in types_for_calc:
        if ptype not in defense_multipliers:
            continue
        for att_type, mult in defense_multipliers[ptype].items():
            combined[att_type] *= mult

    double_from = sorted(
        [t for t, m in combined.items() if m > 1.0]
    )
    half_from = sorted(
        [t for t, m in combined.items() if 0 < m < 1.0]
    )
    no_from = sorted(
        [t for t, m in combined.items() if m == 0.0]
    )

    # --- Offensive relations (outgoing damage) ---
    double_to: Set[str] = set()
    half_to: Set[str] = set()
    no_to: Set[str] = set()

    for ptype in types_for_calc:
        rel = offensive_relations.get(ptype, {})
        double_to |= rel.get("double_to", set())
        half_to |= rel.get("half_to", set())
        no_to |= rel.get("no_to", set())

    # Convert to comma-separated strings
    return {
        "double_damage_from": ",".join(double_from),
        "half_damage_from": ",".join(half_from),
        "no_damage_from": ",".join(no_from),
        "double_damage_to": ",".join(sorted(double_to)),
        "half_damage_to": ",".join(sorted(half_to)),
        "no_damage_to": ",".join(sorted(no_to)),
    }


# --------------------------
# Main ETL
# --------------------------

def fetch_all_species_list() -> List[Dict[str, Any]]:
    """Fetch list of all Pokémon species entries."""
    url = f"{BASE_URL}/pokemon-species?limit=10000"
    data = get_json(url)
    results = data.get("results", [])
    if MAX_SPECIES is not None:
        results = results[:MAX_SPECIES]
    return results


def ensure_data_dir() -> Path:
    """Ensure ../data directory exists relative to this script."""
    script_path = Path(__file__).resolve()
    data_dir = script_path.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def main():
    data_dir = ensure_data_dir()
    pokemon_csv_path = data_dir / "pokemon.csv"
    damage_csv_path = data_dir / "damage_relations.csv"

    species_list = fetch_all_species_list()
    print(f"Found {len(species_list)} species to process.")

    # Precompute type damage tables
    print("Building type damage tables...")
    defense_multipliers, offensive_relations = build_type_damage_tables()
    print("Type damage tables ready.")

    pokemon_rows: List[Dict[str, Any]] = []
    damage_rows: List[Dict[str, Any]] = []

    for idx, entry in enumerate(species_list, start=1):
        species_name = entry["name"]
        print(f"[{idx}/{len(species_list)}] Processing species: {species_name}")

        try:
            species_data = get_species(species_name)

            # Find default Pokémon form from species varieties
            varieties = species_data.get("varieties", [])
            default_pokemon_name = species_name
            for v in varieties:
                if v.get("is_default"):
                    default_pokemon_name = v.get("pokemon", {}).get("name", species_name)
                    break

            pokemon_data = get_pokemon(default_pokemon_name)

            # Basic info
            poke_id = int(pokemon_data["id"])
            name = pokemon_data["name"]

            # Species "name" for display: we can use species_data["genera"] or just species_data["name"]
            species_display = species_data.get("name", "")
            # Optional: nicer species name from genera (e.g. "Seed Pokémon")
            for gen in species_data.get("genera", []):
                if gen.get("language", {}).get("name") == "en":
                    species_display = gen.get("genus", species_display)
                    break

            generation = get_generation_number(species_data)

            official_art, sprite_url, icon_url = extract_sprites(pokemon_data)
            primary_type, secondary_type = extract_types(pokemon_data)
            height_m, weight_kg = convert_height_weight(pokemon_data)
            flavor_text = clean_flavor_text(species_data)

            is_legendary = bool(species_data.get("is_legendary", False))
            is_mythical = bool(species_data.get("is_mythical", False))

            # Evolution info
            prev_species_name, next_species_names, evo_conditions_str = get_evolution_info(species_data)

            prev_evo_id: Optional[int] = None
            next_evo_ids: List[int] = []

            if prev_species_name:
                prev_evo_id = species_name_to_pokemon_id(prev_species_name)

            for n_name in next_species_names:
                try:
                    next_evo_ids.append(species_name_to_pokemon_id(n_name))
                except Exception as e:
                    print(f"  Warning: could not resolve next evolution '{n_name}' to ID: {e}")

            # Convert to CSV fields: IDs as comma-separated list (or empty)
            prev_evo_field = str(prev_evo_id) if prev_evo_id is not None else ""
            next_evo_field = ",".join(str(i) for i in sorted(set(next_evo_ids))) if next_evo_ids else ""

            # Damage relations
            damage = compute_pokemon_damage_relations(
                primary_type,
                secondary_type,
                defense_multipliers,
                offensive_relations,
            )

            # Build main Pokémon row
            pokemon_row = {
                "id": poke_id,
                "name": name,
                "species": species_display,
                "generation": generation,
                "official_artwork_url": official_art or "",
                "sprite_url": sprite_url or "",
                "icon_url": icon_url or "",
                "primary_type": primary_type or "",
                "secondary_type": secondary_type or "",
                "height_m": round(height_m, 2),
                "weight_kg": round(weight_kg, 2),
                "flavor_text": flavor_text,
                "previous_evolution_id": prev_evo_field,
                "next_evolution_id": next_evo_field,
                "evolution_conditions": evo_conditions_str,
                "is_legendary": int(is_legendary),
                "is_mythical": int(is_mythical),
            }
            pokemon_rows.append(pokemon_row)

            damage_row = {
                "id": poke_id,
                "double_damage_from": damage["double_damage_from"],
                "half_damage_from": damage["half_damage_from"],
                "no_damage_from": damage["no_damage_from"],
                "double_damage_to": damage["double_damage_to"],
                "half_damage_to": damage["half_damage_to"],
                "no_damage_to": damage["no_damage_to"],
            }
            damage_rows.append(damage_row)

        except Exception as e:
            print(f"  Error processing species '{species_name}': {e}")

    # Sort rows by ID for sanity
    pokemon_rows.sort(key=lambda r: r["id"])
    damage_rows.sort(key=lambda r: r["id"])

    # Write CSVs
    print(f"Writing {pokemon_csv_path} ...")
    with pokemon_csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id",
            "name",
            "species",
            "generation",
            "official_artwork_url",
            "sprite_url",
            "icon_url",
            "primary_type",
            "secondary_type",
            "height_m",
            "weight_kg",
            "flavor_text",
            "previous_evolution_id",
            "next_evolution_id",
            "evolution_conditions",
            "is_legendary",
            "is_mythical",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pokemon_rows)

    print(f"Writing {damage_csv_path} ...")
    with damage_csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id",
            "double_damage_from",
            "half_damage_from",
            "no_damage_from",
            "double_damage_to",
            "half_damage_to",
            "no_damage_to",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(damage_rows)

    print("Done.")


if __name__ == "__main__":
    main()
