from dotenv import load_dotenv
load_dotenv()

import os
import requests

# Test Groq API
GROQ_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL')

print(f"GROQ_MODEL: {GROQ_MODEL}")
print(f"GROQ_API_KEY present: {bool(GROQ_KEY)}")

if GROQ_KEY:
    url = 'https://api.groq.com/openai/v1/chat/completions'
    payload = {
        'model': GROQ_MODEL,
        'messages': [{'role': 'user', 'content': 'Say hello'}],
        'max_tokens': 10
    }
    headers = {'Authorization': f'Bearer {GROQ_KEY}', 'Content-Type': 'application/json'}
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"\nGroq API Response Status: {r.status_code}")
        if r.status_code == 200:
            print("✓ Groq API is working!")
            print(f"Response: {r.json()}")
        else:
            print(f"✗ Error: {r.text}")
    except Exception as e:
        print(f"✗ Exception: {e}")
