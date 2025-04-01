import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from logging_config import configure_logging

# Set up logging
logger = configure_logging()('image_utils')

# Define required image directories
REQUIRED_DIRECTORIES = [
    'static/images',
    'static/images/histology',
    'static/images/histology/lymphatic',
    'static/images/histology/respiratory',
    'static/images/histology/digestive',
    'static/images/diagrams',
    'data/knowledge',
    'data/user_progress'
]

def ensure_directories_exist():
    """
    Ensures all required image and data directories exist
    Returns whether all directories were successfully verified
    """
    success = True
    for directory in REQUIRED_DIRECTORIES:
        try:
            if not os.path.exists(directory):
                logger.info(f"Creating missing directory: {directory}")
                os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {str(e)}")
            success = False
    return success

def get_image_path(category, system, image_name):
    """
    Gets the appropriate path for an image with error handling and cross-platform support
    
    Args:
        category: The image category (histology, diagram)
        system: The anatomical system (lymphatic, respiratory, digestive)
        image_name: The specific image name
        
    Returns:
        Full path to the image
    """
    # Define the image path using os.path.join for cross-platform compatibility
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if category == 'histology':
        img_path = os.path.join(base_dir, 'static', 'images', 'histology', system, f"{image_name}.png")
    else:  # diagrams
        img_path = os.path.join(base_dir, 'static', 'images', f"{system}_{image_name}.png")
        
    # Check if the image exists, generate placeholder if it doesn't
    if not os.path.exists(img_path):
        logger.warning(f"Image not found: {img_path}")
        placeholder_dir = os.path.dirname(img_path)
        os.makedirs(placeholder_dir, exist_ok=True)
        create_placeholder_image(img_path, system, image_name)
        
    return img_path

def create_placeholder_image(img_path, system, image_name):
    """
    Creates a placeholder image with informative text
    
    Args:
        img_path: Path where the image should be saved
        system: The anatomical system name
        image_name: The specific structure name
    """
    try:
        # Create a placeholder image with a light gray background
        img = Image.new('RGB', (400, 300), (240, 240, 240))
        
        # Add informative text
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("Arial", 20)
        except:
            font = ImageFont.load_default()
        
        # Create formatted text
        title = f"{system.replace('_', ' ').title()}"
        subtitle = f"{image_name.replace('_', ' ').title()}"
        message = "Placeholder Image\nContent Not Available"
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((400 - title_width) // 2, 60), title, font=font, fill=(0, 0, 0))
        
        # Draw subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((400 - subtitle_width) // 2, 100), subtitle, font=font, fill=(0, 0, 0))
        
        # Draw message
        message_bbox = draw.textbbox((0, 0), message, font=font)
        message_width = message_bbox[2] - message_bbox[0]
        message_height = message_bbox[3] - message_bbox[1]
        draw.text(((400 - message_width) // 2, (300 - message_height) // 2 + 50), 
                 message, font=font, fill=(200, 0, 0), align="center")
        
        # Add border
        for i in range(5):
            draw.rectangle([(i, i), (399-i, 299-i)], outline=(100, 100, 100))
        
        # Save the image
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        img.save(img_path)
        logger.info(f"Created placeholder image: {img_path}")
    except Exception as e:
        logger.error(f"Failed to create placeholder image {img_path}: {str(e)}")

def validate_image_resources():
    """
    Validates that all required image resources are available or can be generated
    Returns a dictionary with validation results
    """
    results = {
        "success": True,
        "directories_ok": False,
        "histology_images": {
            "lymphatic": [],
            "respiratory": [],
            "digestive": []
        },
        "diagram_images": [],
        "errors": []
    }
    
    # Check directories
    try:
        results["directories_ok"] = ensure_directories_exist()
        if not results["directories_ok"]:
            results["success"] = False
            results["errors"].append("Failed to create required directories")
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Directory validation error: {str(e)}")
    
    # Check for critical files and attempt to generate placeholders if needed
    systems = ["lymphatic", "respiratory", "digestive"]
    histology_images = {
        "lymphatic": ["thymus", "lymph_node", "spleen"],
        "respiratory": ["trachea", "lung"],
        "digestive": ["esophagus_stomach", "small_intestine"]
    }
    
    try:
        # Check histology images
        for system in systems:
            for image in histology_images.get(system, []):
                img_path = get_image_path("histology", system, image)
                if os.path.exists(img_path):
                    results["histology_images"][system].append(image)
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Histology image validation error: {str(e)}")
    
    # Check diagram images (base images for each system)
    try:
        for system in systems:
            img_path = get_image_path("diagram", system, "base")
            if os.path.exists(img_path):
                results["diagram_images"].append(f"{system}_base")
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Diagram image validation error: {str(e)}")
    
    return results

def cleanup_image_paths(code_file):
    """
    Updates image paths in a code file for cross-platform compatibility
    This is a utility function for deployment preparation
    
    Args:
        code_file: Path to the Python file to update
    """
    try:
        with open(code_file, 'r') as file:
            content = file.read()
        
        # Replace hardcoded image paths with os.path.join
        # This is a simplified approach - for production you'd use AST parsing
        content = content.replace(
            'img_path = f"static/images/histology/{section}/{image_data[\'name\']}.png"',
            'img_path = os.path.join("static", "images", "histology", section, f"{image_data[\'name\']}.png")'
        )
        content = content.replace(
            'path = f"static/images/{diagram_type}_{structure}.png"',
            'path = os.path.join("static", "images", f"{diagram_type}_{structure}.png")'
        )
        
        with open(code_file, 'w') as file:
            file.write(content)
            
        logger.info(f"Updated image paths in {code_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to update image paths in {code_file}: {str(e)}")
        return False
