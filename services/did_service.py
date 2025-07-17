import requests
import json
import os
from core.config import DID_API_KEY

DID_BASE_URL = "https://api.d-id.com"

def create_headers():
    return {
        "Authorization": f"Bearer {DID_API_KEY}",
        "Content-Type": "application/json"
    }

def create_talk_request(photo_url: str, text: str):
    return {
        "script": {
            "type": "text",
            "input": text,
            "provider": {"type": "google", "voice_id": "ru-RU-Wavenet-C"},
        },
        "source_url": photo_url
    }

def animate_photo(photo_url: str, text: str) -> str:
    response = requests.post(
        f"{DID_BASE_URL}/talks",
        headers=create_headers(),
        data=json.dumps(create_talk_request(photo_url, text))
    )
    response.raise_for_status()
    id_ = response.json().get("id")

    # Ожидаем генерацию видео
    for _ in range(30):
        result = requests.get(f"{DID_BASE_URL}/talks/{id_}", headers=create_headers())
        result.raise_for_status()
        data = result.json()
        if "result_url" in data:
            return data["result_url"]
        import time; time.sleep(2)

    raise Exception("⏳ Время ожидания превысило лимит.")

