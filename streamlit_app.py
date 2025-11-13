import streamlit as st
from app.loaders import load_pokemon_data
from app.ui import render_landing_page, render_search_results
from app.etl_runner import start_etl_background

st.set_page_config(
    page_title="Pokédex",
    page_icon="🧿",
    layout="wide",
)

# --------------------------
# SESSION STATE
# --------------------------
if "etl_running" not in st.session_state:
    st.session_state.etl_running = False

if "etl_progress" not in st.session_state:
    st.session_state.etl_progress = None

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# --------------------------
# SIDEBAR: Refresh Database
# --------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    if not st.session_state.etl_running:
        if st.button("🔄 Refresh Database"):
            st.session_state.etl_running = True
            st.session_state.etl_progress = None
            start_etl_background()

    else:
        prog = st.session_state.etl_progress

        if prog:
            total = prog.get("missing_total", 0)
            fetched = prog.get("fetched", 0)

            st.info(f"Updating database… {fetched}/{total} completed.")
            if total > 0:
                st.progress(fetched / total)

            if prog.get("done"):
                st.success("Database update completed!")
                st.session_state.etl_running = False

# -------------------------
# MAIN PAGE
# -------------------------

df = load_pokemon_data()

st.session_state["df"] = df

# Always show top search bar
query = st.text_input("Search Pokémon by name or ID", st.session_state.search_query)

if st.session_state.get("view") == "details":
    from app.components.modal import show_pokemon_modal

    show_pokemon_modal(st.session_state["selected_pokemon"])
    st.markdown("---")

    if st.button("⬅ Back to Pokédex"):
        st.session_state["view"] = "landing"
        st.session_state["selected_pokemon"] = None

        # IMPORTANT FIX: Reset random Pokémon for landing page
        if "landing_random" in st.session_state:
            del st.session_state["landing_random"]

        st.rerun()

    st.stop()


# 2. LANDING PAGE (no search query)
if query.strip() == "":
    render_landing_page(df)

# 3. SEARCH RESULTS
else:
    render_search_results(df, query)


