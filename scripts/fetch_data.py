#!/usr/bin/env python3
"""
FINALIZED ETL SCRIPT FOR POKEDEX
Now includes:
- Base stats (hp, attack, defense, special_attack, special_defense, speed)
- Base stat total (base_stat_total)
"""

import csv
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set, Callable
from functools import lru_cache
import requests

BASE_URL = "https://pokeapi.co/api/v2"
REQUEST_DELAY_SECONDS = 0.1     # Polite rate limit

POKEMON_FIELDNAMES = [
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

    # NEW: Base Stats
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed",
    "base_stat_total",

    "flavor_text",
    "previous_evolution_id",
    "next_evolution_id",
    "evolution_conditions",
    "is_legendary",
    "is_mythical",
]

DAMAGE_FIELDNAMES = [
    "id",
    "double_damage_from",
    "half_damage_from",
    "no_damage_from",
    "double_damage_to",
    "half_damage_to",
    "no_damage_to",
]

# --------------------------------------------------------
# HTTP / Fetch Helpers
# --------------------------------------------------------

def get_json(url: str) -> Dict[str, Any]:
    for attempt in range(3):
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.0)


@lru_cache(maxsize=None)
def get_pokemon(id_or_name: str):
    return get_json(f"{BASE_URL}/pokemon/{id_or_name}")


@lru_cache(maxsize=None)
def get_species(id_or_name: str):
    return get_json(f"{BASE_URL}/pokemon-species/{id_or_name}")


@lru_cache(maxsize=None)
def get_type(type_name: str):
    return get_json(f"{BASE_URL}/type/{type_name}")


@lru_cache(maxsize=None)
def get_evo_chain(chain_id: int):
    return get_json(f"{BASE_URL}/evolution-chain/{chain_id}")


# --------------------------------------------------------
# Species → canonical Pokémon resolver
# --------------------------------------------------------

@lru_cache(maxsize=None)
def species_to_default_form(species_name: str) -> str:
    s = get_species(species_name)
    for v in s["varieties"]:
        if v["is_default"]:
            return v["pokemon"]["name"]
    return species_name


def species_name_to_id(species_name: str) -> int:
    name = species_to_default_form(species_name)
    data = get_pokemon(name)
    return int(data["id"])


# --------------------------------------------------------
# Transform Helpers
# --------------------------------------------------------

def clean_flavor_text(species_data) -> str:
    for entry in species_data.get("flavor_text_entries", []):
        if entry["language"]["name"] == "en":
            t = entry["flavor_text"]
            t = t.replace("\n", " ").replace("\f", " ")
            return " ".join(t.split())
    return ""


def extract_sprites(p):
    sprites = p.get("sprites", {})
    official = sprites.get("other", {}).get("official-artwork", {}).get("front_default")
    sprite = sprites.get("front_default")
    icon = (
        sprites.get("versions", {})
        .get("generation-viii", {})
        .get("icons", {})
        .get("front_default")
        or sprite
    )
    return official, sprite, icon


def extract_types(p):
    types = sorted(p.get("types", []), key=lambda t: t["slot"])
    ptype = types[0]["type"]["name"] if types else ""
    stype = types[1]["type"]["name"] if len(types) > 1 else ""
    return ptype, stype


def convert_height_weight(p):
    return p["height"] / 10.0, p["weight"] / 10.0


def get_generation(species_data):
    gname = species_data.get("generation", {}).get("name", "")
    mapping = {
        "generation-i": 1,
        "generation-ii": 2,
        "generation-iii": 3,
        "generation-iv": 4,
        "generation-v": 5,
        "generation-vi": 6,
        "generation-vii": 7,
        "generation-viii": 8,
        "generation-ix": 9,
    }
    return mapping.get(gname, 0)


# --------------------------------------------------------
# Evolution Helpers
# --------------------------------------------------------

def parse_chain_id(url: str) -> int:
    return int(url.rstrip("/").split("/")[-1])


def find_evo_node(node, target) -> Optional[Tuple[Any, Any]]:
    if node["species"]["name"] == target:
        return None, node
    for child in node["evolves_to"]:
        res = find_evo_node(child, target)
        if res:
            parent, found = res
            return (node if parent is None else parent), found
    return None


