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
        if st.sidebar.button("⬅ Back to Home"):
            st.session_state["view"] = "landing"
            st.session_state["selected_pokemon"] = None
            st.rerun()
    

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
st.session_state["df"] = df  # needed for evolution chain builder

# Always show top search bar
query = st.text_input("Search Pokémon by name or ID", st.session_state.get("search_query", ""))

# Update stored search query
st.session_state["search_query"] = query


# ---------------------------------------------------------
# DECISION LOGIC (ORDER MATTERS!)
# ---------------------------------------------------------

# 1. If viewing details — that takes priority over ANY search
if st.session_state.get("view") == "details":
    from app.components.modal import show_pokemon_modal
    show_pokemon_modal(st.session_state["selected_pokemon"])
    st.stop()


# 2. If search bar is not empty → show search results
if query.strip() != "":
    st.session_state["view"] = "search"
    render_search_results(df, query)
    st.stop()


# 3. Otherwise → landing page
st.session_state["view"] = "landing"
render_landing_page(df)
