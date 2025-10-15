#!/usr/bin/env python3
"""
Character Card Generator

A command-line tool that creates character cards by combining AI-generated
text descriptions with source images using OpenAI Chat Completions API
and Pillow image composition.
"""

import argparse
import os
import sys
import textwrap
import json
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import openai

# Style configuration
STYLE_VERSION = "modern"  # "modern" or "classic"
# Text sanitation
def sanitize_ascii(text):
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-\n")
    return ''.join(ch for ch in (text or '') if ch in allowed)

# Utility: hard-cap text length with ellipsis
def shorten_to_chars(text, max_chars):
    text = text or ''
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max(0, max_chars - 3)].rstrip() + '...'
# Load API keys from environment variables (required for Render deployment)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# For local development, try to load from API_KEYS.py if environment variables are not set
if not OPENAI_API_KEY or not GEMINI_API_KEY:
    try:
        from API_KEYS import OPENAI_API_KEY as LOCAL_OPENAI_KEY, GEMINI_API_KEY as LOCAL_GEMINI_KEY
        if not OPENAI_API_KEY:
            OPENAI_API_KEY = LOCAL_OPENAI_KEY
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = LOCAL_GEMINI_KEY
        print("API keys loaded from API_KEYS.py for local development")
    except ImportError:
        print("API_KEYS.py not found, using environment variables only")

# Verify API keys are available
if not OPENAI_API_KEY or not GEMINI_API_KEY:
    print("ERROR: API keys not found!")
    print("Please set OPENAI_API_KEY and GEMINI_API_KEY environment variables.")
    print("For Render deployment, add these as environment variables in your Render service settings.")
    if not OPENAI_API_KEY:
        print("Missing: OPENAI_API_KEY")
    if not GEMINI_API_KEY:
        print("Missing: GEMINI_API_KEY")
    # Don't exit in web application context - let the web app handle the error
    print("WARNING: API keys not configured - card generation will fail")