def parse_evo_details(det: Dict[str, Any]) -> List[str]:
    result = []
    mapping = [
        ("trigger", lambda d: d["trigger"]["name"]),
        ("min_level", lambda d: f"level:{d['min_level']}"),
        ("item", lambda d: f"use_item:{d['item']['name']}"),
        ("held_item", lambda d: f"held_item:{d['held_item']['name']}"),
        ("time_of_day", lambda d: f"time:{d['time_of_day']}"),
        ("location", lambda d: f"location:{d['location']['name']}"),
        ("known_move", lambda d: f"known_move:{d['known_move']['name']}"),
        ("known_move_type", lambda d: f"known_move_type:{d['known_move_type']['name']}"),
        ("min_happiness", lambda d: f"min_happiness:{d['min_happiness']}"),
        ("min_affection", lambda d: f"min_affection:{d['min_affection']}"),
        ("min_beauty", lambda d: f"min_beauty:{d['min_beauty']}"),
        ("gender", lambda d: f"gender:{d['gender']}"),
        ("needs_overworld_rain", lambda d: "needs_overworld_rain:true"),
        ("relative_physical_stats", lambda d: f"relative_physical_stats:{d['relative_physical_stats']}"),
        ("turn_upside_down", lambda d: "turn_upside_down:true"),
    ]
    for key, func in mapping:
        if key in det and det[key] not in (None, "", []):
            result.append(func(det))
    return result


def get_evo_info(species_data) -> Tuple[Optional[int], List[int], str]:
    chain_url = species_data["evolution_chain"]["url"]
    chain = get_evo_chain(parse_chain_id(chain_url))["chain"]

    name = species_data["name"]
    found = find_evo_node(chain, name)
    if not found:
        return None, [], ""

    parent, node = found
    prev_id = species_name_to_id(parent["species"]["name"]) if parent else None

    next_ids = []
    cond_strings = []

    for nxt in node["evolves_to"]:
        sname = nxt["species"]["name"]
        next_ids.append(species_name_to_id(sname))

        for det in nxt["evolution_details"]:
            conds = parse_evo_details(det)
            if conds:
                cond_strings.append("&".join(conds))

    return prev_id, next_ids, ", ".join(cond_strings)


# --------------------------------------------------------
# Damage Relations Setup
# --------------------------------------------------------

def build_damage_tables():
    type_list = get_json(f"{BASE_URL}/type")["results"]
    type_names = [t["name"] for t in type_list]

    defense = {t: {a: 1.0 for a in type_names} for t in type_names}
    offense = {t: {"double": set(), "half": set(), "none": set()} for t in type_names}

    for t in type_names:
        data = get_type(t)["damage_relations"]

        for rel in data["double_damage_from"]:
            defense[t][rel["name"]] *= 2
        for rel in data["half_damage_from"]:
            defense[t][rel["name"]] *= 0.5
        for rel in data["no_damage_from"]:
            defense[t][rel["name"]] *= 0

        offense[t]["double"] |= {r["name"] for r in data["double_damage_to"]} 
        offense[t]["half"] |= {r["name"] for r in data["half_damage_to"]} 
        offense[t]["none"] |= {r["name"] for r in data["no_damage_to"]} 

    return defense, offense


def compute_damage(primary, secondary, defense, offense):
    types = [t for t in (primary, secondary) if t]

    combined = {atk: defense[types[0]][atk] for atk in defense[types[0]]}

    if secondary:
        for atk in combined.keys():
            combined[atk] *= defense[secondary][atk]

    double_from = sorted([t for t, m in combined.items() if m > 1.0])
    half_from = sorted([t for t, m in combined.items() if 0 < m < 1.0])
    no_from = sorted([t for t, m in combined.items() if m == 0])

    double_to = set()
    half_to = set()
    none_to = set()

    for t in types:
        double_to |= offense[t]["double"]
        half_to |= offense[t]["half"]
        none_to |= offense[t]["none"]

    return {
        "double_damage_from": ",".join(double_from),
        "half_damage_from": ",".join(half_from),
        "no_damage_from": ",".join(no_from),
        "double_damage_to": ",".join(sorted(double_to)),
        "half_damage_to": ",".join(sorted(half_to)),
        "no_damage_to": ",".join(sorted(none_to)),
    }


# --------------------------------------------------------
# Species Index + Existing Data
# --------------------------------------------------------

def get_species_index() -> Dict[int, str]:
    url = f"{BASE_URL}/pokemon-species?limit=10000"
    data = get_json(url)["results"]
    out = {}
    for entry in data:
        sid = int(entry["url"].rstrip("/").split("/")[-1])
        out[sid] = entry["name"]
    return out


def load_existing(csv_path: Path) -> Set[int]:
    if not csv_path.exists():
        return set()
    ids = set()
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ids.add(int(row["id"]))
            except:
                pass
    return ids


# --------------------------------------------------------
# MAIN ETL FUNCTION
# --------------------------------------------------------

