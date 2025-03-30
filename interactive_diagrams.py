import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
import os

def create_placeholder_images():
    """Create placeholder images if actual images aren't available"""
    placeholders_path = "static/images"
    os.makedirs(placeholders_path, exist_ok=True)
    
    # Dictionary of diagrams and their components
    diagrams = {
        "lymph_node": ["base", "capsule", "cortex", "medulla", "germinal_center", "afferent_vessels", "efferent_vessel"],
        "respiratory": ["base", "trachea", "bronchi", "bronchioles", "alveoli", "diaphragm"],
        "digestive": ["base", "esophagus", "stomach", "small_intestine", "large_intestine", "liver", "pancreas", "gallbladder"]
    }
    
    # Generate a simple colored rectangle for each placeholder
    colors = {
        "base": (240, 240, 240),
        "capsule": (200, 200, 255),
        "cortex": (255, 200, 200),
        "medulla": (200, 255, 200),
        "germinal_center": (255, 255, 200),
        "afferent_vessels": (200, 255, 255),
        "efferent_vessel": (255, 200, 255),
        "trachea": (200, 200, 255),
        "bronchi": (255, 200, 200),
        "bronchioles": (200, 255, 200),
        "alveoli": (255, 255, 200),
        "diaphragm": (200, 255, 255),
        "esophagus": (200, 200, 255),
        "stomach": (255, 200, 200),
        "small_intestine": (200, 255, 200),
        "large_intestine": (255, 255, 200),
        "liver": (200, 255, 255),
        "pancreas": (255, 200, 255),
        "gallbladder": (255, 255, 200)
    }
    
    # Create placeholders for each diagram
    for diagram, parts in diagrams.items():
        for part in parts:
            img_path = f"{placeholders_path}/{diagram}_{part}.png"
            if not os.path.exists(img_path):
                # Create a colored image as placeholder
                img = Image.new('RGB', (400, 300), colors.get(part, (240, 240, 240)))
                
                # Add text indicating this is a placeholder
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("Arial", 20)
                except:
                    font = ImageFont.load_default()
                
                text = f"{diagram.replace('_', ' ').title()}\n{part.replace('_', ' ').title()}"
                text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
                position = ((400 - text_width) // 2, (300 - text_height) // 2)
                draw.text(position, text, font=font, fill=(0, 0, 0))
                
                # For highlighted parts, add a border
                if part != "base":
                    for i in range(5):
                        draw.rectangle([(i, i), (399-i, 299-i)], outline=(255, 0, 0))
                
                img.save(img_path)

def get_image_path(diagram_type, structure):
    """Get path to image, checking if it exists first"""
    path = f"static/images/{diagram_type}_{structure}.png"
    if os.path.exists(path):
        return path
    else:
        # Create placeholder images if they don't exist
        create_placeholder_images()
        return path

def lymph_node_interactive():
    """Create an interactive lymph node diagram"""
    st.subheader("Lymph Node Structure")
    
    # Load base image
    base_img_path = get_image_path("lymph_node", "base")
    
    # Create clickable areas
    col1, col2 = st.columns([3, 1])
    
    # Initialize the session state for current highlight if not exist
    if 'current_highlight' not in st.session_state:
        st.session_state.current_highlight = None
        st.session_state.current_structure = None
    
    with col1:
        if st.session_state.current_highlight and st.session_state.current_structure and st.session_state.current_structure.startswith("lymph_node"):
            st.image(st.session_state.current_highlight, caption=f"Lymph Node - {st.session_state.current_structure.split('_')[-1].title()}", use_column_width=True)
        else:
            st.image(base_img_path, caption="Lymph Node Structure", use_column_width=True)
    
    with col2:
        st.write("Click to highlight:")
        
        if st.button("Capsule", key="ln_capsule"):
            highlight_structure("lymph_node", "capsule")
            
        if st.button("Cortex", key="ln_cortex"):
            highlight_structure("lymph_node", "cortex")
            
        if st.button("Medulla", key="ln_medulla"):
            highlight_structure("lymph_node", "medulla")
            
        if st.button("Germinal Center", key="ln_germinal"):
            highlight_structure("lymph_node", "germinal_center")
            
        if st.button("Afferent Vessels", key="ln_afferent"):
            highlight_structure("lymph_node", "afferent_vessels")
            
        if st.button("Efferent Vessel", key="ln_efferent"):
            highlight_structure("lymph_node", "efferent_vessel")
            
        if st.button("Reset View", key="ln_reset"):
            st.session_state.current_highlight = None
            st.session_state.current_structure = None

def respiratory_system_interactive():
    """Create an interactive respiratory system diagram"""
    st.subheader("Respiratory System Structure")
    
    # Load base image
    base_img_path = get_image_path("respiratory", "base")
    
    # Create clickable areas
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.current_highlight and st.session_state.current_structure and st.session_state.current_structure.startswith("respiratory"):
            st.image(st.session_state.current_highlight, caption=f"Respiratory System - {st.session_state.current_structure.split('_')[-1].title()}", use_column_width=True)
        else:
            st.image(base_img_path, caption="Respiratory System", use_column_width=True)
    
    with col2:
        st.write("Click to highlight:")
        
        if st.button("Trachea", key="rs_trachea"):
            highlight_structure("respiratory", "trachea")
            
        if st.button("Bronchi", key="rs_bronchi"):
            highlight_structure("respiratory", "bronchi")
            
        if st.button("Bronchioles", key="rs_bronchioles"):
            highlight_structure("respiratory", "bronchioles")
            
        if st.button("Alveoli", key="rs_alveoli"):
            highlight_structure("respiratory", "alveoli")
            
        if st.button("Diaphragm", key="rs_diaphragm"):
            highlight_structure("respiratory", "diaphragm")
            
        if st.button("Reset View", key="rs_reset"):
            st.session_state.current_highlight = None
            st.session_state.current_structure = None

def digestive_system_interactive():
    """Create an interactive digestive system diagram"""
    st.subheader("Digestive System Structure")
    
    # Load base image
    base_img_path = get_image_path("digestive", "base")
    
    # Create clickable areas
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.current_highlight and st.session_state.current_structure and st.session_state.current_structure.startswith("digestive"):
            st.image(st.session_state.current_highlight, caption=f"Digestive System - {st.session_state.current_structure.split('_')[-1].title()}", use_column_width=True)
        else:
            st.image(base_img_path, caption="Digestive System", use_column_width=True)
    
    with col2:
        st.write("Click to highlight:")
        
        if st.button("Esophagus", key="ds_esophagus"):
            highlight_structure("digestive", "esophagus")
            
        if st.button("Stomach", key="ds_stomach"):
            highlight_structure("digestive", "stomach")
            
        if st.button("Small Intestine", key="ds_small"):
            highlight_structure("digestive", "small_intestine")
            
        if st.button("Large Intestine", key="ds_large"):
            highlight_structure("digestive", "large_intestine")
            
        if st.button("Liver", key="ds_liver"):
            highlight_structure("digestive", "liver")
            
        if st.button("Pancreas", key="ds_pancreas"):
            highlight_structure("digestive", "pancreas")
            
        if st.button("Gallbladder", key="ds_gallbladder"):
            highlight_structure("digestive", "gallbladder")
            
        if st.button("Reset View", key="ds_reset"):
            st.session_state.current_highlight = None
            st.session_state.current_structure = None

def highlight_structure(diagram_type, structure):
    """Highlight a specific structure in a diagram"""
    # Load the appropriate highlight overlay
    highlight_img_path = get_image_path(diagram_type, structure)
    st.session_state.current_highlight = highlight_img_path
    st.session_state.current_structure = f"{diagram_type}_{structure}"
