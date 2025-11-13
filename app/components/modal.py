import streamlit as st
import math
from .type_badge import type_badge


# ------------------------------------------------------------
# SAFE VALUE HELPERS
# ------------------------------------------------------------

def safe_val(v):
    """Convert NaN/blank/None → None."""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    v = str(v).strip()
    if v == "" or v.lower() == "nan":
        return None
    return v


def safe_id(v):
    """
    Fix evolution IDs loaded from CSV:
    - "307" → 307
    - 307.0 → 307
    - "" → None
    - NaN → None
    """
    if v is None:
        return None
    if isinstance(v, float):
        if math.isnan(v):
            return None
        return int(v)
    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return None
        # sometimes floats come as strings (e.g., "307.0")
        try:
            return int(float(v))
        except:
            return None
    return None


def parse_list_field(s):
    """
    Convert CSV fields like:
    "", NaN, "fire,water", "fire, water"
    → ["fire","water"]
    """
    if s is None:
        return []
    if isinstance(s, float):
        if math.isnan(s):
            return []
        s = str(s)
    if not isinstance(s, str):
        return []
    s = s.strip()
    if s == "":
        return []
    return [x.strip().lower() for x in s.split(",") if x.strip()]


# ------------------------------------------------------------
# MAIN DETAILS PAGE
# ------------------------------------------------------------

def build_full_evo_chain(df, current_id):
    """
    Build the full evolution chain from the CSV, left→right.
    Includes support for branching evolutions.
    Returns a list of lists:
       [ [id1], [id2, id3], [id4] ]
    Each inner list = all species at that stage.
    """

    # Convert IDs to ints
    df = df.copy()
    df["id"] = df["id"].astype(int)

    # Start from the first stage
    # Find the earliest ancestor (walk back using previous_evolution_id)
    ancestor = current_id
    visited = set()

    while True:
        row = df.loc[df["id"] == ancestor]
        if row.empty:
            break
        prev_raw = row.iloc[0]["previous_evolution_id"]
        prev_id = safe_id(prev_raw)
        if prev_id is None or prev_id in visited:
            break
        visited.add(prev_id)
        ancestor = prev_id

    # Now build the chain forward
    chain = []
    stage = [ancestor]
    visited.clear()

    while stage:
        chain.append(stage)
        next_stage = []

        for pid in stage:
            row = df.loc[df["id"] == pid]
            if row.empty:
                continue

            next_raw = safe_val(row.iloc[0]["next_evolution_id"])
            next_ids = [safe_id(x) for x in parse_list_field(next_raw)]

            for nid in next_ids:
                if nid and nid not in visited:
                    next_stage.append(nid)
                    visited.add(nid)

        stage = next_stage

    return chain


def show_pokemon_modal(row):
    name = row["name"].capitalize()
    st.markdown(f"## #{row['id']} — {name}")

    # --------------------------------------------------------
    # HEADER INFO
    # --------------------------------------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(row["official_artwork_url"], width=250)

    with col2:
        st.write(f"**Species:** {row['species']}")
        st.write(f"**Generation:** {row['generation']}")

        st.write("**Type(s):**")
        type_badge(row["primary_type"])
        type_badge(row["secondary_type"])

        st.write("---")
        st.write(f"**Height:** {row['height_m']} m")
        st.write(f"**Weight:** {row['weight_kg']} kg")

    st.write("---")

    # --------------------------------------------------------
    # BASE STATS
    # --------------------------------------------------------
    st.markdown("### Base Stats")

    stats = {
        "HP": row["hp"],
        "Attack": row["attack"],
        "Defense": row["defense"],
        "Sp. Atk": row["special_attack"],
        "Sp. Def": row["special_defense"],
        "Speed": row["speed"],
        "Total": row["base_stat_total"],
    }

    for label, value in stats.items():
        st.write(f"**{label}:** {value}")

    st.write("---")

    # --------------------------------------------------------
    # POKÉDEX ENTRY
    # --------------------------------------------------------
    st.markdown("### Pokédex Entry")

    text = safe_val(row.get("flavor_text"))
    st.write(text if text else "No entry available.")

    st.write("---")

    # --------------------------------------------------------
    # FULL EVOLUTION CHAIN (HORIZONTAL FIXED)
    # --------------------------------------------------------
    st.markdown("### Evolution Chain")

    full_chain = build_full_evo_chain(st.session_state["df"], row["id"])

    html = """
    <div style='display:flex; align-items:center; flex-wrap:wrap; gap:32px;'>
    """

    for stage_index, stage in enumerate(full_chain):

        # Stage group container
        html += "<div style='display:flex; flex-direction:row; gap:18px;'>"

        for pid in stage:
            sprite = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pid}.png"

            # Current Pokémon highlighted
            if pid == row["id"]:
                html += f"""
                <div style='text-align:center;'>
                    <img src='{sprite}' width='120'
                        style='border:3px solid #ffcb05; border-radius:12px; padding:4px;'>
                    <div style='font-weight:bold; color:#ffcb05;'>#{pid}</div>
                </div>
                """
            else:
                html += f"""
                <div style='text-align:center;'>
                    <img src='{sprite}' width='80'>
                    <div>#{pid}</div>
                </div>
                """

        html += "</div>"  # END stage group

        # Add arrow unless last stage
        if stage_index < len(full_chain) - 1:
            html += "<div style='font-size:2rem; font-weight:bold;'>→</div>"

    html += "</div>"  # END flex root

    st.markdown(html, unsafe_allow_html=True)




    # --------------------------------------------------------
    # DAMAGE TAKEN (ONLY DAMAGE TO THIS POKÉMON)
    # --------------------------------------------------------
    st.markdown("### Damage Taken")

    weak_to = parse_list_field(row.get("double_damage_from"))
    resists = parse_list_field(row.get("half_damage_from"))
    immune_to = parse_list_field(row.get("no_damage_from"))

    def show_block(label, items):
        st.write(f"**{label}:**")
        if not items:
            st.write("None")
        else:
            for t in items:
                type_badge(t)
        st.write("")

    show_block("Weak To (2×)", weak_to)
    show_block("Resists (½×)", resists)
    show_block("Immune To (0×)", immune_to)
