import requests
import time
import random

def get_ai_response(user_message):
    """Get AI response from Google Gemini API with retry logic"""
    api_key = "AIzaSyCUeI2CsA8N2KMegUEtDBreE46ypLbCfvM"
    
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    health_prompt = f"You are Dr. LifeSync, a professional health and nutrition expert. Answer this health question directly with specific, actionable advice: {user_message}. Provide practical tips, exercises, or nutritional guidance. Be conversational but informative. Keep under 200 words."
    
    for model in models:
        for attempt in range(3):
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                    headers={'Content-Type': 'application/json'},
                    json={
                        "contents": [{"parts": [{"text": health_prompt}]}],
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            return candidate['content']['parts'][0]['text']
                
                elif response.status_code == 503:
                    wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                    print(f"Model {model} overloaded, waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Model {model} failed with status {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"Error with {model}: {e}")
                if attempt < 2:
                    time.sleep(1)
                continue
    
    return "I'm Dr. LifeSync! I'm experiencing high demand right now. Here's some general advice: For most health questions, focus on balanced nutrition, regular exercise, adequate sleep (7-9 hours), and staying hydrated. Please try asking again in a moment!"