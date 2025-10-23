import requests

api_key = "AIzaSyCUeI2CsA8N2KMegUEtDBreE46ypLbCfvM"

try:
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
        headers={'Content-Type': 'application/json'},
        json={
            "contents": [{"parts": [{"text": "Hello, how are you?"}]}]
        },
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")