import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if not key:
    print("Error: GEMINI_API_KEY is missing or empty in .env!")
    exit(1)

print(f"Testing GEMINI_API_KEY: {key[:6]}...{key[-6:] if len(key) > 12 else ''}")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [{"parts": [{"text": "Hello, are you active?"}]}]
}

try:
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    print("Status Code:", resp.status_code)
    if resp.status_code == 200:
        print("✓ Gemini API is active and working successfully!")
        try:
            print("Reply:", resp.json()["candidates"][0]["content"]["parts"][0]["text"])
        except Exception:
            print("Response:", resp.json())
    else:
        print("✗ Gemini API returned an error:")
        print(resp.text)
except Exception as e:
    print("✗ Request failed:", e)
