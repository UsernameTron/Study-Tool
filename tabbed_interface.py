import streamlit as st
import os
import logging
from user_progress import update_viewed_section
from image_utils import get_image_path, ensure_directories_exist

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tabbed_interface')

# Ensure required directories exist at import time
ensure_directories_exist()

def tabbed_study_interface(section):
    """
    Creates a tabbed interface for study content with text, histology, and interactive diagrams
    
    Args:
        section: The anatomical section name (e.g., "lymphatic", "respiratory", "digestive")
    """
    # Record that user has viewed this section
    if "user_id" in st.session_state:
        update_viewed_section(st.session_state.user_id, section.lower())
    
    # Create a mapping of system names to their full titles
    system_titles = {
        "lymphatic": "Lymphatic System",
        "respiratory": "Respiratory System",
        "digestive": "Digestive System"
    }
    
    # Display the system title
    st.title(system_titles.get(section, section.capitalize() + " System"))
    
    # Create tabs for different content types
    study_tab, histology_tab, interactive_tab = st.tabs([
        "📚 Study Content", 
        "🔬 Histology Slides", 
        "🔄 Interactive Diagram"
    ])
    
    # Load HTML content for the study tab
    with study_tab:
        with open(os.path.join('data', 'knowledge', f'{section}.html'), 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Use CSS class for styling
        st.markdown(f'<div class="study-content">{content}</div>', unsafe_allow_html=True)
    
    # Display histology slides in the histology tab
    with histology_tab:
        st.subheader(f"{system_titles.get(section, section.capitalize())} Histology")
        
        # Define histology images for each system
        histology_images = {
            "lymphatic": [
                {"name": "thymus", "title": "Thymus Histology", "description": "T-cell maturation site"},
                {"name": "lymph_node", "title": "Lymph Node Histology", "description": "Shows germinal centers and medulla"},
                {"name": "spleen", "title": "Spleen Histology", "description": "Red and white pulp regions"}
            ],
            "respiratory": [
                {"name": "trachea", "title": "Trachea Histology", "description": "Pseudo-stratified ciliated columnar epithelium"},
                {"name": "lung", "title": "Lung Histology", "description": "Alveolar architecture"}
            ],
            "digestive": [
                {"name": "esophagus_stomach", "title": "Esophagus-Stomach Junction", "description": "Transition from stratified squamous to simple columnar epithelium"},
                {"name": "small_intestine", "title": "Small Intestine", "description": "Villi and microvilli structures"}
            ]
        }
        
        # Get histology images for the current section
        section_images = histology_images.get(section, [])
        
        if section_images:
            # Create a selector for different histology slides
            selected_image = st.selectbox(
                "Select a histology slide to view:", 
                options=[img["title"] for img in section_images],
                key=f"histology_selector_{section}"
            )
            
            # Find the selected image data
            image_data = next((img for img in section_images if img["title"] == selected_image), None)
            
            if image_data:
                # Get the image path with error handling
                try:
                    img_path = get_image_path('histology', section, image_data['name'])
                    st.image(img_path, caption=image_data["title"])
                except Exception as e:
                    logger.error(f"Error displaying image {image_data['name']}: {str(e)}")
                    st.error(f"Could not load image: {image_data['title']}")
                
                # Display the description
                st.markdown(f"""
                <div class="custom-card">
                    <h4>{image_data["title"]}</h4>
                    <p>{image_data["description"]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display histological features
                st.subheader("Key Histological Features")
                features = get_histological_features(section, image_data["name"])
                for i, (feature, description) in enumerate(features.items()):
                    st.markdown(f"**{feature}**: {description}")
        else:
            st.warning("No histology slides available for this section.")
    
    # Display interactive diagrams in the interactive tab
    with interactive_tab:
        st.subheader(f"Interactive {system_titles.get(section, section.capitalize())} Diagram")
        
        # Import the interactive diagram functions dynamically
        from interactive_diagrams import (
            lymph_node_interactive, 
            respiratory_system_interactive,
            digestive_system_interactive
        )
        
        # Display the appropriate interactive diagram
        if section == "lymphatic":
            lymph_node_interactive()
        elif section == "respiratory":
            respiratory_system_interactive()
        elif section == "digestive":
            digestive_system_interactive()
        else:
            st.warning("No interactive diagram available for this section.")

def get_histological_features(system, image_name):
    """
    Returns key histological features for a given system and image
    
    Args:
        system: Anatomical system name
        image_name: Name of the histology image
        
    Returns:
        Dictionary of feature names and descriptions
    """
    # Define features for each histology image
    features = {
        "lymphatic": {
            "thymus": {
                "Cortex": "Densely packed area of immature T cells (thymocytes)",
                "Medulla": "Less dense area with mature T cells",
                "Hassall's Corpuscles": "Concentric whorls of epithelial cells in the medulla",
                "Capsule": "Thin connective tissue covering"
            },
            "lymph_node": {
                "Cortex": "Outer region containing lymphoid follicles",
                "Germinal Centers": "Sites of B cell proliferation",
                "Paracortex": "T cell-rich area",
                "Medulla": "Inner region with medullary cords",
                "Subcapsular Sinus": "Space beneath the capsule where afferent lymph enters"
            },
            "spleen": {
                "White Pulp": "Lymphoid tissue surrounding arterioles",
                "Red Pulp": "Blood-filled spaces where RBCs are filtered",
                "Marginal Zone": "Boundary between red and white pulp",
                "Trabecular Arteries": "Branches of splenic artery",
                "Venous Sinuses": "Specialized blood vessels in red pulp"
            }
        },
        "respiratory": {
            "trachea": {
                "Pseudostratified Epithelium": "Ciliated columnar cells with goblet cells",
                "Lamina Propria": "Loose connective tissue below epithelium",
                "Submucosal Glands": "Produce mucus and serous secretions",
                "Hyaline Cartilage": "C-shaped rings providing structural support",
                "Trachealis Muscle": "Smooth muscle connecting ends of cartilage rings"
            },
            "lung": {
                "Alveoli": "Terminal air sacs where gas exchange occurs",
                "Type I Pneumocytes": "Thin squamous cells forming most of alveolar surface",
                "Type II Pneumocytes": "Cuboidal cells that produce surfactant",
                "Alveolar Macrophages": "Phagocytic cells that remove debris",
                "Capillary Network": "Dense network surrounding alveoli"
            }
        },
        "digestive": {
            "esophagus_stomach": {
                "Stratified Squamous Epithelium": "Multiple layers of flattened cells in esophagus",
                "Simple Columnar Epithelium": "Single layer of tall cells in stomach",
                "Z-line": "Abrupt transition between epithelial types",
                "Gastric Pits": "Invaginations in stomach mucosa",
                "Parietal Cells": "Acid-producing cells in stomach glands"
            },
            "small_intestine": {
                "Villi": "Finger-like projections increasing surface area",
                "Microvilli": "Tiny projections forming the brush border",
                "Crypts of Lieberkühn": "Glands between villi containing stem cells",
                "Goblet Cells": "Mucus-secreting cells",
                "Paneth Cells": "Cells at crypt bases containing defensive granules",
                "Lamina Propria": "Connective tissue core of villi"
            }
        }
    }
    
    # Return features for the specific system and image, or empty dict if not found
    return features.get(system, {}).get(image_name, {})
