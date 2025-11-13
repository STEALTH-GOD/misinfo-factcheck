from dotenv import load_dotenv
load_dotenv()

import requests
import json

print('Testing /api/verify_claim endpoint...\n')

url = "http://127.0.0.1:8000/api/verify_claim"
payload = {
    "claim": "Nepal is located in South Asia",
    "lang": "ne"
}

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('\n✓ SUCCESS!\n')
        print(json.dumps(result, indent=2))
    else:
        print(f'\n✗ ERROR: {response.status_code}')
        print(response.text)
except requests.exceptions.ConnectionError:
    print('✗ Connection Error: Is the server running?')
except Exception as e:
    print(f'✗ Exception: {e}')