def generate_card_data(traits, api_key):
    """
    Generate structured card data using OpenAI Chat Completions API.
    
    Args:
        traits (list): List of five character traits
        api_key (str): OpenAI API key
        
    Returns:
        dict: Generated card data if successful, None if failed
    """
    try:
        print("Generating character card data with OpenAI GPT-4o...")
        print(f"API key provided: {'Yes' if api_key else 'No'}")
        print(f"API key length: {len(api_key) if api_key else 0}")
        print(f"Traits count: {len(traits) if traits else 0}")
        
        # Check if API key is valid
        if not api_key:
            print("[ERROR] No API key provided")
            return None
            
        if not api_key.startswith('sk-'):
            print("[ERROR] Invalid API key format - should start with 'sk-'")
            return None
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Combine traits into a single user message
        user_prompt = "Here are five things about this character:\n\n"
        for i, trait in enumerate(traits, 1):
            user_prompt += f"{i}. {trait}\n"
        
        # Make API call
        print("Making OpenAI API call...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a creative personality card designer who creates hilarious, entertaining character cards. Based on the 5 things about this character, generate a JSON response with the following structure:

{
    "card_name": "Creative and funny name based on personality traits in the things about this character",
    "custom_type": "One of the 20 personality types below that BEST matches the character",
    "custom_type_icon": "A single emoji that represents this personality type",
    "trait_icon": "A single emoji that represents the most prominent trait from the 5 things about this character",
    "stat1_name": "Creative stat name (e.g., 'Chaos', 'Rizz', 'Drama', 'Stealth', 'Cringe Level', 'Vibe Strength')",
    "stat1_value": number (100-3000, increments of 100),
    "stat2_name": "Different creative stat name that complements stat1",
    "stat2_value": number (100-3000, increments of 100),
    "effect_description": "Write like a Yu-Gi-Oh card effect description with meme-like twist. 3-5 sentences. Must include a clear nod to EACH of the 5 things (at least one distinct idea per thing). Use Yu-Gi-Oh formatting style (e.g., 'When this card is activated...', 'This card cannot be...', etc.) with internet meme humor. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).",
    "visual_effects": ["effect1", "effect2"] // Suggest 2-3 visual effects like "sparkles", "flames", "lightning", "glitch", "shadows", "stars", "spiral", "smoke", "neon", "bubbles"
}

20 PERSONALITY TYPES (choose the ONE that best matches):

VIBE & ATMOSPHERE:
- "Mood": Not a person who has a mood, but one who is the collective atmosphere of the room
- "Vibe": Bypasses specific descriptors; they are simply their distinct, inexplicable vibe
- "Spicy": Delivers every opinion with a sharp, slightly aggressive kick
- "Juice": The source of energy, motivation, or charisma for a group

DIGITAL & LOGIC:
- "NPC": Follows preset social scripts; seems to lack independent thought
- "Glitch": Has brief, random, illogical moments of social instability
- "Lag": Perpetually half a beat behind the joke or conversation
- "Ping": Sends rapid, sporadic, low-effort conversational checks/messages
- "Debug": Hyper-analytical, always looking for the source of a problem in other people's lives/plans
- "Firewall": Has an impenetrable emotional defense system; nothing personal gets through

EGO & STATUS:
- "Main": The one whose life everyone else's seems to revolve around
- "Flex": Their every action is designed to show off status or skill
- "IYKYK": Personality built on obscure references and shared, exclusionary knowledge
- "Cringe": Their social output causes persistent, painful secondhand embarrassment

ACTION & CONFLICT:
- "Clapback": Primary function is to immediately and aggressively return fire in any verbal exchange
- "Sus": Constantly acting in a way that is vaguely inconsistent or questionable
- "Cap": A personality fundamentally prone to dishonesty and obvious exaggeration
- "Send": Extreme willingness to try anything reckless or weird for the sheer chaos of it

MOVEMENT & AVOIDANCE:
- "Ghost": Defining trait is sudden, complete, unannounced disappearance from commitments
- "Simp": Chronically and pathetically eager to please a specific person or group

IMPORTANT RULES:
1. CARD NAME: If a person's name is mentioned, incorporate it. Otherwise, create a funny/creative name from personality traits. NEVER use generic names or filenames.
2. Choose the MOST FITTING personality type from the 20 options above based on the dominant trait in the things about this character.
3. Select an emoji for custom_type_icon that visually represents that personality type.
4. Select a different emoji for trait_icon that represents the most prominent trait from the 5 things about this character.
5. Create 2 UNIQUE and CREATIVE stat names that match the personality (not generic ATK/DEF).
6. Stat values should increment by 100s and somewhat reflect personality strength (100-3000 range).
7. Effect description: Write like a Yu-Gi-Oh card effect with meme-like twist, 3-5 COMPLETE sentences (no cut-off mid-sentence), MUST reference a core idea from EACH of the 5 things. Use Yu-Gi-Oh formatting style with internet humor. Keep under 380 characters to ensure all sentences are complete. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).
8. Suggest 2-3 visual effects that would enhance the card's personality aesthetically.