def run_etl(callback: Optional[Callable[[Dict[str, Any]], None]] = None):
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    poke_path = data_dir / "pokemon.csv"
    dmg_path  = data_dir / "damage_relations.csv"

    existing = load_existing(poke_path)

    species_index = get_species_index()
    all_ids = sorted(species_index.keys())
    missing = [sid for sid in all_ids if sid not in existing]

    if callback:
        callback({
            "missing_total": len(missing),
            "fetched": 0,
            "current_id": None,
            "current_species": None
        })

    if not missing:
        if callback:
            callback({"missing_total": 0, "fetched": 0, "done": True})
        return

    defense, offense = build_damage_tables()

    write_header_poke = not poke_path.exists()
    write_header_dmg = not dmg_path.exists()

    poke_f = poke_path.open("a", newline="", encoding="utf-8")
    dmg_f  = dmg_path.open("a", newline="", encoding="utf-8")

    p_writer = csv.DictWriter(poke_f, fieldnames=POKEMON_FIELDNAMES)
    d_writer = csv.DictWriter(dmg_f,  fieldnames=DAMAGE_FIELDNAMES)

    if write_header_poke:
        p_writer.writeheader()
    if write_header_dmg:
        d_writer.writeheader()

    # Main loop
    for idx, sid in enumerate(missing, start=1):
        species_name = species_index[sid]

        if callback:
            callback({
                "missing_total": len(missing),
                "fetched": idx - 1,
                "current_id": sid,
                "current_species": species_name
            })

        try:
            species_data = get_species(sid)
            default_name = species_to_default_form(species_data["name"])
            p = get_pokemon(default_name)

            pid = p["id"]

            # BASICS
            official, sprite, icon = extract_sprites(p)
            ptype, stype = extract_types(p)
            height, weight = convert_height_weight(p)
            flavor = clean_flavor_text(species_data)
            gen = get_generation(species_data)

            # Species display
            s_display = species_data["name"]
            for g in species_data["genera"]:
                if g["language"]["name"] == "en":
                    s_display = g["genus"]
                    break

            # EVOLUTIONS
            prev_id, next_ids, conds = get_evo_info(species_data)

            # DAMAGE RELATIONS
            dmg = compute_damage(ptype, stype, defense, offense)

            # -----------------------------------------
            # NEW: BASE STATS EXTRACTION
            # -----------------------------------------
            stats_raw = p.get("stats", [])

            hp = attack = defense_stat = sp_atk = sp_def = speed = None

            for stat_entry in stats_raw:
                stat_name = stat_entry["stat"]["name"]
                base_value = stat_entry["base_stat"]

                if stat_name == "hp":
                    hp = base_value
                elif stat_name == "attack":
                    attack = base_value
                elif stat_name == "defense":
                    defense_stat = base_value
                elif stat_name == "special-attack":
                    sp_atk = base_value
                elif stat_name == "special-defense":
                    sp_def = base_value
                elif stat_name == "speed":
                    speed = base_value

            base_stat_total = sum(
                v for v in [hp, attack, defense_stat, sp_atk, sp_def, speed] if v is not None
            )

            # WRITE POKÉMON ROW
            p_writer.writerow({
                "id": pid,
                "name": p["name"],
                "species": s_display,
                "generation": gen,
                "official_artwork_url": official or "",
                "sprite_url": sprite or "",
                "icon_url": icon or "",
                "primary_type": ptype,
                "secondary_type": stype,
                "height_m": round(height, 2),
                "weight_kg": round(weight, 2),

                # NEW STATS
                "hp": hp or "",
                "attack": attack or "",
                "defense": defense_stat or "",
                "special_attack": sp_atk or "",
                "special_defense": sp_def or "",
                "speed": speed or "",
                "base_stat_total": base_stat_total or "",

                "flavor_text": flavor,
                "previous_evolution_id": prev_id or "",
                "next_evolution_id": ",".join(str(x) for x in next_ids),
                "evolution_conditions": conds,
                "is_legendary": int(species_data["is_legendary"]),
                "is_mythical": int(species_data["is_mythical"]),
            })
            poke_f.flush()

            # DAMAGE ROW
            d = {"id": pid}
            d.update(dmg)
            d_writer.writerow(d)
            dmg_f.flush()

        except Exception as e:
            print(f"Error processing ID {sid}: {e}")
            continue

    if callback:
        callback({
            "missing_total": len(missing),
            "fetched": len(missing),
            "done": True
        })

    print("ETL complete.")


if __name__ == "__main__":
    run_etl(callback=None)
