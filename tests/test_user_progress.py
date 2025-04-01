"""
Tests for the user_progress module
"""
import os
import tempfile
import json
import pytest
from datetime import datetime
from user_progress import initialize_user_progress, update_viewed_section, load_user_progress

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            os.makedirs("data/user_progress", exist_ok=True)
            yield temp_dir
        finally:
            os.chdir(original_dir)

def test_initialize_user_progress(temp_data_dir):
    """Test user progress initialization"""
    user_id = "test-user-123"
    
    # Initialize progress
    progress = initialize_user_progress(user_id)
    
    # Check structure
    assert "quiz_history" in progress
    assert "viewed_sections" in progress
    assert "mastery_levels" in progress
    
    # Check file was created
    assert os.path.exists(f"data/user_progress/{user_id}.json")

def test_update_viewed_section(temp_data_dir):
    """Test section viewing tracking"""
    user_id = "test-user-123"
    progress = initialize_user_progress(user_id)
    
    # First time viewing a section
    result = update_viewed_section(user_id, "respiratory")
    assert "respiratory" in result["viewed_sections"]
    assert len(result["viewed_sections"]["respiratory"]) == 1
    
    # View the same section again
    result = update_viewed_section(user_id, "respiratory")
    assert len(result["viewed_sections"]["respiratory"]) == 2