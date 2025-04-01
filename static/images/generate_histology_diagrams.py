from PIL import Image, ImageDraw, ImageFont
import os
import random
import math

def generate_scale_bar(draw, width, height, font):
    """Generate a scale bar in the bottom right corner"""
    # Draw scale bar
    bar_width = 100
    bar_height = 5
    draw.rectangle(
        [(width - 120, height - 40), (width - 120 + bar_width, height - 40 + bar_height)],
        fill=(0, 0, 0)
    )
    
    # Draw scale label
    scale_text = "100 μm"
    draw.text((width - 120 + bar_width/2 - 25, height - 40 + bar_height + 5), 
              scale_text, font=font, fill=(0, 0, 0))

def create_thymus_image(width, height, base_color):
    """Create a realistic thymus histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create cortex region (darker) and medulla region (lighter)
    for y in range(height):
        for x in range(width):
            # Calculate distance from center
            center_x, center_y = width//2, height//2
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # Create a lobular pattern characteristic of thymus
            angle = math.atan2(y - center_y, x - center_x)
            
            # Create several thymic lobules with cortex (outer) and medulla (inner)
            for i in range(3):
                lobe_angle = i * 2 * math.pi / 3
                lobe_x = center_x + 150 * math.cos(lobe_angle)
                lobe_y = center_y + 150 * math.sin(lobe_angle)
                lobe_dist = math.sqrt((x - lobe_x)**2 + (y - lobe_y)**2)
                
                if lobe_dist < 120:  # Inside a lobule
                    if lobe_dist < 60:  # Medulla (lighter)
                        color = (240, 240, 255)
                    else:  # Cortex (darker, more lymphocytes)
                        color = (200, 200, 230)
                    
                    # Add texture and cells
                    r_jitter = random.randint(-15, 15)
                    g_jitter = random.randint(-15, 15)
                    b_jitter = random.randint(-15, 15)
                    
                    pixel_color = (
                        max(0, min(255, color[0] + r_jitter)),
                        max(0, min(255, color[1] + g_jitter)),
                        max(0, min(255, color[2] + b_jitter))
                    )
                    
                    img.putpixel((x, y), pixel_color)
    
    # Add cellular details - thymocytes (T cells in development)
    for _ in range(3000):
        lobe_idx = random.randint(0, 2)
        lobe_angle = lobe_idx * 2 * math.pi / 3
        
        # More cells in cortex than medulla
        if random.random() < 0.7:  # Cortex cells
            radius = random.uniform(60, 120)
        else:  # Medulla cells
            radius = random.uniform(0, 60)
            
        angle = random.uniform(0, 2*math.pi)
        lobe_x = width//2 + 150 * math.cos(lobe_angle)
        lobe_y = height//2 + 150 * math.sin(lobe_angle)
        
        x = int(lobe_x + radius * math.cos(angle))
        y = int(lobe_y + radius * math.sin(angle))
        
        if 0 <= x < width and 0 <= y < height:
            # T cells are small and round
            size = random.randint(1, 3)
            cell_color = (80, 80, 160) if random.random() < 0.8 else (100, 100, 200)
            
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=cell_color)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 20)
    except:
        label_font = ImageFont.load_default()
    
    # Draw labels
    draw.text((width//2 - 150, height//2 - 10), "Medulla", font=label_font, fill=(0, 0, 0))
    draw.text((width//2 + 50, height//2 + 80), "Cortex", font=label_font, fill=(0, 0, 0))
    draw.text((width//2, height//2 - 120), "Thymic Lobule", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_lymph_node_image(width, height, base_color):
    """Create a realistic lymph node histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create basic structure
    center_x, center_y = width//2, height//2
    radius = min(width, height) // 2 - 50
    
    # Draw lymph node outer capsule
    capsule_color = (180, 180, 200)
    capsule_width = 15
    draw.ellipse([(center_x - radius, center_y - radius), 
                  (center_x + radius, center_y + radius)], 
                 outline=(100, 100, 120), width=capsule_width)
    
    # Create cortex, paracortex and medulla with different densities
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            if dist < radius:
                if dist < radius * 0.4:  # Medulla
                    base = (235, 235, 250)
                elif dist < radius * 0.7:  # Paracortex
                    base = (215, 215, 235)
                else:  # Cortex
                    base = (195, 195, 225)
                
                # Add texture
                r_jitter = random.randint(-15, 15)
                g_jitter = random.randint(-15, 15)
                b_jitter = random.randint(-15, 15)
                
                pixel_color = (
                    max(0, min(255, base[0] + r_jitter)),
                    max(0, min(255, base[1] + g_jitter)),
                    max(0, min(255, base[2] + b_jitter))
                )
                
                img.putpixel((x, y), pixel_color)
    
    # Add germinal centers in cortex (3-4 circular structures)
    for i in range(4):
        angle = i * math.pi / 2
        gc_distance = radius * 0.8
        gc_x = int(center_x + gc_distance * math.cos(angle))
        gc_y = int(center_y + gc_distance * math.sin(angle))
        gc_radius = radius * 0.15
        
        # Draw the germinal center
        for y in range(max(0, gc_y - int(gc_radius)), min(height, gc_y + int(gc_radius))):
            for x in range(max(0, gc_x - int(gc_radius)), min(width, gc_x + int(gc_radius))):
                dist = math.sqrt((x - gc_x)**2 + (y - gc_y)**2)
                if dist < gc_radius:
                    # Lighter color for germinal center
                    base = (230, 230, 250)
                    
                    # Add texture
                    r_jitter = random.randint(-10, 10)
                    g_jitter = random.randint(-10, 10)
                    b_jitter = random.randint(-10, 10)
                    
                    pixel_color = (
                        max(0, min(255, base[0] + r_jitter)),
                        max(0, min(255, base[1] + g_jitter)),
                        max(0, min(255, base[2] + b_jitter))
                    )
                    
                    img.putpixel((x, y), pixel_color)
    
    # Add lymphocytes (B and T cells)
    for _ in range(8000):
        dist_factor = random.random()
        angle = random.uniform(0, 2*math.pi)
        
        if dist_factor < 0.4:  # Medulla (fewer cells)
            radius_factor = random.uniform(0, 0.4)
        elif dist_factor < 0.7:  # Paracortex (T cell zone)
            radius_factor = random.uniform(0.4, 0.7)
        else:  # Cortex (B cell zone)
            radius_factor = random.uniform(0.7, 0.95)
            
        x = int(center_x + radius * radius_factor * math.cos(angle))
        y = int(center_y + radius * radius_factor * math.sin(angle))
        
        if 0 <= x < width and 0 <= y < height:
            # Different colors for B and T cells
            if radius_factor > 0.7:  # B cells in cortex
                cell_color = (100, 100, 180) if random.random() < 0.8 else (120, 120, 200)
            else:  # T cells in paracortex
                cell_color = (80, 120, 160) if random.random() < 0.8 else (100, 140, 180)
                
            size = random.randint(1, 3)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=cell_color)
    
    # Add afferent and efferent lymphatic vessels
    # Afferent vessels (multiple, enter at different angles)
    for i in range(3):
        angle = i * 2 * math.pi / 3 + math.pi/6
        vessel_start_x = int(center_x + (radius + 20) * math.cos(angle))
        vessel_start_y = int(center_y + (radius + 20) * math.sin(angle))
        vessel_end_x = int(center_x + radius * math.cos(angle))
        vessel_end_y = int(center_y + radius * math.sin(angle))
        
        draw.line([(vessel_start_x, vessel_start_y), (vessel_end_x, vessel_end_y)], 
                  fill=(150, 150, 220), width=8)
    
    # Efferent vessel (single, exits at hilum)
    hilum_angle = 5 * math.pi / 4
    vessel_start_x = int(center_x + radius * math.cos(hilum_angle))
    vessel_start_y = int(center_y + radius * math.sin(hilum_angle))
    vessel_end_x = int(center_x + (radius + 60) * math.cos(hilum_angle))
    vessel_end_y = int(center_y + (radius + 60) * math.sin(hilum_angle))
    
    draw.line([(vessel_start_x, vessel_start_y), (vessel_end_x, vessel_end_y)], 
              fill=(150, 150, 220), width=12)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 18)
    except:
        label_font = ImageFont.load_default()
    
    # Draw labels
    draw.text((center_x - 30, center_y - 20), "Medulla", font=label_font, fill=(0, 0, 0))
    draw.text((center_x - 100, center_y - 100), "Paracortex", font=label_font, fill=(0, 0, 0))
    draw.text((center_x + 60, center_y + 80), "Cortex", font=label_font, fill=(0, 0, 0))
    draw.text((gc_x - 60, gc_y - 10), "Germinal Center", font=label_font, fill=(0, 0, 0))
    draw.text((center_x - radius - 80, center_y - radius - 10), "Capsule", font=label_font, fill=(0, 0, 0))
    draw.text((vessel_start_x + 20, vessel_start_y - 40), "Efferent Vessel", font=label_font, fill=(0, 0, 0))
    draw.text((vessel_start_x - 160, vessel_start_y + 60), "Afferent Vessels", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_spleen_image(width, height, base_color):
    """Create a realistic spleen histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create white pulp and red pulp regions
    for y in range(height):
        for x in range(width):
            # Create a pattern of white pulp surrounded by red pulp
            # Use perlin noise-like effect for natural transitions
            noise_val = (math.sin(x/20) + math.sin(y/20) + 
                         math.sin((x+y)/25) + math.sin(math.sqrt(x*x + y*y)/30)) / 4
            
            if noise_val > 0.2:  # White pulp areas
                base = (225, 225, 245)
            else:  # Red pulp areas
                base = (245, 220, 220)
            
            # Add texture
            r_jitter = random.randint(-15, 15)
            g_jitter = random.randint(-15, 15)
            b_jitter = random.randint(-15, 15)
            
            pixel_color = (
                max(0, min(255, base[0] + r_jitter)),
                max(0, min(255, base[1] + g_jitter)),
                max(0, min(255, base[2] + b_jitter))
            )
            
            img.putpixel((x, y), pixel_color)
    
    # Add cellular details
    # Red blood cells in red pulp
    for _ in range(6000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        
        # Check if in red pulp region
        noise_val = (math.sin(x/20) + math.sin(y/20) + 
                     math.sin((x+y)/25) + math.sin(math.sqrt(x*x + y*y)/30)) / 4
        
        if noise_val <= 0.2:  # Red pulp
            # Red blood cells
            size = random.randint(2, 4)
            # Variation in red blood cell color
            cell_color = (
                random.randint(180, 220),
                random.randint(50, 90),
                random.randint(50, 90)
            )
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=cell_color)
    
    # Lymphocytes in white pulp
    for _ in range(4000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        
        # Check if in white pulp region
        noise_val = (math.sin(x/20) + math.sin(y/20) + 
                     math.sin((x+y)/25) + math.sin(math.sqrt(x*x + y*y)/30)) / 4
        
        if noise_val > 0.2:  # White pulp
            # Lymphocytes
            size = random.randint(1, 3)
            # Variation in lymphocyte color
            cell_color = (
                random.randint(80, 120),
                random.randint(80, 120),
                random.randint(160, 200)
            )
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=cell_color)
    
    # Add trabeculae (fibrous bands)
    for _ in range(5):
        start_x = random.randint(0, width-1)
        start_y = random.randint(0, height-1)
        end_x = random.randint(0, width-1)
        end_y = random.randint(0, height-1)
        
        # Make trabeculae thicker
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(180, 180, 200), width=15)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 20)
    except:
        label_font = ImageFont.load_default()
    
    # Label white and red pulp regions
    center_wp_x, center_wp_y = width//4, height//3
    draw.text((center_wp_x - 40, center_wp_y), "White Pulp", font=label_font, fill=(0, 0, 0))
    
    center_rp_x, center_rp_y = 3*width//4, 2*height//3
    draw.text((center_rp_x - 40, center_rp_y), "Red Pulp", font=label_font, fill=(0, 0, 0))
    
    # Label trabeculae
    draw.text((width//2, height//4 + 50), "Trabecula", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_trachea_image(width, height, base_color):
    """Create a realistic trachea histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create layered structure of trachea (from inside to outside)
    # 1. Pseudostratified ciliated columnar epithelium
    # 2. Lamina propria (connective tissue)
    # 3. Submucosal glands
    # 4. Hyaline cartilage (C-shape)
    # 5. Adventitia (outer layer)
    
    # Draw the C-shaped hyaline cartilage
    cartilage_color = (200, 230, 240)
    center_x, center_y = width//2, height//2
    outer_radius = min(width, height) // 2 - 50
    inner_radius = outer_radius - 70
    
    # Draw C-shaped cartilage
    start_angle = math.radians(210)
    end_angle = math.radians(150)
    
    # Fill the C-shaped cartilage
    for theta in range(210, 510):  # From 210 to 510 degrees
        if theta <= 510:  # Until 510 degrees (150 degrees)
            rad = math.radians(theta)
            for r in range(inner_radius, outer_radius):
                x = int(center_x + r * math.cos(rad))
                y = int(center_y + r * math.sin(rad))
                
                if 0 <= x < width and 0 <= y < height:
                    # Add texture to cartilage
                    r_jitter = random.randint(-20, 20)
                    g_jitter = random.randint(-20, 20)
                    b_jitter = random.randint(-20, 20)
                    
                    pixel_color = (
                        max(0, min(255, cartilage_color[0] + r_jitter)),
                        max(0, min(255, cartilage_color[1] + g_jitter)),
                        max(0, min(255, cartilage_color[2] + b_jitter))
                    )
                    
                    img.putpixel((x, y), pixel_color)
    
    # Draw lumen and epithelium
    lumen_radius = inner_radius - 40
    
    # Fill the lumen (airway)
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            if dist < lumen_radius:
                # Lumen (white/light pink)
                base = (250, 245, 245)
                
                # Add slight texture
                r_jitter = random.randint(-5, 5)
                g_jitter = random.randint(-5, 5)
                b_jitter = random.randint(-5, 5)
                
                pixel_color = (
                    max(0, min(255, base[0] + r_jitter)),
                    max(0, min(255, base[1] + g_jitter)),
                    max(0, min(255, base[2] + b_jitter))
                )
                
                img.putpixel((x, y), pixel_color)
            elif dist < lumen_radius + 15:
                # Epithelium layer
                base = (220, 180, 200)
                
                # Add texture
                r_jitter = random.randint(-15, 15)
                g_jitter = random.randint(-15, 15)
                b_jitter = random.randint(-15, 15)
                
                pixel_color = (
                    max(0, min(255, base[0] + r_jitter)),
                    max(0, min(255, base[1] + g_jitter)),
                    max(0, min(255, base[2] + b_jitter))
                )
                
                img.putpixel((x, y), pixel_color)
            elif dist < inner_radius and not (inner_radius <= dist <= outer_radius and 
                                              start_angle <= math.atan2(y - center_y, x - center_x) <= end_angle):
                # Lamina propria and submucosa (between epithelium and cartilage)
                base = (230, 210, 210)
                
                # Add texture
                r_jitter = random.randint(-15, 15)
                g_jitter = random.randint(-15, 15)
                b_jitter = random.randint(-15, 15)
                
                pixel_color = (
                    max(0, min(255, base[0] + r_jitter)),
                    max(0, min(255, base[1] + g_jitter)),
                    max(0, min(255, base[2] + b_jitter))
                )
                
                img.putpixel((x, y), pixel_color)
    
    # Add cilia to epithelium
    for theta in range(0, 360, 2):
        rad = math.radians(theta)
        x = int(center_x + lumen_radius * math.cos(rad))
        y = int(center_y + lumen_radius * math.sin(rad))
        
        # Cilia as tiny lines
        cilia_length = random.randint(2, 5)
        end_x = int(center_x + (lumen_radius - cilia_length) * math.cos(rad))
        end_y = int(center_y + (lumen_radius - cilia_length) * math.sin(rad))
        
        draw.line([(x, y), (end_x, end_y)], fill=(150, 100, 150), width=1)
    
    # Add submucosal glands
    for _ in range(15):
        angle = random.uniform(math.pi/2, 3*math.pi/2)  # Only on the side opposite to open part of C
        gland_dist = random.uniform(lumen_radius + 20, inner_radius - 10)
        gland_x = int(center_x + gland_dist * math.cos(angle))
        gland_y = int(center_y + gland_dist * math.sin(angle))
        gland_size = random.randint(5, 12)
        
        # Draw a circular gland
        draw.ellipse([(gland_x - gland_size, gland_y - gland_size), 
                       (gland_x + gland_size, gland_y + gland_size)], 
                      fill=(240, 190, 190))
    
    # Add chondrocytes in cartilage (small blue circles)
    for _ in range(200):
        angle = random.uniform(math.radians(210), math.radians(510))
        chondrocyte_dist = random.uniform(inner_radius + 10, outer_radius - 10)
        chondrocyte_x = int(center_x + chondrocyte_dist * math.cos(angle))
        chondrocyte_y = int(center_y + chondrocyte_dist * math.sin(angle))
        
        if 0 <= chondrocyte_x < width and 0 <= chondrocyte_y < height:
            chondrocyte_size = random.randint(2, 5)
            draw.ellipse([(chondrocyte_x - chondrocyte_size, chondrocyte_y - chondrocyte_size), 
                          (chondrocyte_x + chondrocyte_size, chondrocyte_y + chondrocyte_size)], 
                         fill=(160, 200, 220))
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 16)
        small_font = ImageFont.truetype("Arial", 14)
    except:
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw labels
    draw.text((center_x - 25, center_y - 20), "Lumen", font=label_font, fill=(0, 0, 0))
    draw.text((center_x - lumen_radius - 150, center_y - 10), 
              "Pseudostratified\nCiliated Epithelium", font=small_font, fill=(0, 0, 0))
    draw.text((center_x + 40, center_y - lumen_radius - 50), 
              "Lamina Propria", font=small_font, fill=(0, 0, 0))
    draw.text((center_x - 70, center_y + lumen_radius + 40), 
              "Submucosal Gland", font=small_font, fill=(0, 0, 0))
    draw.text((center_x - inner_radius - 60, center_y + inner_radius - 20), 
              "Hyaline Cartilage", font=label_font, fill=(0, 0, 0))
    draw.text((center_x + 80, center_y + inner_radius + 20), 
              "Chondrocyte", font=small_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_lung_image(width, height, base_color):
    """Create a realistic lung histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create basic lung parenchyma with alveoli
    # Add a bronchiole and blood vessels
    
    # First create the background lung tissue
    for y in range(height):
        for x in range(width):
            # Create a slightly textured background
            r_jitter = random.randint(-10, 10)
            g_jitter = random.randint(-10, 10)
            b_jitter = random.randint(-10, 10)
            
            pixel_color = (
                max(0, min(255, base_color[0] + r_jitter)),
                max(0, min(255, base_color[1] + g_jitter)),
                max(0, min(255, base_color[2] + b_jitter))
            )
            
            img.putpixel((x, y), pixel_color)
    
    # Add alveoli (numerous small air sacs)
    num_alveoli = 150
    alveoli_centers = []
    min_distance = 40  # Minimum distance between alveoli centers
    
    # Generate alveoli centers with minimum distance constraint
    for _ in range(num_alveoli):
        while True:
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            
            # Check distance from existing centers
            valid_position = True
            for cx, cy in alveoli_centers:
                if math.sqrt((x - cx)**2 + (y - cy)**2) < min_distance:
                    valid_position = False
                    break
            
            if valid_position:
                alveoli_centers.append((x, y))
                break
    
    # Draw alveoli
    for center_x, center_y in alveoli_centers:
        size = random.randint(10, 25)
        
        # Alveoli have irregular shapes rather than perfect circles
        # Create a slightly irregular shape by varying radius
        points = []
        num_points = 12
        for i in range(num_points):
            angle = i * 2 * math.pi / num_points
            radius_variation = random.uniform(0.8, 1.2)
            px = center_x + int(size * radius_variation * math.cos(angle))
            py = center_y + int(size * radius_variation * math.sin(angle))
            points.append((px, py))
        
        # Draw the irregular alveolus
        draw.polygon(points, fill=(250, 250, 250), outline=(200, 200, 210))
        
        # Add simple alveolar wall (with capillaries)
        for i in range(num_points):
            if random.random() < 0.7:  # Add some capillaries along the wall
                p1 = points[i]
                p2 = points[(i+1) % num_points]
                
                # Draw thicker alveolar wall section with a capillary
                mid_x = (p1[0] + p2[0]) // 2
                mid_y = (p1[1] + p2[1]) // 2
                
                # Draw a small red dot representing a capillary
                capillary_size = random.randint(2, 4)
                draw.ellipse([(mid_x - capillary_size, mid_y - capillary_size),
                              (mid_x + capillary_size, mid_y + capillary_size)],
                             fill=(220, 100, 100))
    
    # Add a bronchiole
    bronchiole_x, bronchiole_y = width//4, height//3
    bronchiole_radius = 60
    
    # Draw bronchiole lumen (center)
    draw.ellipse([(bronchiole_x - bronchiole_radius//2, bronchiole_y - bronchiole_radius//2),
                   (bronchiole_x + bronchiole_radius//2, bronchiole_y + bronchiole_radius//2)],
                  fill=(250, 250, 250))
    
    # Draw bronchiole wall
    draw.ellipse([(bronchiole_x - bronchiole_radius, bronchiole_y - bronchiole_radius),
                   (bronchiole_x + bronchiole_radius, bronchiole_y + bronchiole_radius)],
                  outline=(140, 100, 140), width=4)
    
    # Add folded epithelium in bronchiole
    for i in range(12):
        angle = i * 2 * math.pi / 12
        fold_length = bronchiole_radius//4
        start_x = bronchiole_x + int((bronchiole_radius//2) * math.cos(angle))
        start_y = bronchiole_y + int((bronchiole_radius//2) * math.sin(angle))
        end_x = bronchiole_x + int((bronchiole_radius//2 + fold_length) * math.cos(angle))
        end_y = bronchiole_y + int((bronchiole_radius//2 + fold_length) * math.sin(angle))
        
        # Draw epithelial fold
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(180, 140, 180), width=3)
    
    # Add a pulmonary blood vessel (artery)
    vessel_x, vessel_y = 3*width//4, 2*height//3
    vessel_radius = 50
    
    # Draw vessel lumen (center)
    draw.ellipse([(vessel_x - vessel_radius//2, vessel_y - vessel_radius//2),
                   (vessel_x + vessel_radius//2, vessel_y + vessel_radius//2)],
                  fill=(240, 200, 200))
    
    # Draw vessel wall (thicker than bronchiole)
    draw.ellipse([(vessel_x - vessel_radius, vessel_y - vessel_radius),
                   (vessel_x + vessel_radius, vessel_y + vessel_radius)],
                  outline=(160, 60, 60), width=6)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 16)
    except:
        label_font = ImageFont.load_default()
    
    # Draw labels
    draw.text((bronchiole_x - 40, bronchiole_y + bronchiole_radius + 10), 
              "Bronchiole", font=label_font, fill=(0, 0, 0))
    draw.text((vessel_x - 45, vessel_y + vessel_radius + 10), 
              "Blood Vessel", font=label_font, fill=(0, 0, 0))
    draw.text((width//2, height//4), 
              "Alveoli", font=label_font, fill=(0, 0, 0))
    draw.text((width//2 + 80, height//2), 
              "Capillary", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_esophagus_stomach_image(width, height, base_color):
    """Create a realistic esophagus-stomach junction histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a dividing line representing the junction
    junction_x = width // 2
    draw.line([(junction_x, 0), (junction_x, height)], fill=(100, 100, 100), width=2)
    
    # Left side: Esophagus with stratified squamous epithelium
    # Right side: Stomach with simple columnar epithelium
    
    # Create layers for both sides
    # 1. Mucosa (epithelium + lamina propria)
    # 2. Submucosa
    # 3. Muscularis externa
    # 4. Serosa/Adventitia
    
    # Layer heights
    mucosa_height = 120
    submucosa_height = 80
    muscularis_height = 150
    
    # Layer colors (base colors, will add texture)
    esophagus_epithelium_color = (220, 180, 180)
    stomach_epithelium_color = (200, 160, 180)
    lamina_propria_color = (210, 190, 200)
    submucosa_color = (230, 210, 210)
    muscularis_color = (200, 170, 170)
    serosa_color = (240, 230, 230)
    
    # Fill layers
    for y in range(height):
        for x in range(width):
            # Determine which side (esophagus or stomach)
            is_esophagus = x < junction_x
            
            # Define layer boundaries
            if y < mucosa_height:  # Mucosa layer
                if is_esophagus:
                    # Esophagus epithelium (stratified squamous)
                    # Create "layers" of squamous cells
                    cell_layer = y // 15  # Divide the mucosa into cell layers
                    layer_offset = y % 15  # Position within cell layer
                    
                    if layer_offset < 10:  # Cell body
                        base_color = list(esophagus_epithelium_color)
                        # Make deeper layers slightly darker
                        darkening = 10 * (cell_layer + 1)
                        base_color = [max(0, c - darkening) for c in base_color]
                    else:  # Cell boundary
                        base_color = [c - 30 for c in esophagus_epithelium_color]
                else:
                    # Stomach epithelium (simple columnar)
                    # Create column-like cells
                    column_x = x % 12  # Position within a columnar cell
                    
                    if 2 <= column_x <= 9:  # Cell body
                        base_color = stomach_epithelium_color
                        
                        # Add cell nuclei at the bottom of some columns
                        if column_x == 5 and 60 <= y <= 80:
                            base_color = (100, 100, 160)
                    else:  # Cell boundary
                        base_color = [c - 30 for c in stomach_epithelium_color]
                        
                    # Add gastric pits in stomach (invaginations)
                    gastric_pit_x = ((x - junction_x) // 50) * 50 + junction_x + 25
                    if abs(x - gastric_pit_x) < 15 and y > 40:
                        base_color = (250, 250, 250)  # Lumen of gastric pit
            
            elif y < mucosa_height + submucosa_height:  # Submucosa layer
                base_color = submucosa_color
                
                # Add blood vessels and connective tissue elements
                if random.random() < 0.01:
                    base_color = (220, 100, 100)  # Blood vessel
            
            elif y < mucosa_height + submucosa_height + muscularis_height:  # Muscularis layer
                # Add inner circular and outer longitudinal muscle layers
                rel_y = y - (mucosa_height + submucosa_height)
                is_circular = rel_y < muscularis_height // 2
                
                if is_circular:
                    # Inner circular muscle layer - patterns across x-axis
                    pattern = (x // 8) % 2
                    base_color = [c - 20 if pattern else c for c in muscularis_color]
                else:
                    # Outer longitudinal muscle layer - patterns along y-axis
                    pattern = (y // 8) % 2
                    base_color = [c - 20 if pattern else c for c in muscularis_color]
            
            else:  # Serosa/Adventitia layer
                base_color = serosa_color
            
            # Add texture
            r_jitter = random.randint(-15, 15)
            g_jitter = random.randint(-15, 15)
            b_jitter = random.randint(-15, 15)
            
            pixel_color = (
                max(0, min(255, base_color[0] + r_jitter)),
                max(0, min(255, base_color[1] + g_jitter)),
                max(0, min(255, base_color[2] + b_jitter))
            )
            
            img.putpixel((x, y), pixel_color)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 16)
        title_font = ImageFont.truetype("Arial", 20)
    except:
        label_font = ImageFont.load_default()
        title_font = label_font
    
    # Draw titles for each side
    draw.text((junction_x//2 - 50, 10), "Esophagus", font=title_font, fill=(0, 0, 0))
    draw.text((junction_x + junction_x//2 - 40, 10), "Stomach", font=title_font, fill=(0, 0, 0))
    
    # Draw layer labels
    draw.text((10, mucosa_height//2), "Stratified Squamous\nEpithelium", font=label_font, fill=(0, 0, 0))
    draw.text((width - 180, mucosa_height//2), "Simple Columnar\nEpithelium", font=label_font, fill=(0, 0, 0))
    draw.text((width//2 - 40, mucosa_height + 20), "Submucosa", font=label_font, fill=(0, 0, 0))
    draw.text((width//2 - 130, mucosa_height + submucosa_height + 30), "Muscularis\n(Inner Circular)", 
              font=label_font, fill=(0, 0, 0))
    draw.text((width//2 - 140, mucosa_height + submucosa_height + muscularis_height//2 + 30), 
              "Muscularis\n(Outer Longitudinal)", font=label_font, fill=(0, 0, 0))
    draw.text((width//2 - 40, mucosa_height + submucosa_height + muscularis_height + 20), 
              "Serosa", font=label_font, fill=(0, 0, 0))
    
    # Label gastric pits
    draw.text((width - 140, mucosa_height - 50), "Gastric Pit", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def create_small_intestine_image(width, height, base_color):
    """Create a realistic small intestine histology image"""
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create small intestine with:
    # 1. Villi (finger-like projections)
    # 2. Crypts of Lieberkühn (tubular glands)
    # 3. Simple columnar epithelium with goblet cells
    # 4. Lamina propria, muscularis mucosa, submucosa, muscularis
    
    # Create basic tissue layers
    mucosa_height = height - 200  # Leave space for villi to project upward
    lumen_color = (250, 250, 250)  # Lumen is white/very light
    
    # Fill the lumen area
    for y in range(mucosa_height):
        for x in range(width):
            # Add some texture to lumen
            r_jitter = random.randint(-5, 5)
            g_jitter = random.randint(-5, 5)
            b_jitter = random.randint(-5, 5)
            
            pixel_color = (
                max(0, min(255, lumen_color[0] + r_jitter)),
                max(0, min(255, lumen_color[1] + g_jitter)),
                max(0, min(255, lumen_color[2] + b_jitter))
            )
            
            img.putpixel((x, y), pixel_color)
    
    # Create tissue layers beneath mucosa
    for y in range(mucosa_height, height):
        for x in range(width):
            # Define different tissue layers
            if y < mucosa_height + 30:  # Muscularis mucosae
                base_color = (210, 180, 180)
            elif y < mucosa_height + 90:  # Submucosa
                base_color = (220, 200, 200)
            elif y < mucosa_height + 150:  # Muscularis (circular)
                base_color = (200, 170, 170)
            elif y < mucosa_height + 200:  # Muscularis (longitudinal)
                base_color = (190, 160, 160)
            else:  # Serosa
                base_color = (230, 220, 220)
            
            # Add texture
            r_jitter = random.randint(-15, 15)
            g_jitter = random.randint(-15, 15)
            b_jitter = random.randint(-15, 15)
            
            pixel_color = (
                max(0, min(255, base_color[0] + r_jitter)),
                max(0, min(255, base_color[1] + g_jitter)),
                max(0, min(255, base_color[2] + b_jitter))
            )
            
            img.putpixel((x, y), pixel_color)
    
    # Add villi (finger-like projections)
    villi_width = 60
    num_villi = width // villi_width
    
    for i in range(num_villi):
        # Calculate villus center
        villus_x = i * villi_width + villi_width // 2
        villus_base_y = mucosa_height
        villus_height = random.randint(150, 180)
        villus_tip_y = villus_base_y - villus_height
        
        # Draw villus shape (finger-like projection)
        points = []
        # Left side of villus
        for y in range(villus_tip_y, villus_base_y, 10):
            # Create slightly irregular edge
            x_offset = random.randint(-5, 5)
            rel_height = (y - villus_tip_y) / (villus_base_y - villus_tip_y)
            width_factor = 0.3 + 0.7 * rel_height  # Wider at base, narrower at tip
            x = villus_x - int(villi_width//2 * width_factor) + x_offset
            points.append((x, y))
        
        # Right side of villus (going back up)
        for y in range(villus_base_y, villus_tip_y, -10):
            # Create slightly irregular edge
            x_offset = random.randint(-5, 5)
            rel_height = (y - villus_tip_y) / (villus_base_y - villus_tip_y)
            width_factor = 0.3 + 0.7 * rel_height  # Wider at base, narrower at tip
            x = villus_x + int(villi_width//2 * width_factor) + x_offset
            points.append((x, y))
        
        # Draw the villus
        draw.polygon(points, fill=(220, 190, 190), outline=(200, 170, 170))
        
        # Add columnar epithelium cells along the edge
        prev_point = points[0]
        for point in points[1:]:
            # Draw line segments with brush-border effect
            draw.line([prev_point, point], fill=(180, 150, 150), width=3)
            prev_point = point
            
            # Add goblet cells (randomly)
            if random.random() < 0.2:
                goblet_x = (prev_point[0] + point[0]) // 2
                goblet_y = (prev_point[1] + point[1]) // 2
                goblet_size = random.randint(3, 6)
                
                # Draw goblet cell (oval shape)
                draw.ellipse([(goblet_x - goblet_size, goblet_y - goblet_size),
                              (goblet_x + goblet_size, goblet_y + goblet_size)],
                             fill=(220, 220, 250))
    
    # Add crypts of Lieberkühn (tubular glands between villi bases)
    for i in range(num_villi - 1):
        crypt_x = (i + 1) * villi_width
        crypt_top_y = mucosa_height
        crypt_depth = random.randint(40, 60)
        crypt_bottom_y = crypt_top_y + crypt_depth
        crypt_width = 15
        
        # Draw crypt lumen (vertical tubular structure)
        draw.rectangle([(crypt_x - crypt_width//2, crypt_top_y),
                         (crypt_x + crypt_width//2, crypt_bottom_y)],
                        fill=(240, 240, 240), outline=(200, 180, 180))
        
        # Add epithelial cells around the crypt
        for y in range(crypt_top_y, crypt_bottom_y, 8):
            # Left side cells
            cell_x = crypt_x - crypt_width//2 - 4
            cell_y = y
            draw.ellipse([(cell_x - 4, cell_y - 4), (cell_x + 4, cell_y + 4)],
                         fill=(200, 170, 170))
            
            # Right side cells
            cell_x = crypt_x + crypt_width//2 + 4
            draw.ellipse([(cell_x - 4, cell_y - 4), (cell_x + 4, cell_y + 4)],
                         fill=(200, 170, 170))
    
    # Add blood vessels in lamina propria (inside villi)
    for i in range(num_villi):
        villus_x = i * villi_width + villi_width // 2
        villus_base_y = mucosa_height
        villus_height = random.randint(150, 180)
        villus_tip_y = villus_base_y - villus_height
        
        # Add a central blood vessel/lacteal
        vessel_start_y = villus_base_y - 20
        vessel_end_y = villus_tip_y + 30
        
        # Draw the vessel
        draw.line([(villus_x, vessel_start_y), (villus_x, vessel_end_y)],
                  fill=(220, 150, 150), width=6)
    
    # Add labels
    try:
        label_font = ImageFont.truetype("Arial", 16)
    except:
        label_font = ImageFont.load_default()
    
    # Draw labels
    # Villi labels
    draw.text((width//4, mucosa_height - 140), 
              "Villus", font=label_font, fill=(0, 0, 0))
    
    # Goblet cell label
    draw.text((width//2 + 70, mucosa_height - 120), 
              "Goblet Cell", font=label_font, fill=(0, 0, 0))
    
    # Crypt label
    draw.text((width//2 - 20, mucosa_height + 20), 
              "Crypt of Lieberkühn", font=label_font, fill=(0, 0, 0))
    
    # Blood vessel label
    draw.text((width//4 - 60, mucosa_height - 80), 
              "Blood Vessel/Lacteal", font=label_font, fill=(0, 0, 0))
    
    # Layer labels
    draw.text((10, mucosa_height + 10), 
              "Muscularis Mucosae", font=label_font, fill=(0, 0, 0))
    draw.text((10, mucosa_height + 50), 
              "Submucosa", font=label_font, fill=(0, 0, 0))
    draw.text((10, mucosa_height + 120), 
              "Muscularis Externa", font=label_font, fill=(0, 0, 0))
    draw.text((10, mucosa_height + 180), 
              "Serosa", font=label_font, fill=(0, 0, 0))
    
    # Columnar epithelium label
    draw.text((3*width//4, mucosa_height - 180), 
              "Simple Columnar\nEpithelium", font=label_font, fill=(0, 0, 0))
    
    # Add scale bar
    generate_scale_bar(draw, width, height, label_font)
    
    return img

def generate_histology_images():
    """Generate detailed histology images for anatomy study app"""
    
    # Define the histology images we need
    histology_images = {
        "lymphatic": [
            {"name": "thymus", "title": "Thymus Histology", "color": (230, 240, 255)},
            {"name": "lymph_node", "title": "Lymph Node Histology", "color": (230, 240, 255)},
            {"name": "spleen", "title": "Spleen Histology", "color": (230, 240, 255)}
        ],
        "respiratory": [
            {"name": "trachea", "title": "Trachea Histology", "color": (255, 240, 240)},
            {"name": "lung", "title": "Lung Histology", "color": (255, 240, 240)}
        ],
        "digestive": [
            {"name": "esophagus_stomach", "title": "Esophagus-Stomach Junction", "color": (240, 255, 240)},
            {"name": "small_intestine", "title": "Small Intestine", "color": (240, 255, 240)}
        ]
    }
    
    # Define image dimensions
    width, height = 800, 600
    
    # Create base directory if it doesn't exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the histology images
    for system, images in histology_images.items():
        # Ensure system directory exists
        system_dir = os.path.join(base_dir, "histology", system)
        os.makedirs(system_dir, exist_ok=True)
        
        for img_info in images:
            img_path = os.path.join(system_dir, f"{img_info['name']}.png")
            base_color = img_info['color']
            
            # Create specific tissue type image
            if img_info['name'] == 'thymus':
                img = create_thymus_image(width, height, base_color)
            elif img_info['name'] == 'lymph_node':
                img = create_lymph_node_image(width, height, base_color)
            elif img_info['name'] == 'spleen':
                img = create_spleen_image(width, height, base_color)
            elif img_info['name'] == 'trachea':
                img = create_trachea_image(width, height, base_color)
            elif img_info['name'] == 'lung':
                img = create_lung_image(width, height, base_color)
            elif img_info['name'] == 'esophagus_stomach':
                img = create_esophagus_stomach_image(width, height, base_color)
            elif img_info['name'] == 'small_intestine':
                img = create_small_intestine_image(width, height, base_color)
            
            # Add title
            draw = ImageDraw.Draw(img)
            try:
                title_font = ImageFont.truetype("Arial", 24)
            except:
                title_font = ImageFont.load_default()
            
            title_text = img_info['title']
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((width - title_width) // 2, 10), title_text, font=title_font, fill=(0, 0, 0))
            
            # Save the image
            img.save(img_path)
            print(f"Created {img_path}")

if __name__ == "__main__":
    generate_histology_images()