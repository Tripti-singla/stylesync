import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if not key:
    print("Error: GEMINI_API_KEY missing.")
    exit(1)

models = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-pro"
]

print(f"Testing models with API Key: {key[:6]}...")

for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Model {model:20} -> Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("  ✓ SUCCESS!")
        elif resp.status_code == 429:
            print("  ✗ 429 Too Many Requests (Rate limit/quota exceeded)")
        else:
            print(f"  ✗ Failed: {resp.text[:120]}")
    except Exception as e:
        print(f"Model {model} failed: {e}")
