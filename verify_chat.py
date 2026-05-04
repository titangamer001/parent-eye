import requests
import json

base_url = "http://127.0.0.1:5000"

print("--- DASHBOARD TEST ---")
try:
    url = f"{base_url}/api/dashboard?user=parent1&lang=te"
    response = requests.get(url)
    data = response.json()
    print(f"Remarks (TE): {data.get('remarks')}")
    print(f"Notification 0 (TE): {data.get('notifications')[0].get('message')}")
except Exception as e:
    print(f"Dashboard Error: {e}")

print("\n--- CHATBOT TEST ---")
url = f"{base_url}/api/chat"
headers = {"Content-Type": "application/json"}
payload = {
    "message": "నా బిడ్డ పనితీరు ఎలా ఉంది?",
    "user": "parent1",
    "lang": "te"
}
try:
    response = requests.post(url, json=payload)
    data = response.json()
    print(f"Input (TE): {payload['message']}")
    print(f"Response (TE): {data.get('response')}")
    print(f"Original (EN): {data.get('original')}")
    print(f"Status: {'SUCCESS' if 'response' in data else 'FAILED'}")
except Exception as e:
    print(f"Chat Error: {e}")
