import streamlit as st

def initialize_session_state():
    """Initialize all required session state variables"""
    defaults = {
        "user_id": None,
        "navigation": "Home",
        "dark_mode": False,
        "current_highlight": None,
        "current_structure": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Quiz state is now handled by quiz_state.py
    from quiz_state import initialize_quiz_state
    initialize_quiz_state()