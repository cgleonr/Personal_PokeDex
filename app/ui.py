import streamlit as st
import pandas as pd
from app.components.pokemon_card import pokemon_card
from app.components.modal import show_pokemon_modal

# -------------------------------------------------------------------
# LANDING PAGE
# -------------------------------------------------------------------

def render_landing_page(df: pd.DataFrame):
    st.title("📘 Welcome to Your Personal Pokédex")

    if df.empty:
        st.warning("No data loaded. Please refresh the database.")
        return

    st.subheader("✨ Random Pokémon")

    # --- FIX: Only generate random Pokémon once ---
    if "landing_random" not in st.session_state:
        st.session_state["landing_random"] = df.sample(3)

    random_rows = st.session_state["landing_random"]

    cols = st.columns(3)

    for i, (_, row) in enumerate(random_rows.iterrows()):
        with cols[i]:

            # BUTTON FIRST
            if st.button(f"View #{row['id']}", key=f"landing_btn_{row['id']}"):
                st.session_state["selected_pokemon"] = row.to_dict()
                st.session_state["view"] = "details"
                st.rerun()

            # CARD BELOW BUTTON
            pokemon_card(row)


# -------------------------------------------------------------------
# SEARCH RESULTS PAGE
# -------------------------------------------------------------------

def render_search_results(df: pd.DataFrame, query: str):
    st.title("🔍 Search Results")

    query = query.lower().strip()
    if not query:
        st.warning("Enter a Pokémon name or ID.")
        return

    results = df[
        df["name"].str.contains(query, case=False) |
        df["id"].astype(str).str.contains(query)
    ]

    if results.empty:
        st.warning("No Pokémon found.")
        return

    cols = st.columns(4)
    idx = 0

    for _, row in results.iterrows():
        with cols[idx % 4]:

            if st.button(f"View #{row['id']}", key=f"search_btn_{row['id']}"):
                st.session_state["selected_pokemon"] = row.to_dict()
                st.session_state["view"] = "details"
                st.rerun()

            pokemon_card(row)

        idx += 1