Examples:
- Things about being the life of the party → Type: "Juice", Icon: "⚡", Stats: "Charisma"/2400, "Energy"/2100
- Things about always ghosting plans → Type: "Ghost", Icon: "👻", Stats: "Vanish Speed"/2800, "Commitment"/200
- Things about excessive flexing → Type: "Flex", Icon: "💪", Stats: "Clout"/2700, "Humility"/100"""
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_tokens=750,
                temperature=0.9
            )
            print("OpenAI API call successful")
        except Exception as api_error:
            print(f"[ERROR] OpenAI API call failed: {str(api_error)}")
            print(f"[ERROR] API error type: {type(api_error).__name__}")
            return None
        
        # Extract and parse the generated JSON
        response_text = response.choices[0].message.content
        if response_text:
            print(f"[DEBUG] Raw response from OpenAI: {response_text[:200]}...")
            response_text = response_text.strip()
        else:
            print("[ERROR] Empty response from OpenAI API")
            return None
        
        # Try to extract JSON from the response (in case it has extra text)
        try:
            # Look for JSON between curly braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            print(f"[DEBUG] JSON extraction - start: {start_idx}, end: {end_idx}")
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                print(f"[DEBUG] Extracted JSON string: {json_str[:200]}...")
                card_data = json.loads(json_str)
            else:
                print(f"[DEBUG] No curly braces found, trying to parse entire response")
                card_data = json.loads(response_text)
            
            print(f"[DEBUG] Successfully parsed JSON: {list(card_data.keys())}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON response: {e}")
            print(f"[ERROR] Response text: {response_text}")
            return None
        
        # Heuristic coverage check for 5-fact inclusion in effect_description
        def _extract_keywords_from_fact(fact_text):
            text = fact_text.lower()
            # Keep alphanumerics and spaces
            cleaned = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in text)
            tokens = [t for t in cleaned.split() if len(t) > 3]
            # Prefer the two longest tokens to represent the core idea
            tokens.sort(key=len, reverse=True)
            return tokens[:2] if tokens else (cleaned.split()[:1] if cleaned.split() else [])

        def _find_uncovered_traits(desc_text, input_traits):
            desc_lc = desc_text.lower()
            missing_indices = []
            for idx, trait in enumerate(input_traits):
                keywords = _extract_keywords_from_fact(trait)
                if not keywords:
                    continue
                if not any(k in desc_lc for k in keywords):
                    missing_indices.append(idx)
            return missing_indices

        # Perform coverage check and single-pass rewrite if needed
        try:
            effect_desc = card_data.get('effect_description', '') or ''
            missing = _find_uncovered_traits(effect_desc, traits)
            if missing:
                # Targeted rewrite to include all 5 traits
                rewrite_user = "Rewrite ONLY the effect_description below into 3-5 COMPLETE sentences in Yu-Gi-Oh card effect style with meme-like twist. It must nod to EACH of the 5 things with at least one distinct idea per thing. Use Yu-Gi-Oh formatting (e.g., 'When this card is activated...', 'This card cannot be...') with internet humor. Max 380 characters total. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).\n\nThings about character:\n" + "\n".join(f"- {i+1}. {t}" for i, t in enumerate(traits)) + "\n\nCurrent effect_description:\n" + effect_desc + "\n\nReturn only the rewritten effect_description text."
                rewrite_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You refine humorous card descriptions to match Yu-Gi-Oh card formatting with meme-like twists while preserving factual coverage."},
                        {"role": "user", "content": rewrite_user},
                    ],
                    max_tokens=300,
                    temperature=0.9,
                )
                msg_content = rewrite_resp.choices[0].message.content or ""
                new_text = msg_content.strip()
                if new_text:
                    card_data['effect_description'] = shorten_to_chars(sanitize_ascii(new_text), 380)
        except Exception as _:
            # If rewrite fails, proceed with original effect description
            card_data['effect_description'] = shorten_to_chars(sanitize_ascii(effect_desc), 380)

        # Always sanitize the primary generation too
        card_data['effect_description'] = shorten_to_chars(sanitize_ascii(card_data.get('effect_description', '')), 380)
        print(f"[SUCCESS] Generated card data for personality type: {card_data.get('custom_type', 'unknown')}")
        return card_data
        
    except Exception as e:
        print(f"[ERROR] Failed to generate card data: {e}")
        return None


# Removed extract_character_name function - now using AI-generated names only


def get_type_pattern(custom_type):
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


def get_custom_type_colors(custom_type):
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


def get_category_fonts(category):
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


def generate_card_descriptor(card_data, custom_descriptor=None):
    """
    Generate a 1-2 word descriptor for the card filename.
    
    Args:
        card_data (dict): Generated card data with category and type
        custom_descriptor (str, optional): Custom descriptor provided by user
        
    Returns:
        str: Card descriptor for filename
    """
    if custom_descriptor:
        return custom_descriptor.replace(' ', '_')
    
    category = card_data.get('category', 'Unknown').title()
    card_type = card_data.get('type', 'Unknown')
    
    # Create 1-2 word descriptor
    if len(card_type.split()) <= 2:
        return f"{category}_{card_type}"
    else:
        # Take first word of type if it's too long
        first_word = card_type.split()[0]
        return f"{category}_{first_word}"


def save_uploaded_image(uploaded_file, original_filename):
    """
    Save uploaded image to Original_Photos folder.
    
    Args:
        uploaded_file: Flask file object
        original_filename (str): Original filename
        
    Returns:
        str: Path to saved image file
    """
    # Ensure Original_Photos directory exists
    os.makedirs("Original_Photos", exist_ok=True)
    
    # Create safe filename
    safe_filename = original_filename.replace(' ', '_').replace('-', '_')
    file_path = os.path.join("Original_Photos", safe_filename)
    
    # Check if filename was changed (has spaces or hyphens)
    original_path = os.path.join("Original_Photos", original_filename)
    filename_was_changed = safe_filename != original_filename
    
    # Save the file
    uploaded_file.save(file_path)
    
    # If filename was changed and original file exists, delete it to avoid duplicates
    if filename_was_changed and os.path.exists(original_path) and original_path != file_path:
        try:
            os.remove(original_path)
            print(f"Deleted original file: {original_path}")
        except Exception as e:
            print(f"Warning: Could not delete original file {original_path}: {e}")
    
    return file_path


def generate_card_web(uploaded_file, traits, custom_descriptor=None):
    """
    Generate a character card from web upload and traits using AI-generated names.
    
    Args:
        uploaded_file: Flask file object
        traits (list): List of 5 character traits
        custom_descriptor (str, optional): Custom descriptor for filename (deprecated)
        
    Returns:
        dict: Result with success status, card data, and file path
    """
    try:
        print(f"[GENERATE_CARD_WEB] Starting card generation...")
        print(f"[GENERATE_CARD_WEB] File: {uploaded_file.filename if uploaded_file else 'None'}")
        print(f"[GENERATE_CARD_WEB] Traits count: {len(traits) if traits else 0}")
        print(f"[GENERATE_CARD_WEB] API key available: {'Yes' if OPENAI_API_KEY else 'No'}")
        
        # Check if API key is available
        if not OPENAI_API_KEY:
            print("[GENERATE_CARD_WEB] ERROR: No OpenAI API key available")
            return {"success": False, "error": "OpenAI API key not configured. Please check your environment variables."}
        
        # Save uploaded image
        print("[GENERATE_CARD_WEB] Saving uploaded image...")
        original_filename = uploaded_file.filename
        image_path = save_uploaded_image(uploaded_file, original_filename)
        print(f"[GENERATE_CARD_WEB] Image saved to: {image_path}")
        
        # Generate card data with AI-generated name
        print("[GENERATE_CARD_WEB] Generating card data with AI...")
        card_data = generate_card_data(traits, OPENAI_API_KEY)
        if not card_data:
            print("[GENERATE_CARD_WEB] ERROR: Failed to generate card data")
            return {"success": False, "error": "Failed to generate card data. Check API key and try again."}
        
        print(f"[GENERATE_CARD_WEB] Card data generated successfully: {card_data.get('card_name', 'Unknown')}")
        
        # Create card image (descriptor parameter is now ignored)
        print("[GENERATE_CARD_WEB] Creating card image...")
        success = create_card_image(image_path, card_data)
        
        if success:
            card_name = card_data.get('card_name', 'Unknown Card')
            # Generate filename using AI-generated card name
            import time
            safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in card_name)
            safe_name = safe_name.replace(' ', '_')
            timestamp = int(time.time())
            filename = f"{safe_name}_{timestamp}.png"
            
            print(f"[GENERATE_CARD_WEB] Card generation successful: {filename}")
            return {
                "success": True,
                "card_data": card_data,
                "filename": filename,
                "character_name": card_name,
                "descriptor": card_data.get('custom_type', 'Vibe')
            }
        else:
            print("[GENERATE_CARD_WEB] ERROR: Failed to create card image")
            return {"success": False, "error": "Failed to create card image"}
            
    except Exception as e:
        print(f"[GENERATE_CARD_WEB] EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def create_gradient_background(width, height, color1, color2, direction='vertical'):
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
    def hex_to_rgb(hex_color):
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


def create_rounded_rectangle_mask(width, height, radius):
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


def add_text_shadow(draw, text, position, font, fill_color, shadow_color, shadow_offset=(2, 2)):
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


def create_texture_overlay(width, height, category):
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




def apply_rounded_corners(image, radius):
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


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
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




def create_unified_card(canvas, draw, source_image_path, card_data, colors):
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
    try:
        title_font = ImageFont.truetype(fonts["title"], 36)
        header_font = ImageFont.truetype(fonts["header"], 24)
        stat_font = ImageFont.truetype(fonts["stat"], 22)
        text_font = ImageFont.truetype(fonts["text"], 20)
    except (OSError, IOError):
        # Fallback to different fonts based on category if category fonts not available
        try:
            if category == "cute":
                title_font = ImageFont.truetype("comic.ttf", 36)
                header_font = ImageFont.truetype("comic.ttf", 24)
                stat_font = ImageFont.truetype("verdana.ttf", 22)
                text_font = ImageFont.truetype("calibri.ttf", 20)
            elif category == "cool":
                title_font = ImageFont.truetype("calibri.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                stat_font = ImageFont.truetype("consola.ttf", 22)
                text_font = ImageFont.truetype("calibri.ttf", 20)
            elif category == "heroic":
                title_font = ImageFont.truetype("impact.ttf", 36)
                header_font = ImageFont.truetype("impact.ttf", 24)
                stat_font = ImageFont.truetype("arial.ttf", 22)
                text_font = ImageFont.truetype("tahoma.ttf", 20)
            elif category == "legendary":
                title_font = ImageFont.truetype("times.ttf", 36)
                header_font = ImageFont.truetype("georgia.ttf", 24)
                stat_font = ImageFont.truetype("georgia.ttf", 22)
                text_font = ImageFont.truetype("times.ttf", 20)
            elif category == "mystical":
                title_font = ImageFont.truetype("georgia.ttf", 36)
                header_font = ImageFont.truetype("times.ttf", 24)
                stat_font = ImageFont.truetype("georgia.ttf", 22)
                text_font = ImageFont.truetype("trebuc.ttf", 20)
            elif category == "chaotic":
                title_font = ImageFont.truetype("impact.ttf", 36)
                header_font = ImageFont.truetype("trebuc.ttf", 24)
                stat_font = ImageFont.truetype("consola.ttf", 22)
                text_font = ImageFont.truetype("calibri.ttf", 20)
            elif category == "fierce":
                title_font = ImageFont.truetype("impact.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                stat_font = ImageFont.truetype("verdana.ttf", 22)
                text_font = ImageFont.truetype("tahoma.ttf", 20)
            elif category == "wise":
                title_font = ImageFont.truetype("times.ttf", 36)
                header_font = ImageFont.truetype("georgia.ttf", 24)
                stat_font = ImageFont.truetype("consola.ttf", 22)
                text_font = ImageFont.truetype("georgia.ttf", 20)
            else:
                # Default fallback
                title_font = ImageFont.truetype("arial.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                stat_font = ImageFont.truetype("arial.ttf", 22)
                text_font = ImageFont.truetype("arial.ttf", 20)
        except (OSError, IOError):
            # Final fallback to default fonts with larger sizes
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
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
    
    # 2. Type badge with icons (in header like original)
    type_text = card_data.get('custom_type', 'Unknown')
    type_icon = card_data.get('custom_type_icon', '✨')
    trait_icon = card_data.get('trait_icon', '⭐')
    
    # Calculate width for type badge with icon
    type_with_icon = f"{type_icon} {type_text}"
    type_bbox = draw.textbbox((0, 0), type_with_icon, font=header_font)
    type_width = type_bbox[2] - type_bbox[0] + 20
    type_x = card_width - margin - type_width - 15
    type_y = header_y + 15
    
    # Type badge background
    draw.rounded_rectangle([type_x, type_y, type_x + type_width, type_y + 30], 
                         radius=8, fill=colors['accent'])
    draw.text((type_x + 10, type_y + 5), type_with_icon, fill=colors['background'], font=header_font)
    
    # Add trait icon next to the type badge
    trait_icon_x = type_x + type_width + 10
    trait_icon_y = type_y + 5
    draw.text((trait_icon_x, trait_icon_y), trait_icon, fill=colors['text'], font=header_font)
    
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
        y = stats_y + 20
        
        # Stat background circle
        circle_radius = 35
        circle_x = x + stat_width // 2
        circle_y = y + 30
        draw.ellipse([circle_x - circle_radius, circle_y - circle_radius, 
                     circle_x + circle_radius, circle_y + circle_radius], 
                   fill=colors['accent'])
        
        # Stat label
        label_bbox = draw.textbbox((0, 0), label, font=stat_font)
        label_width = label_bbox[2] - label_bbox[0]
        draw.text((circle_x - label_width // 2, y), label, fill=colors['text'], font=stat_font)
        
        # Stat value
        value_bbox = draw.textbbox((0, 0), str(value), font=stat_font)
        value_width = value_bbox[2] - value_bbox[0]
        draw.text((circle_x - value_width // 2, circle_y + 10), str(value), 
                fill=colors['background'], font=stat_font)
    
    # 5. Ability section with enhanced styling like original
    ability_y = stats_y + stats_height + 25
    ability_height = 140
    
    # Ability background with gradient
    ability_bg = create_gradient_background(card_width - 40, ability_height, colors['secondary'], colors['primary'])
    ability_mask = create_rounded_rectangle_mask(card_width - 40, ability_height, 12)
    ability_bg.putalpha(ability_mask)
    canvas.paste(ability_bg, (20, ability_y), ability_bg)
    draw = ImageDraw.Draw(canvas)
    
    # Effect description
    effect_desc = card_data.get('effect_description', 'No description available.')
    # Wrap text - use full available width (doubled the length before wrapping)
    max_chars = (card_width - 2 * margin - 40) // 5  # Double the text length before wrapping
    wrapped_desc = textwrap.fill(effect_desc, width=max_chars)
    # Draw description without shadow
    draw.text((margin + 20, ability_y + 15), wrapped_desc, fill=colors['text'], font=text_font)


def create_card_image(source_image_path, card_data):
    """
    Create a personality card with AI-generated name and custom type.
    
    Args:
        source_image_path (str): Path to the source image file
        card_data (dict): Generated card data with stats and abilities
        
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
        
        # Generate filename using AI-generated card name
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
        return False


