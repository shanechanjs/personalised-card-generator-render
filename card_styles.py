#!/usr/bin/env python3
"""
Card Styles Configuration Module

This module contains all static configuration and style-related functions
for the character card generator, including color schemes, font mappings,
and pattern configurations.
"""

# Style configuration
STYLE_VERSION = "modern"  # "modern" or "classic"


def get_type_pattern(custom_type: str) -> str:
    """
    Get pattern type based on personality category.
    
    Args:
        custom_type (str): One of the 20 custom personality types
        
    Returns:
        str: Pattern type name
    """
    pattern_map = {
        # VIBE & ATMOSPHERE
        "Mood": "bokeh",
        "Vibe": "dots", 
        "Spicy": "stars",
        "Juice": "bokeh",
        
        # DIGITAL & LOGIC
        "NPC": "grid",
        "Glitch": "scanlines",
        "Lag": "diagonals",
        "Ping": "grid",
        "Debug": "scanlines",
        "Firewall": "diagonals",
        
        # EGO & STATUS
        "Main": "diamonds",
        "Flex": "sparks",
        "IYKYK": "diamonds",
        "Cringe": "sparks",
        
        # ACTION & CONFLICT
        "Clapback": "slashes",
        "Sus": "chevrons",
        "Cap": "arrows",
        "Send": "slashes",
        
        # MOVEMENT & AVOIDANCE
        "Ghost": "mist",
        "Simp": "fade"
    }
    
    return pattern_map.get(custom_type, "dots")


def get_custom_type_colors(custom_type: str) -> dict:
    """
    Get color scheme based on custom personality type, mapped to original categories.
    
    Args:
        custom_type (str): One of the 20 custom personality types
        
    Returns:
        dict: Color scheme dictionary with original simple structure
    """
    # Original color schemes
    base_color_schemes = {
        "cute": {
            "primary": "#FFB6C1",      # Light pink
            "secondary": "#FFC0CB",    # Pink
            "accent": "#FF69B4",       # Hot pink
            "text": "#8B008B",         # Dark magenta
            "background": "#FFF0F5"    # Lavender blush
        },
        "cool": {
            "primary": "#87CEEB",      # Sky blue
            "secondary": "#B0E0E6",    # Powder blue
            "accent": "#4169E1",       # Royal blue
            "text": "#191970",         # Midnight blue
            "background": "#F0F8FF"    # Alice blue
        },
        "heroic": {
            "primary": "#FFD700",      # Gold
            "secondary": "#FFA500",    # Orange
            "accent": "#FF8C00",       # Dark orange
            "text": "#8B4513",         # Saddle brown
            "background": "#FFFACD"    # Lemon chiffon
        },
        "legendary": {
            "primary": "#DDA0DD",      # Plum
            "secondary": "#DA70D6",    # Orchid
            "accent": "#9370DB",       # Medium purple
            "text": "#4B0082",         # Indigo
            "background": "#F8F8FF"    # Ghost white
        },
        "mystical": {
            "primary": "#9370DB",      # Medium purple
            "secondary": "#BA55D3",    # Medium orchid
            "accent": "#8A2BE2",       # Blue violet
            "text": "#4B0082",         # Indigo
            "background": "#F0E6FF"    # Lavender
        },
        "chaotic": {
            "primary": "#FF4500",      # Orange red
            "secondary": "#FF6347",    # Tomato
            "accent": "#DC143C",       # Crimson
            "text": "#8B0000",         # Dark red
            "background": "#FFF5EE"    # Seashell
        },
        "fierce": {
            "primary": "#B22222",      # Fire brick
            "secondary": "#DC143C",    # Crimson
            "accent": "#8B0000",       # Dark red
            "text": "#2F0000",         # Very dark red
            "background": "#FFE4E1"    # Misty rose
        },
        "wise": {
            "primary": "#4682B4",      # Steel blue
            "secondary": "#87CEEB",    # Sky blue
            "accent": "#191970",       # Midnight blue
            "text": "#2F4F4F",         # Dark slate gray
            "background": "#F0F8FF"    # Alice blue
        }
    }
    
    # Map 20 personality types to 8 base categories
    type_to_category = {
        # VIBE & ATMOSPHERE → cute
        "Mood": "cute",
        "Vibe": "cute",
        "Simp": "cute",
        
        # DIGITAL & LOGIC (mystical/cool/wise)
        "NPC": "mystical",
        "Glitch": "mystical",
        "Ghost": "mystical",
        "Lag": "cool",
        "Ping": "cool",
        "Firewall": "cool",
        "Debug": "wise",
        "Sus": "wise",
        "IYKYK": "wise",
        
        # EGO & STATUS → legendary/heroic
        "Main": "legendary",
        "Flex": "legendary",
        "Cringe": "mystical",
        
        # ACTION & CONFLICT → chaotic/fierce
        "Spicy": "chaotic",
        "Clapback": "chaotic",
        "Cap": "heroic",
        "Send": "heroic"
    }
    
    # Get category for this type
    category = type_to_category.get(custom_type, "cool")
    return base_color_schemes.get(category, base_color_schemes["cool"])


