import streamlit as st
import math

TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}

def type_badge(type_name):
    """Safely render a type badge (handles NaN, None, empty)."""

    # FIX: handle NaN or None or float types
    if not type_name or (isinstance(type_name, float) and math.isnan(type_name)):
        return  # don't render anything

    type_name = str(type_name).strip().lower()
    color = TYPE_COLORS.get(type_name, "#888888")

    st.markdown(
        f"""
        <span style="
            background-color:{color};
            padding:4px 10px;
            border-radius:8px;
            color:white;
            margin-right:4px;
            font-size:0.8rem;
            font-weight:600;">
            {type_name.capitalize()}
        </span>
        """,
        unsafe_allow_html=True,
    )
