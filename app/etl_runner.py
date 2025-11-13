import threading
import streamlit as st
from scripts.fetch_data import run_etl

_etl_thread = None

def etl_progress_callback(update: dict):
    st.session_state.etl_progress = update

def start_etl_background():
    global _etl_thread

    if _etl_thread and _etl_thread.is_alive():
        return

    _etl_thread = threading.Thread(
        target=run_etl,
        kwargs={"callback": etl_progress_callback},
        daemon=True,
    )
    _etl_thread.start()
