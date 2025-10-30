#!/usr/bin/env python3
"""
LLM API Integration Module

This module handles all interactions with Large Language Model APIs,
implementing a primary/fallback system with Google Gemini as primary
and OpenAI as fallback service.
"""

import os
import json
import google.generativeai as genai
from openai import OpenAI
from typing import List, Dict, Optional, Any


def sanitize_ascii(text: str) -> str:
    """
    Sanitize text to contain only basic ASCII characters.
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text with only allowed characters
    """
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-\n")
    return ''.join(ch for ch in (text or '') if ch in allowed)


def shorten_to_chars(text: str, max_chars: int) -> str:
    """
    Truncate text to maximum character count with ellipsis.
    
    Args:
        text (str): Input text to truncate
        max_chars (int): Maximum number of characters
        
    Returns:
        str: Truncated text with ellipsis if needed
    """
    text = text or ''
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max(0, max_chars - 3)].rstrip() + '...'


def _configure_gemini(api_key: str) -> Optional[Any]:
    """
    Configure Google Gemini API client.
    
    Args:
        api_key (str): Gemini API key
        
    Returns:
        Optional[Any]: Configured Gemini model or None if failed
    """
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Warning: Could not configure Gemini API: {e}")
        return None


def _configure_openai(api_key: str) -> Optional[OpenAI]:
    """
    Configure OpenAI API client.
    
    Args:
        api_key (str): OpenAI API key
        
    Returns:
        Optional[OpenAI]: Configured OpenAI client or None if failed
    """
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not configure OpenAI API: {e}")
        return None


def _call_gemini_api(traits: List[str], model: Any) -> Optional[Dict[str, Any]]:
    """
    Call Gemini API to generate card data.
    
    Args:
        traits (List[str]): List of character traits
        model: Configured Gemini model
        
    Returns:
        Optional[Dict[str, Any]]: Generated card data or None if failed
    """
    try:
        print("Making Gemini API call...")
        
        # Combine traits into a single user message
        user_prompt = "Here are five things about this character:\n\n"
        for i, trait in enumerate(traits, 1):
            user_prompt += f"{i}. {trait}\n"
        
        # Create the full prompt for Gemini
        full_prompt = f"""You are a creative personality card designer who creates hilarious, entertaining character cards. Based on the 5 things about this character, generate a JSON response with the following structure:

{{
    "card_name": "Creative and funny name based on personality traits in the things about this character (max 25 characters including spaces)",
    "custom_type": "One of the 20 personality types below that BEST matches the character",
    "stat1_name": "Creative stat name (e.g., 'Chaos', 'Rizz', 'Drama', 'Stealth', 'Cringe Level', 'Vibe Strength')",
    "stat1_value": number (100-3000, increments of 100),
    "stat2_name": "Different creative stat name that complements stat1",
    "stat2_value": number (100-3000, increments of 100),
    "effect_description": "Write like a Yu-Gi-Oh card effect description with meme-like twist. 3-4 sentences maximum. Must include a clear nod to EACH of the 5 things (at least one distinct idea per thing). Use Yu-Gi-Oh formatting style (e.g., 'When this card is activated...', 'This card cannot be...', etc.) with internet meme humor. MAXIMUM 280 CHARACTERS TOTAL including spaces and punctuation. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).",
    "visual_effects": ["effect1", "effect2"] // Suggest 2-3 visual effects like "sparkles", "flames", "lightning", "glitch", "shadows", "stars", "spiral", "smoke", "neon", "bubbles"
}}

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
1. CARD NAME: Must be max 25 characters including spaces. If a person's name is mentioned, incorporate it. Otherwise, create a funny/creative name from personality traits. NEVER use generic names or filenames.
2. Choose the MOST FITTING personality type from the 20 options above based on the dominant trait in the things about this character.
3. Create 2 UNIQUE and CREATIVE stat names that match the personality (not generic ATK/DEF).
4. Stat values should increment by 100s and somewhat reflect personality strength (100-3000 range).
5. Effect description: Write like a Yu-Gi-Oh card effect with meme-like twist, 3-4 COMPLETE sentences MAXIMUM (no cut-off mid-sentence), MUST reference a core idea from EACH of the 5 things. Use Yu-Gi-Oh formatting style with internet humor. CRITICAL: MAXIMUM 280 CHARACTERS TOTAL including spaces and punctuation - this is a hard limit to ensure text fits in the card. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).
6. Suggest 2-3 visual effects that would enhance the card's personality aesthetically.

Examples:
- Things about being the life of the party → Type: "Juice", Stats: "Charisma"/2400, "Energy"/2100
- Things about always ghosting plans → Type: "Ghost", Stats: "Vanish Speed"/2800, "Commitment"/200
- Things about excessive flexing → Type: "Flex", Stats: "Clout"/2700, "Humility"/100

{user_prompt}"""

        # Make API call
        response = model.generate_content(full_prompt)
        
        if not response.text:
            print("[ERROR] Empty response from Gemini API")
            return None
        
        # Parse JSON response
        response_text = response.text.strip()
        print(f"[DEBUG] Raw response from Gemini: {response_text[:200]}...")
        
        # Try to extract JSON from the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                print(f"[DEBUG] Extracted JSON string: {json_str[:200]}...")
                card_data = json.loads(json_str)
            else:
                print(f"[DEBUG] No curly braces found, trying to parse entire response")
                card_data = json.loads(response_text)
            
            print(f"[DEBUG] Successfully parsed JSON: {list(card_data.keys())}")
            
            # Sanitize and validate the response
            card_data = _validate_and_sanitize_card_data(card_data, traits)
            print(f"[SUCCESS] Generated card data with Gemini for personality type: {card_data.get('custom_type', 'unknown')}")
            return card_data
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON response from Gemini: {e}")
            print(f"[ERROR] Response text: {response_text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {str(e)}")
        print(f"[ERROR] API error type: {type(e).__name__}")
        return None


