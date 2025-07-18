import httpx
import asyncio
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
            "provider": {
                "type": "google",
                "voice_id": "ru-RU-Wavenet-C"
            }
        },
        "source_url": photo_url
    }

async def animate_photo(photo_url: str, text: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            # 1. Отправка запроса на создание анимации
            talk_response = await client.post(
                f"{DID_BASE_URL}/talks",
                headers=create_headers(),
                json=create_talk_request(photo_url, text)
            )
            talk_response.raise_for_status()
            talk_id = talk_response.json().get("id")

            if not talk_id:
                raise Exception("❌ Не удалось получить ID анимации от D-ID")

            # 2. Ожидание генерации результата
            for _ in range(30):
                status_response = await client.get(
                    f"{DID_BASE_URL}/talks/{talk_id}",
                    headers=create_headers()
                )
                status_response.raise_for_status()
                data = status_response.json()

                result_url = data.get("result_url")
                if result_url:
                    return result_url

                await asyncio.sleep(2)

        raise Exception("⏳ Видео не было сгенерировано в течение времени ожидания.")

    except httpx.RequestError as e:
        raise Exception(f"❌ Ошибка при запросе к D-ID API: {e}")
    except Exception as e:
        raise Exception(f"❌ Ошибка: {e}")
