import streamlit as st

def initialize_session_state():
    """Initialize all required session state variables"""
    defaults = {
        "user_id": None,
        "navigation": "Home",
        "dark_mode": False,
        # Quiz-specific state variables
        "quiz_active": False,
        "quiz_submitted": False,
        "user_responses": {},
        "active_questions": [],
        "quiz_result": {"score": 0, "total": 0, "difficulty": "intermediate"},
        "quiz_category": None,
        "quiz_difficulty": "intermediate",  # Make sure this is included
        "current_highlight": None,
        "current_structure": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value