def _call_openai_api(traits: List[str], client: OpenAI) -> Optional[Dict[str, Any]]:
    """
    Call OpenAI API to generate card data.
    
    Args:
        traits (List[str]): List of character traits
        client: Configured OpenAI client
        
    Returns:
        Optional[Dict[str, Any]]: Generated card data or None if failed
    """
    try:
        print("Making OpenAI API call...")
        
        # Combine traits into a single user message
        user_prompt = "Here are five things about this character:\n\n"
        for i, trait in enumerate(traits, 1):
            user_prompt += f"{i}. {trait}\n"
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a creative personality card designer who creates hilarious, entertaining character cards. Based on the 5 things about this character, generate a JSON response with the following structure:

{
    "card_name": "Creative and funny name based on personality traits in the things about this character (max 25 characters including spaces)",
    "custom_type": "One of the 20 personality types below that BEST matches the character",
    "stat1_name": "Creative stat name (e.g., 'Chaos', 'Rizz', 'Drama', 'Stealth', 'Cringe Level', 'Vibe Strength')",
    "stat1_value": number (100-3000, increments of 100),
    "stat2_name": "Different creative stat name that complements stat1",
    "stat2_value": number (100-3000, increments of 100),
    "effect_description": "Write like a Yu-Gi-Oh card effect description with meme-like twist. 3-4 sentences maximum. Must include a clear nod to EACH of the 5 things (at least one distinct idea per thing). Use Yu-Gi-Oh formatting style (e.g., 'When this card is activated...', 'This card cannot be...', etc.) with internet meme humor. MAXIMUM 280 CHARACTERS TOTAL including spaces and punctuation. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).",
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
1. CARD NAME: Must be max 25 characters including spaces. If a person's name is mentioned, incorporate it. Otherwise, create a funny/creative name from personality traits. NEVER use generic names or filenames.
2. Choose the MOST FITTING personality type from the 20 options above based on the dominant trait in the things about this character.
3. Create 2 UNIQUE and CREATIVE stat names that match the personality (not generic ATK/DEF).
4. Stat values should increment by 100s and somewhat reflect personality strength (100-3000 range).
5. Effect description: Write like a Yu-Gi-Oh card effect with meme-like twist, 3-4 COMPLETE sentences MAXIMUM (no cut-off mid-sentence), MUST reference a core idea from EACH of the 5 things. Use Yu-Gi-Oh formatting style with internet humor. CRITICAL: MAXIMUM 280 CHARACTERS TOTAL including spaces and punctuation - this is a hard limit to ensure text fits in the card. Use only basic ASCII characters (letters, numbers, spaces, and . , ! ? ' -).
6. Suggest 2-3 visual effects that would enhance the card's personality aesthetically.

Examples:
- Things about being the life of the party → Type: "Juice", Stats: "Charisma"/2400, "Energy"/2100
- Things about always ghosting plans → Type: "Ghost", Stats: "Vanish Speed"/2800, "Commitment"/200
- Things about excessive flexing → Type: "Flex", Stats: "Clout"/2700, "Humility"/100"""
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
        
        # Extract and parse the generated JSON
        response_text = response.choices[0].message.content
        if response_text:
            print(f"[DEBUG] Raw response from OpenAI: {response_text[:200]}...")
            response_text = response_text.strip()
        else:
            print("[ERROR] Empty response from OpenAI API")
            return None
        
        # Try to extract JSON from the response
        try:
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
            
            # Sanitize and validate the response
            card_data = _validate_and_sanitize_card_data(card_data, traits)
            print(f"[SUCCESS] Generated card data with OpenAI for personality type: {card_data.get('custom_type', 'unknown')}")
            return card_data
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON response from OpenAI: {e}")
            print(f"[ERROR] Response text: {response_text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] OpenAI API call failed: {str(e)}")
        print(f"[ERROR] API error type: {type(e).__name__}")
        return None


def _validate_and_sanitize_card_data(card_data: Dict[str, Any], traits: List[str]) -> Dict[str, Any]:
    """
    Validate and sanitize card data from LLM response.
    
    Args:
        card_data (Dict[str, Any]): Raw card data from LLM
        traits (List[str]): Original input traits for validation
        
    Returns:
        Dict[str, Any]: Validated and sanitized card data
    """
    # Sanitize effect description
    effect_desc = card_data.get('effect_description', '') or ''
    card_data['effect_description'] = shorten_to_chars(sanitize_ascii(effect_desc), 280)
    
    # Ensure required fields exist with defaults
    card_data.setdefault('card_name', 'Unknown Card')
    card_data.setdefault('custom_type', 'Vibe')
    card_data.setdefault('stat1_name', 'Power')
    card_data.setdefault('stat1_value', 1000)
    card_data.setdefault('stat2_name', 'Defense')
    card_data.setdefault('stat2_value', 1000)
    card_data.setdefault('visual_effects', ['sparkles', 'glow'])
    
    # Sanitize card name
    card_data['card_name'] = sanitize_ascii(card_data['card_name'])[:25]
    
    return card_data


def generate_card_data(traits: List[str], gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Generate structured card data using LLM APIs with primary/fallback pattern.
    
    This function implements a primary/fallback system where Gemini is tried first,
    and if it fails, OpenAI is used as a fallback.
    
    Args:
        traits (List[str]): List of five character traits
        gemini_api_key (Optional[str]): Gemini API key for primary service
        openai_api_key (Optional[str]): OpenAI API key for fallback service
        
    Returns:
        Optional[Dict[str, Any]]: Generated card data if successful, None if failed
    """
    print("Generating character card data with LLM fallback system...")
    print(f"Traits count: {len(traits) if traits else 0}")
    print(f"Gemini API key provided: {'Yes' if gemini_api_key else 'No'}")
    print(f"OpenAI API key provided: {'Yes' if openai_api_key else 'No'}")
    
    # Validate input
    if not traits or len(traits) != 5:
        print("[ERROR] Exactly 5 traits are required")
        return None
    
    # 1. Primary Attempt: Google Gemini
    if gemini_api_key:
        try:
            print("Attempting API call with primary service (Gemini)...")
            gemini_model = _configure_gemini(gemini_api_key)
            if gemini_model:
                result = _call_gemini_api(traits, gemini_model)
                if result:
                    print("Successfully received response from Gemini.")
                    return result
                else:
                    print("Primary service (Gemini) failed. Falling back...")
            else:
                print("Primary service (Gemini) not available. Falling back...")
        except Exception as e:
            print(f"Primary service (Gemini) failed: {e}. Falling back...")
    
    # 2. Fallback: OpenAI
    if openai_api_key:
        try:
            print("Attempting API call with secondary service (OpenAI)...")
            openai_client = _configure_openai(openai_api_key)
            if openai_client:
                result = _call_openai_api(traits, openai_client)
                if result:
                    print("Successfully received response from OpenAI.")
                    return result
                else:
                    print("Secondary service (OpenAI) failed.")
            else:
                print("Secondary service (OpenAI) not available.")
        except Exception as e:
            print(f"Secondary service (OpenAI) failed: {e}")
    
    # 3. Final Failure
    print("Error: Both LLM services are currently unavailable or failed.")
    return None
