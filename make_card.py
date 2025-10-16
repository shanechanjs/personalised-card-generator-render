#!/usr/bin/env python3
"""
Character Card Generator

A command-line tool that creates character cards by combining AI-generated
text descriptions with source images using LLM APIs (Gemini primary, OpenAI fallback)
and Pillow image composition.
"""

import argparse
import os
import sys
from pathlib import Path

# Import from new modular structure
from llm_api import generate_card_data
from card_graphics import create_card_image

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


def generate_card_web(uploaded_file, traits, custom_descriptor=None, gemini_api_key=None, openai_api_key=None):
    """
    Generate a character card from web upload and traits using AI-generated names.
    
    Args:
        uploaded_file: Flask file object
        traits (list): List of 5 character traits
        custom_descriptor (str, optional): Custom descriptor for filename (deprecated)
        gemini_api_key (str, optional): Gemini API key for primary LLM service
        openai_api_key (str, optional): OpenAI API key for fallback LLM service
        
    Returns:
        dict: Result with success status, card data, and file path
    """
    try:
        print(f"[GENERATE_CARD_WEB] Starting card generation...")
        print(f"[GENERATE_CARD_WEB] File: {uploaded_file.filename if uploaded_file else 'None'}")
        print(f"[GENERATE_CARD_WEB] Traits count: {len(traits) if traits else 0}")
        print(f"[GENERATE_CARD_WEB] Gemini API key available: {'Yes' if gemini_api_key else 'No'}")
        print(f"[GENERATE_CARD_WEB] OpenAI API key available: {'Yes' if openai_api_key else 'No'}")
        
        # Use passed API keys or fall back to global ones
        effective_gemini_key = gemini_api_key or GEMINI_API_KEY
        effective_openai_key = openai_api_key or OPENAI_API_KEY
        
        # Check if at least one API key is available
        if not effective_gemini_key and not effective_openai_key:
            print("[GENERATE_CARD_WEB] ERROR: No API keys available")
            return {"success": False, "error": "No API keys configured. Please check your environment variables."}
        
        # Save uploaded image
        print("[GENERATE_CARD_WEB] Saving uploaded image...")
        original_filename = uploaded_file.filename
        image_path = save_uploaded_image(uploaded_file, original_filename)
        print(f"[GENERATE_CARD_WEB] Image saved to: {image_path}")
        
        # Generate card data with AI-generated name using both API keys
        print("[GENERATE_CARD_WEB] Generating card data with AI...")
        card_data = generate_card_data(traits, effective_gemini_key, effective_openai_key)
        if not card_data:
            print("[GENERATE_CARD_WEB] ERROR: Failed to generate card data")
            return {"success": False, "error": "Failed to generate card data. Check API keys and try again."}
        
        print(f"[GENERATE_CARD_WEB] Card data generated successfully: {card_data.get('card_name', 'Unknown')}")
        
        # Generate filename using AI-generated card name (before creating image)
        card_name = card_data.get('card_name', 'Unknown Card')
        import time
        safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in card_name)
        safe_name = safe_name.replace(' ', '_')
        timestamp = int(time.time())
        filename = f"{safe_name}_{timestamp}.png"
        
        # Create card image with the specific filename
        print("[GENERATE_CARD_WEB] Creating card image...")
        success = create_card_image(image_path, card_data, filename)
        
        if success:
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
    
    # Step 1: Generate character card data using AI with fallback
    card_data = generate_card_data(traits, GEMINI_API_KEY, OPENAI_API_KEY)
    
    if not card_data:
        print("[ERROR] Failed to generate character card data. Exiting.")
        sys.exit(1)
    
    print(f"\nGenerated Personality Card Data:")
    print(f"  Card Name: {card_data.get('card_name', 'Unknown')}")
    # Handle emoji display safely for console
    try:
        print(f"  Custom Type: {card_data.get('custom_type', 'Vibe')}")
        print(f"  Visual Effects: {', '.join(card_data.get('visual_effects', []))}")
    except UnicodeEncodeError:
        print(f"  Custom Type: {card_data.get('custom_type', 'Vibe')} [emoji]")
        print(f"  Visual Effects: [emoji]")
    print(f"  {card_data.get('stat1_name', 'Stat1')}: {card_data.get('stat1_value', 0)}")
    print(f"  {card_data.get('stat2_name', 'Stat2')}: {card_data.get('stat2_value', 0)}")
    print(f"  Effect: {card_data.get('effect_description', 'No effect.')}")
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