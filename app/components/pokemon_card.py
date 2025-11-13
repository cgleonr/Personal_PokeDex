import streamlit as st
from .type_badge import type_badge

def pokemon_card(row):
    """Simple Pokémon card component."""
    st.markdown(
        """
        <div style="
            background-color:#f4f4f4;
            padding:12px;
            border-radius:12px;
            text-align:center;
            box-shadow:0 2px 6px rgba(0,0,0,0.08);
        ">
        """,
        unsafe_allow_html=True,
    )

    if row["official_artwork_url"]:
        st.image(row["official_artwork_url"], width=140)

    st.markdown(
        f"<h4 style='margin-bottom:4px;'>#{row['id']} — {row['name'].capitalize()}</h4>",
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    with cols[0]:
        type_badge(row["primary_type"])
    with cols[1]:
        type_badge(row["secondary_type"])

    st.markdown("</div>", unsafe_allow_html=True)
