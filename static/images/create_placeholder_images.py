from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_images():
    """Create placeholder images for the study app"""
    placeholders_path = os.path.dirname(os.path.abspath(__file__))
    
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
            img_path = os.path.join(placeholders_path, f"{diagram}_{part}.png")
            
            # Create a colored image as placeholder
            img = Image.new('RGB', (600, 400), colors.get(part, (240, 240, 240)))
            
            # Add text indicating this is a placeholder
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("Arial", 30)
            except:
                font = ImageFont.load_default()
            
            text = f"{diagram.replace('_', ' ').title()}\n{part.replace('_', ' ').title()}"
            
            # Add text in center
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = ((600 - text_width) // 2, (400 - text_height) // 2)
            draw.text(position, text, font=font, fill=(0, 0, 0))
            
            # For highlighted parts, add a border
            if part != "base":
                for i in range(5):
                    draw.rectangle([(i, i), (599-i, 399-i)], outline=(255, 0, 0))
            
            # Create a special labeled version for identification questions
            if part == "germinal_center" and diagram == "lymph_node":
                labeled_img_path = os.path.join(placeholders_path, f"{diagram}_labeled.png")
                labeled_img = img.copy()
                labeled_draw = ImageDraw.Draw(labeled_img)
                
                # Add arrow pointing to the center with a question mark
                arrow_start = (500, 50)
                arrow_end = (400, 200)
                labeled_draw.line([arrow_start, arrow_end], fill=(255, 0, 0), width=3)
                
                # Add "?" label
                labeled_draw.text((arrow_start[0] + 10, arrow_start[1] - 30), "?", font=font, fill=(255, 0, 0))
                
                labeled_img.save(labeled_img_path)
            
            # Save the image
            img.save(img_path)

if __name__ == "__main__":
    create_placeholder_images()
