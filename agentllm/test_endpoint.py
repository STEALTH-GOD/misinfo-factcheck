import sys
import requests
import json

# Test the verify_claim endpoint
url = "http://127.0.0.1:8000/api/verify_claim"
payload = {
    "claim": "Nepal is a beautiful country",
    "lang": "ne"
}

print("Testing /api/verify_claim endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ SUCCESS!")
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print(f"\n✗ ERROR: {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
    sys.exit(1)