def get_category_fonts(category: str) -> dict:
    """
    Get font configuration based on category.
    
    Args:
        category (str): Character category
        
    Returns:
        dict: Font configuration with paths for different text elements
    """
    # Windows system font paths
    font_paths = {
        "arial": "C:/Windows/Fonts/arial.ttf",
        "arialbd": "C:/Windows/Fonts/arialbd.ttf",
        "comic": "C:/Windows/Fonts/comic.ttf",
        "comicbd": "C:/Windows/Fonts/comicbd.ttf",
        "impact": "C:/Windows/Fonts/impact.ttf",
        "times": "C:/Windows/Fonts/times.ttf",
        "timesbd": "C:/Windows/Fonts/timesbd.ttf",
        "verdana": "C:/Windows/Fonts/verdana.ttf",
        "verdanab": "C:/Windows/Fonts/verdanab.ttf",
        "trebuchet": "C:/Windows/Fonts/trebuc.ttf",
        "trebuchetbd": "C:/Windows/Fonts/trebucbd.ttf",
        "georgia": "C:/Windows/Fonts/georgia.ttf",
        "georgiab": "C:/Windows/Fonts/georgiab.ttf",
        "courier": "C:/Windows/Fonts/cour.ttf",
        "courierbd": "C:/Windows/Fonts/courbd.ttf",
        "calibri": "C:/Windows/Fonts/calibri.ttf",
        "calibrib": "C:/Windows/Fonts/calibrib.ttf",
        "consolas": "C:/Windows/Fonts/consola.ttf",
        "consolasb": "C:/Windows/Fonts/consolab.ttf",
        "tahoma": "C:/Windows/Fonts/tahoma.ttf",
        "tahomabd": "C:/Windows/Fonts/tahomabd.ttf"
    }
    
    # Category-specific font mappings with more variety
    font_mappings = {
        "cute": {
            "title": font_paths["comicbd"],
            "header": font_paths["comic"],
            "stat": font_paths["verdanab"],
            "text": font_paths["calibri"]
        },
        "cool": {
            "title": font_paths["calibrib"],
            "header": font_paths["arialbd"],
            "stat": font_paths["consolas"],
            "text": font_paths["calibri"]
        },
        "heroic": {
            "title": font_paths["impact"],
            "header": font_paths["impact"],
            "stat": font_paths["arialbd"],
            "text": font_paths["tahoma"]
        },
        "legendary": {
            "title": font_paths["timesbd"],
            "header": font_paths["georgiab"],
            "stat": font_paths["georgia"],
            "text": font_paths["times"]
        },
        "mystical": {
            "title": font_paths["georgiab"],
            "header": font_paths["timesbd"],
            "stat": font_paths["georgia"],
            "text": font_paths["trebuchet"]
        },
        "chaotic": {
            "title": font_paths["impact"],
            "header": font_paths["trebuchetbd"],
            "stat": font_paths["consolas"],
            "text": font_paths["calibri"]
        },
        "fierce": {
            "title": font_paths["impact"],
            "header": font_paths["arialbd"],
            "stat": font_paths["verdanab"],
            "text": font_paths["tahoma"]
        },
        "wise": {
            "title": font_paths["timesbd"],
            "header": font_paths["georgiab"],
            "stat": font_paths["consolas"],
            "text": font_paths["georgia"]
        }
    }
    
    return font_mappings.get(category.lower(), font_mappings["cool"])
