from langdetect import detect
from .constants import NEPALI_CHARS

def detect_language(text):
    """Detect language of input text"""
    try:
        # Check for Nepali characters (Devanagari script)
        if any(char in text for char in NEPALI_CHARS):
            return 'ne'  # Nepali
        
        # Use langdetect for other languages
        detected = detect(text)
        return detected
    except:
        return 'en'  # Default to English