from PIL import Image, ImageDraw, ImageFont
import os

def generate_histology_placeholders():
    """Generate placeholder histology images until actual histology slides from PDF can be extracted"""
    
    # Define the histology images we need based on the requirements
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
    
    # Create base directory if it doesn't exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the placeholder images
    for system, images in histology_images.items():
        # Ensure system directory exists
        system_dir = os.path.join(base_dir, "histology", system)
        os.makedirs(system_dir, exist_ok=True)
        
        for img_info in images:
            img_path = os.path.join(system_dir, f"{img_info['name']}.png")
            
            # Create a colored image as placeholder
            # Use different base colors for different systems
            if system == "lymphatic":
                base_color = (230, 240, 255)  # Light blue
            elif system == "respiratory":
                base_color = (255, 240, 240)  # Light red
            elif system == "digestive":
                base_color = (240, 255, 240)  # Light green
            
            # Create the image
            img = Image.new('RGB', (800, 600), base_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fall back to default if not available
            try:
                title_font = ImageFont.truetype("Arial", 40)
                desc_font = ImageFont.truetype("Arial", 20)
            except:
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
            
            # Add title
            title_text = img_info['title']
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_position = ((800 - title_width) // 2, 50)
            draw.text(title_position, title_text, font=title_font, fill=(0, 0, 0))
            
            # Add description
            desc_text = img_info['description']
            desc_bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
            desc_width = desc_bbox[2] - desc_bbox[0]
            desc_position = ((800 - desc_width) // 2, 120)
            draw.text(desc_position, desc_text, font=desc_font, fill=(0, 0, 0))
            
            # Add placeholder grid pattern to simulate histology
            # Draw horizontal lines
            for y in range(200, 550, 20):
                draw.line([(100, y), (700, y)], fill=(80, 80, 80), width=1)
            
            # Draw vertical lines
            for x in range(100, 750, 20):
                draw.line([(x, 200), (x, 550)], fill=(80, 80, 80), width=1)
            
            # Add some "cell-like" structures
            import random
            for _ in range(100):
                x = random.randint(120, 680)
                y = random.randint(220, 530)
                size = random.randint(5, 15)
                # Use different colors for different types of cells
                if random.random() < 0.3:
                    cell_color = (100, 100, 200)  # Blue cells
                elif random.random() < 0.6:
                    cell_color = (200, 100, 100)  # Red cells
                else:
                    cell_color = (100, 200, 100)  # Green cells
                
                draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=cell_color)
            
            # Add note about placeholder
            note_text = "Placeholder image - Replace with actual histology from PDF"
            note_bbox = draw.textbbox((0, 0), note_text, font=desc_font)
            note_width = note_bbox[2] - note_bbox[0]
            note_position = ((800 - note_width) // 2, 570)
            draw.text(note_position, note_text, font=desc_font, fill=(150, 0, 0))
            
            # Save the image
            img.save(img_path)
            print(f"Created {img_path}")

if __name__ == "__main__":
    generate_histology_placeholders()
