import requests

api_key = "AIzaSyCUeI2CsA8N2KMegUEtDBreE46ypLbCfvM"

try:
    response = requests.get(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print("Available models:")
        for model in models.get('models', []):
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                print(f"- {model['name']}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")