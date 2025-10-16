#!/usr/bin/env python3
"""
Card Graphics Module

This module contains all image manipulation and drawing functions
for the character card generator, including gradient creation,
text effects, and card layout composition.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional, Tuple
from card_styles import get_custom_type_colors, get_category_fonts


def create_gradient_background(width: int, height: int, color1: str, color2: str, direction: str = 'vertical') -> Image.Image:
    """
    Create a gradient background image.
    
    Args:
        width (int): Image width
        height (int): Image height
        color1 (str): Start color (hex)
        color2 (str): End color (hex)
        direction (str): 'vertical' or 'horizontal'
        
    Returns:
        PIL.Image: Gradient background
    """
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    gradient = Image.new('RGB', (width, height))
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)
            for x in range(width):
                gradient.putpixel((x, y), (r, g, b))
    else:  # horizontal
        for x in range(width):
            ratio = x / width
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)
            for y in range(height):
                gradient.putpixel((x, y), (r, g, b))
    
    return gradient


def create_rounded_rectangle_mask(width: int, height: int, radius: int) -> Image.Image:
    """
    Create a mask for rounded rectangles.
    
    Args:
        width (int): Rectangle width
        height (int): Rectangle height
        radius (int): Corner radius
        
    Returns:
        PIL.Image: Alpha mask for rounded rectangle
    """
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
    return mask


def add_text_shadow(draw: ImageDraw.Draw, text: str, position: Tuple[int, int], font: ImageFont.FreeTypeFont, 
                   fill_color: Any, shadow_color: Any, shadow_offset: Tuple[int, int] = (2, 2)) -> None:
    """
    Add shadow effect to text.
    
    Args:
        draw: ImageDraw object
        text (str): Text to draw
        position (tuple): (x, y) position
        font: PIL Font object
        fill_color: Text color
        shadow_color: Shadow color
        shadow_offset (tuple): (x, y) offset for shadow
    """
    # Draw shadow
    shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    draw.text(shadow_pos, text, fill=shadow_color, font=font)
    # Draw main text
    draw.text(position, text, fill=fill_color, font=font)


def create_texture_overlay(width: int, height: int, category: str) -> Image.Image:
    """
    Create category-specific texture overlay.
    
    Args:
        width (int): Overlay width
        height (int): Overlay height
        category (str): Character category
        
    Returns:
        PIL.Image: Texture overlay with alpha
    """
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    if category == 'mystical':
        # Add star-like pattern
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            overlay_draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 255, 30))
    elif category == 'chaotic':
        # Add lightning-like pattern
        for _ in range(10):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-20, 20)
            y2 = y1 + random.randint(10, 30)
            overlay_draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 40), width=2)
    elif category == 'fierce':
        # Add flame-like pattern
        for _ in range(15):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 5)
            overlay_draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 100, 0, 25))
    elif category == 'wise':
        # Add subtle geometric pattern
        for _ in range(25):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 2)
            overlay_draw.rectangle([x-size, y-size, x+size, y+size], fill=(255, 255, 255, 20))
    
    return overlay


def apply_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """
    Apply rounded corners to an image.
    
    Args:
        image: PIL Image object
        radius (int): Corner radius in pixels
        
    Returns:
        PIL.Image: Image with rounded corners and transparent background
    """
    # Create a mask for rounded corners
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, image.size[0], image.size[1]], radius=radius, fill=255)
    
    # Convert image to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create output image with transparency
    output = Image.new('RGBA', image.size, (0, 0, 0, 0))
    output.paste(image, (0, 0))
    output.putalpha(mask)
    
    return output


def draw_rounded_rectangle(draw: ImageDraw.Draw, xy: list, radius: int, fill: Any = None, 
                          outline: Any = None, width: int = 1) -> None:
    """
    Draw a rounded rectangle on the canvas.
    
    Args:
        draw: ImageDraw object
        xy: Coordinates [x1, y1, x2, y2]
        radius (int): Corner radius
        fill: Fill color
        outline: Outline color
        width (int): Outline width
    """
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def create_unified_card(canvas: Image.Image, draw: ImageDraw.Draw, source_image_path: str, 
                       card_data: Dict[str, Any], colors: Dict[str, str]) -> None:
    """
    Create unified personality card layout with original simple styling.
    
    Args:
        canvas: PIL Image object
        draw: ImageDraw object
        source_image_path: Path to character image
        card_data: Card data dictionary
        colors: Color scheme dictionary
    """
    card_width, card_height = canvas.size
    margin = 20
    
    # Get category for fonts
    custom_type = card_data.get('custom_type', 'Vibe')
    type_to_category = {
        "Mood": "cute", "Vibe": "cute", "Simp": "cute",
        "NPC": "mystical", "Glitch": "mystical", "Ghost": "mystical",
        "Spicy": "chaotic", "Clapback": "chaotic",
        "Juice": "legendary", "Flex": "legendary", "Main": "legendary",
        "Lag": "cool", "Ping": "cool", "Firewall": "cool",
        "Debug": "wise", "Sus": "wise", "IYKYK": "wise",
        "Cringe": "mystical", "Cap": "heroic", "Send": "heroic"
    }
    category = type_to_category.get(custom_type, "cool")
    
    # Load category-specific fonts like original
    fonts = get_category_fonts(category)
    print(f"[DEBUG] Loading fonts for category: {category}")
    print(f"[DEBUG] Font paths: {fonts}")
    try:
        title_font = ImageFont.truetype(fonts["title"], 14)
        header_font = ImageFont.truetype(fonts["header"], 16)
        stat_font = ImageFont.truetype(fonts["stat"], 12)
        text_font = ImageFont.truetype(fonts["text"], 10)
        print("[DEBUG] Successfully loaded category-specific fonts")
    except (OSError, IOError) as e:
        print(f"[DEBUG] Category fonts failed: {e}")
        print("[DEBUG] Trying fallback fonts...")
        # Fallback to different fonts based on category if category fonts not available
        try:
            if category == "cute":
                title_font = ImageFont.truetype("comic.ttf", 14)
                header_font = ImageFont.truetype("comic.ttf", 16)
                stat_font = ImageFont.truetype("verdana.ttf", 12)
                text_font = ImageFont.truetype("calibri.ttf", 10)
            elif category == "cool":
                title_font = ImageFont.truetype("calibri.ttf", 14)
                header_font = ImageFont.truetype("arial.ttf", 16)
                stat_font = ImageFont.truetype("consola.ttf", 12)
                text_font = ImageFont.truetype("calibri.ttf", 10)
            elif category == "heroic":
                title_font = ImageFont.truetype("impact.ttf", 14)
                header_font = ImageFont.truetype("impact.ttf", 16)
                stat_font = ImageFont.truetype("arial.ttf", 12)
                text_font = ImageFont.truetype("tahoma.ttf", 10)
            elif category == "legendary":
                title_font = ImageFont.truetype("times.ttf", 14)
                header_font = ImageFont.truetype("georgia.ttf", 16)
                stat_font = ImageFont.truetype("georgia.ttf", 12)
                text_font = ImageFont.truetype("times.ttf", 10)
            elif category == "mystical":
                title_font = ImageFont.truetype("georgia.ttf", 14)
                header_font = ImageFont.truetype("times.ttf", 16)
                stat_font = ImageFont.truetype("georgia.ttf", 12)
                text_font = ImageFont.truetype("trebuc.ttf", 10)
            elif category == "chaotic":
                title_font = ImageFont.truetype("impact.ttf", 14)
                header_font = ImageFont.truetype("trebuc.ttf", 16)
                stat_font = ImageFont.truetype("consola.ttf", 12)
                text_font = ImageFont.truetype("calibri.ttf", 10)
            elif category == "fierce":
                title_font = ImageFont.truetype("impact.ttf", 14)
                header_font = ImageFont.truetype("arial.ttf", 16)
                stat_font = ImageFont.truetype("verdana.ttf", 12)
                text_font = ImageFont.truetype("tahoma.ttf", 10)
            elif category == "wise":
                title_font = ImageFont.truetype("times.ttf", 14)
                header_font = ImageFont.truetype("georgia.ttf", 16)
                stat_font = ImageFont.truetype("consolas.ttf", 12)
                text_font = ImageFont.truetype("georgia.ttf", 10)
            else:
                # Default fallback
                title_font = ImageFont.truetype("arial.ttf", 14)
                header_font = ImageFont.truetype("arial.ttf", 16)
                stat_font = ImageFont.truetype("arial.ttf", 12)
                text_font = ImageFont.truetype("arial.ttf", 10)
        except (OSError, IOError) as e:
            print(f"[DEBUG] Category fallback fonts failed: {e}")
            print("[DEBUG] Trying final fallback...")
            # Final fallback - try to use system fonts with proper sizes
            try:
                title_font = ImageFont.truetype("arial.ttf", 14)
                header_font = ImageFont.truetype("arial.ttf", 16)
                stat_font = ImageFont.truetype("arial.ttf", 12)
                text_font = ImageFont.truetype("arial.ttf", 10)
                print("[DEBUG] Successfully loaded final fallback fonts")
            except (OSError, IOError):
                # Absolute last resort - use larger cross-platform fallback
                print("WARNING: All font loading failed - using larger cross-platform fallback")
                try:
                    # Try DejaVuSans which is commonly available on Linux systems
                    title_font = ImageFont.truetype("DejaVuSans.ttf", 28)
                    header_font = ImageFont.truetype("DejaVuSans.ttf", 32)
                    stat_font = ImageFont.truetype("DejaVuSans.ttf", 24)
                    text_font = ImageFont.truetype("DejaVuSans.ttf", 20)
                    print("[DEBUG] Successfully loaded DejaVuSans fallback fonts")
                except (OSError, IOError):
                    # Last resort - use default font with larger sizes
                    print("[DEBUG] Using default font with larger sizes")
                    try:
                        # Try to load default font and scale it up
                        base_font = ImageFont.load_default()
                        # Create larger fonts by using a scaling factor
                        title_font = ImageFont.truetype("arial.ttf", 28) if os.path.exists("arial.ttf") else base_font
                        header_font = ImageFont.truetype("arial.ttf", 32) if os.path.exists("arial.ttf") else base_font
                        stat_font = ImageFont.truetype("arial.ttf", 24) if os.path.exists("arial.ttf") else base_font
                        text_font = ImageFont.truetype("arial.ttf", 20) if os.path.exists("arial.ttf") else base_font
                        print("[DEBUG] Using scaled default fonts")
                    except:
                        # Absolute last resort - use default font as-is
                        print("[DEBUG] Using default font as-is")
                        base_font = ImageFont.load_default()
                        title_font = base_font
                        header_font = base_font
                        stat_font = base_font
                        text_font = base_font
    
    # Log which font loading path succeeded
    print(f"[DEBUG] Font loading complete - Title: {title_font}, Header: {header_font}, Stat: {stat_font}, Text: {text_font}")
    
    # Simple ornate border with glow effect like original
    corner_radius = 15
    border_width = 6
    for i in range(3):
        glow_width = border_width - i * 2
        glow_color = colors['accent'] if i == 0 else colors['primary']
        draw.rounded_rectangle([i, i, card_width - i, card_height - i], 
                             radius=corner_radius - i, outline=glow_color, width=glow_width)
    
    # 1. Header section with gradient background like original
    header_y = 30
    header_height = 80
    
    # Header background with rounded corners
    header_bg = create_gradient_background(card_width - 40, header_height, colors['primary'], colors['secondary'])
    header_mask = create_rounded_rectangle_mask(card_width - 40, header_height, 10)
    header_bg.putalpha(header_mask)
    
    # Paste header background
    header_x = 20
    canvas.paste(header_bg, (header_x, header_y), header_bg)
    draw = ImageDraw.Draw(canvas)
    
    card_name = card_data.get('card_name', 'Unknown')
    # Character name with shadow
    add_text_shadow(draw, card_name, (margin + 15, header_y + 10), title_font, 
                   colors['text'], (0, 0, 0, 100))
    
    # 2. Type badge (in header like original)
    type_text = card_data.get('custom_type', 'Unknown')
    
    # Try to load a Unicode-capable font for type badge (larger size)
    try:
        icon_font = ImageFont.truetype("arial.ttf", 20)  # Arial supports more Unicode, increased size
    except (OSError, IOError):
        try:
            icon_font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except (OSError, IOError):
            icon_font = header_font  # Fallback to header font
    
    # Calculate width for type badge (text only, no icons)
    type_bbox = draw.textbbox((0, 0), type_text, font=icon_font)
    type_width = type_bbox[2] - type_bbox[0] + 20
    type_x = card_width - margin - type_width - 15
    type_y = header_y + 15
    
    # Type badge background
    draw.rounded_rectangle([type_x, type_y, type_x + type_width, type_y + 30], 
                         radius=8, fill=colors['accent'])
    
    # Draw type text only (no icons/emojis)
    try:
        draw.text((type_x + 10, type_y + 5), type_text, fill=colors['background'], font=icon_font)
    except Exception as e:
        print(f"[DEBUG] Failed to draw type: {e}")
        # Fallback: draw just the type text
        draw.text((type_x + 10, type_y + 5), type_text, fill=colors['background'], font=header_font)
    
    # 3. Image section with rounded frame like original
    image_y = header_y + header_height + 20
    image_width = card_width - (2 * margin) - 20
    image_height = 320
    
    # Image frame with inner shadow
    frame_x = margin + 10
    frame_y = image_y
    draw.rounded_rectangle([frame_x, frame_y, frame_x + image_width, frame_y + image_height], 
                         radius=12, outline=colors['accent'], width=4)
    
    # Inner frame
    inner_frame_x = frame_x + 8
    inner_frame_y = frame_y + 8
    inner_width = image_width - 16
    inner_height = image_height - 16
    draw.rounded_rectangle([inner_frame_x, inner_frame_y, inner_frame_x + inner_width, inner_frame_y + inner_height], 
                         radius=8, outline=colors['primary'], width=2)
    
    # Load and resize source image
    with Image.open(source_image_path) as source_img:
        if source_img.mode != 'RGB':
            source_img = source_img.convert('RGB')
        
        # Calculate aspect ratio and resize to fit
        aspect_ratio = source_img.height / source_img.width
        if aspect_ratio > inner_height / inner_width:
            new_height = inner_height
            new_width = int(inner_height / aspect_ratio)
        else:
            new_width = inner_width
            new_height = int(inner_width * aspect_ratio)
        
        resized_img = source_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center image with rounded corners
        x_offset = inner_frame_x + (inner_width - new_width) // 2
        y_offset = inner_frame_y + (inner_height - new_height) // 2
        
        # Create mask for image
        img_mask = create_rounded_rectangle_mask(new_width, new_height, 6)
        resized_img.putalpha(img_mask)
        
        # Paste image
        canvas.paste(resized_img, (x_offset, y_offset), resized_img)
    
    # 4. Stats section with enhanced styling like original
    stats_y = image_y + image_height + 25
    stats_height = 140
    
    # Stats background with gradient
    stats_bg = create_gradient_background(card_width - 40, stats_height, colors['primary'], colors['secondary'])
    stats_mask = create_rounded_rectangle_mask(card_width - 40, stats_height, 12)
    stats_bg.putalpha(stats_mask)
    canvas.paste(stats_bg, (20, stats_y), stats_bg)
    draw = ImageDraw.Draw(canvas)
    
    # Custom stats displayed in circles like original
    stat1_name = card_data.get('stat1_name', 'Power')
    stat1_value = card_data.get('stat1_value', 1000)
    stat2_name = card_data.get('stat2_name', 'Defense')
    stat2_value = card_data.get('stat2_value', 1000)
    
    stats = [
        (stat1_name, stat1_value),
        (stat2_name, stat2_value)
    ]
    
    stat_width = (card_width - 2 * margin - 20) // 2
    for i, (label, value) in enumerate(stats):
        x = margin + 10 + (i * stat_width)
        
        # Stat background circle - larger size
        circle_radius = 45
        circle_x = x + stat_width // 2
        # Center the circle vertically in the stats box
        # stats_height = 140, account for label height (~15px) above circle
        label_offset = 25
        circle_y = stats_y + (stats_height // 2) + (label_offset // 2)
        
        draw.ellipse([circle_x - circle_radius, circle_y - circle_radius, 
                     circle_x + circle_radius, circle_y + circle_radius], 
                   fill=colors['accent'])
        
        # Stat label - positioned above circle
        label_bbox = draw.textbbox((0, 0), label, font=stat_font)
        label_width = label_bbox[2] - label_bbox[0]
        label_y = circle_y - circle_radius - label_offset
        draw.text((circle_x - label_width // 2, label_y), label, fill=colors['text'], font=stat_font)
        
        # Stat value - centered in circle
        value_bbox = draw.textbbox((0, 0), str(value), font=stat_font)
        value_width = value_bbox[2] - value_bbox[0]
        value_height = value_bbox[3] - value_bbox[1]
        draw.text((circle_x - value_width // 2, circle_y - value_height // 2), str(value), 
                fill=colors['background'], font=stat_font)
    
    # 5. Ability section with enhanced styling like original
    ability_y = stats_y + stats_height + 25
    ability_height = 180
    
    # Ability background with gradient
    ability_bg = create_gradient_background(card_width - 40, ability_height, colors['secondary'], colors['primary'])
    ability_mask = create_rounded_rectangle_mask(card_width - 40, ability_height, 12)
    ability_bg.putalpha(ability_mask)
    canvas.paste(ability_bg, (20, ability_y), ability_bg)
    draw = ImageDraw.Draw(canvas)
    
    # Effect description with dynamic text wrapping to prevent overflow
    effect_desc = card_data.get('effect_description', 'No description available.')
    
    # Calculate available space for text
    text_area_width = card_width - 2 * margin - 40 - 20  # Account for padding
    text_area_height = ability_height - 30  # Account for top/bottom margins
    
    # Use textbbox to measure actual text dimensions and wrap dynamically
    max_width_px = text_area_width
    
    # Start with a reasonable character estimate and adjust
    words = effect_desc.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=text_font)
        line_width = bbox[2] - bbox[0]
        
        if line_width <= max_width_px:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word is too long, add it anyway
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    
    wrapped_desc = '\n'.join(lines)
    
    # Check if text height exceeds available space and truncate if needed
    bbox = draw.textbbox((0, 0), wrapped_desc, font=text_font)
    text_height = bbox[3] - bbox[1]
    
    if text_height > text_area_height:
        # Remove lines from bottom until it fits
        while lines and text_height > text_area_height:
            lines.pop()
            if lines:
                lines[-1] = lines[-1].rstrip() + '...'
            wrapped_desc = '\n'.join(lines)
            bbox = draw.textbbox((0, 0), wrapped_desc, font=text_font)
            text_height = bbox[3] - bbox[1]
    
    # Draw description without shadow
    draw.text((margin + 20, ability_y + 15), wrapped_desc, fill=colors['text'], font=text_font)


def create_card_image(source_image_path: str, card_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
    """
    Create a personality card with AI-generated name and custom type.
    
    Args:
        source_image_path (str): Path to the source image file
        card_data (dict): Generated card data with stats and abilities
        filename (str, optional): Specific filename to use for saving
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("Creating personality card with enhanced visuals...")
        
        # Card dimensions (trading card proportions: 59mm × 86mm scaled up)
        card_width = 600
        card_height = 840
        
        # Get color scheme based on custom type
        custom_type = card_data.get('custom_type', 'Vibe')
        print(f"Custom Type: {custom_type}")
        colors = get_custom_type_colors(custom_type)
        
        # Create gradient background like original
        background = create_gradient_background(card_width, card_height, colors['background'], colors['secondary'])
        
        # Get category for texture overlay
        type_to_category = {
            "Mood": "cute", "Vibe": "cute", "Simp": "cute",
            "NPC": "mystical", "Glitch": "mystical", "Ghost": "mystical",
            "Spicy": "chaotic", "Clapback": "chaotic",
            "Lag": "cool", "Ping": "cool", "Firewall": "cool"
        }
        category = type_to_category.get(custom_type, "cool")
        
        # Add texture overlay
        texture_overlay = create_texture_overlay(card_width, card_height, category)
        background = background.convert('RGBA')
        background = Image.alpha_composite(background, texture_overlay)
        background = background.convert('RGB')
        
        # Create main canvas
        canvas = Image.new('RGB', (card_width, card_height), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        # Apply background with rounded corners
        canvas.paste(background, (0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # Create unified card layout
        create_unified_card(canvas, draw, source_image_path, card_data, colors)
        
        # Ensure Generated_Cards directory exists
        os.makedirs("Generated_Cards", exist_ok=True)
        
        # Use provided filename or generate one
        if not filename:
            import time
            card_name = card_data.get('card_name', 'Unknown_Card')
            # Sanitize filename
            safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in card_name)
            safe_name = safe_name.replace(' ', '_')
            timestamp = int(time.time())
            filename = f"{safe_name}_{timestamp}.png"
        
        output_path = os.path.join("Generated_Cards", filename)
        canvas.save(output_path, 'PNG')
        print(f"[SUCCESS] Personality card saved as: {output_path}")
        return True
        
    except FileNotFoundError as e:
        print(f"[ERROR] Image file not found: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create card image: {e}")
        import traceback
        traceback.print_exc()
        return False
