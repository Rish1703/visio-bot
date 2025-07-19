import requests
from core.config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

OPENAI_URL = "https://api.openai.com/v1/images/edits"

def edit_image_with_dalle(image_path: str, prompt: str) -> str:
    """
    Отправляет изображение и описание в DALL·E 2 (inpainting).
    Возвращает URL готового изображения.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    logger.debug(f"⏳ Отправляем запрос в DALL·E 2 с prompt: {prompt}")
    print(f"[DEBUG] Отправка в DALL·E: prompt={prompt}, image_path={image_path}")

    with open(image_path, "rb") as image_file:
        files = {
            "image": (image_path, image_file, "image/png"),
            "mask": (None, None),  # без маски редактируется всё
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }

        response = requests.post(OPENAI_URL, headers=headers, files=files, data=data)

        print("[DEBUG] Ответ DALL·E статус:", response.status_code)
        print("[DEBUG] Ответ DALL·E тело:", response.text)

        response.raise_for_status()

        return response.json()["data"][0]["url"]

def edit_photo(image_path: str, prompt: str) -> str:
    return edit_image_with_dalle(image_path, prompt)
