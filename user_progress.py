import json
import os
from datetime import datetime

def initialize_user_progress(user_id):
    """Initialize progress tracking for a new user"""
    if not os.path.exists("data/user_progress"):
        os.makedirs("data/user_progress")
        
    progress = {
        "user_id": user_id,
        "quiz_history": [],
        "viewed_sections": {
            "lymphatic": [],
            "respiratory": [],
            "digestive": []
        },
        "mastery_levels": {
            "lymphatic": 0,
            "respiratory": 0,
            "digestive": 0
        }
    }
    
    save_user_progress(user_id, progress)
    return progress

def save_user_progress(user_id, progress):
    """Save user progress to file"""
    with open(f"data/user_progress/{user_id}.json", "w") as f:
        json.dump(progress, f)
        
def load_user_progress(user_id):
    """Load user progress from file"""
    try:
        with open(f"data/user_progress/{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return initialize_user_progress(user_id)
        
def update_quiz_history(user_id, quiz_results, category):
    """Add new quiz results to history"""
    progress = load_user_progress(user_id)
    
    quiz_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "score": quiz_results["score"],
        "total": quiz_results["total"],
        "difficulty": quiz_results["difficulty"]
    }
    
    progress["quiz_history"].append(quiz_entry)
    
    # Update mastery level based on recent quiz performance
    recent_quizzes = [q for q in progress["quiz_history"] if q["category"] == category][-5:]
    if len(recent_quizzes) >= 3:
        avg_score = sum(q["score"]/q["total"] for q in recent_quizzes) / len(recent_quizzes)
        
        if avg_score > 0.9:
            progress["mastery_levels"][category] = 3  # Expert
        elif avg_score > 0.7:
            progress["mastery_levels"][category] = 2  # Intermediate
        else:
            progress["mastery_levels"][category] = 1  # Beginner
    
    save_user_progress(user_id, progress)
    return progress

def update_viewed_section(user_id, section):
    """Record that user has viewed a section"""
    progress = load_user_progress(user_id)
    
    if section in progress["viewed_sections"]:
        timestamp = datetime.now().isoformat()
        progress["viewed_sections"][section].append(timestamp)
        save_user_progress(user_id, progress)
    
    return progress