def main():
    """Main function to handle command-line arguments and execute card creation."""
    parser = argparse.ArgumentParser(
        description="Create a character card by combining AI-generated text with a source image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python make_card.py ./johnny_bravo.jpg "They have a ridiculously specific collection of vintage hotel soap bars" "Their phone's autocorrect changes 'the' to 'the magnificent banana-lizard'" "They can flawlessly imitate the sound of an old-school fax machine" "Their signature food order is plain buttered toast and milk" "They have a secret online identity as 'The Doom-Waffle'"
        """
    )
    
    # Add command-line arguments
    parser.add_argument(
        "image_path",
        help="Path to the source image file"
    )
    
    parser.add_argument(
        "prompt1",
        help="First character fact"
    )
    
    parser.add_argument(
        "prompt2", 
        help="Second character fact"
    )
    
    parser.add_argument(
        "prompt3",
        help="Third character fact"
    )
    
    parser.add_argument(
        "prompt4",
        help="Fourth character fact"
    )
    
    parser.add_argument(
        "prompt5",
        help="Fifth character fact"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate image file exists
    if not os.path.exists(args.image_path):
        print(f"[ERROR] Image file not found: {args.image_path}")
        sys.exit(1)
    
    # Prepare traits list
    traits = [args.prompt1, args.prompt2, args.prompt3, args.prompt4, args.prompt5]
    
    # Display input information
    print("Character Card Generator")
    print("=" * 40)
    print(f"Source Image: {args.image_path}")
    print("Character Traits:")
    for i, trait in enumerate(traits, 1):
        print(f"  {i}. {trait}")
    print("=" * 40)
    
    # Step 1: Generate character card data using AI
    card_data = generate_card_data(traits, OPENAI_API_KEY)
    
    if not card_data:
        print("[ERROR] Failed to generate character card data. Exiting.")
        sys.exit(1)
    
    print(f"\nGenerated Personality Card Data:")
    print(f"  Card Name: {card_data.get('card_name', 'Unknown')}")
    # Handle emoji display safely for console
    try:
        print(f"  Custom Type: {card_data.get('custom_type', 'Vibe')} {card_data.get('custom_type_icon', '✨')}")
        print(f"  Trait Icon: {card_data.get('trait_icon', '⭐')}")
    except UnicodeEncodeError:
        print(f"  Custom Type: {card_data.get('custom_type', 'Vibe')} [emoji]")
        print(f"  Trait Icon: [emoji]")
    print(f"  {card_data.get('stat1_name', 'Stat1')}: {card_data.get('stat1_value', 0)}")
    print(f"  {card_data.get('stat2_name', 'Stat2')}: {card_data.get('stat2_value', 0)}")
    print(f"  Effect: {card_data.get('effect_description', 'No effect.')}")
    visual_effects_str = ', '.join(card_data.get('visual_effects', []))
    print(f"  Visual Effects: {visual_effects_str}")
    print("=" * 40)
    
    # Step 2: Create the character card
    success = create_card_image(args.image_path, card_data)
    
    if success:
        print("\n[SUCCESS] Character card creation completed successfully!")
        sys.exit(0)
    else:
        print("\n[ERROR] Character card creation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
