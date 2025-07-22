import requests
import logging
from core.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Эндпоинт редактирования изображений в DALL·E 2 (inpainting)
OPENAI_URL = "https://api.openai.com/v1/images/edits"

def edit_image_with_dalle(image_path: str, prompt: str) -> str:
    """
    Отправляет изображение и описание в DALL·E 2 (inpainting).
    Возвращает URL готового изображения.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    logger.info(f"📤 Отправка изображения в DALL·E 2. Prompt: '{prompt}'")
    print(f"[DEBUG] Отправка в DALL·E: prompt={prompt}, image_path={image_path}")

    with open(image_path, "rb") as image_file:
        files = {
            "image": ("image.png", image_file, "image/png"),
            "mask": (None, None),  # Без маски — редактируется всё изображение
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }

        try:
            response = requests.post(OPENAI_URL, headers=headers, files=files, data=data)

            logger.debug(f"📨 Статус ответа DALL·E: {response.status_code}")
            print("[DEBUG] Ответ DALL·E статус:", response.status_code)
            print("[DEBUG] Ответ DALL·E тело:", response.text)

            response.raise_for_status()

            json_data = response.json()
            if "data" in json_data and len(json_data["data"]) > 0:
                image_url = json_data["data"][0]["url"]
                logger.info(f"✅ Получено изображение: {image_url}")
                return image_url
            else:
                logger.error("❗ DALL·E не вернул изображение.")
                raise ValueError("❗ Ошибка: DALL·E не вернул изображение.")

        except requests.RequestException as e:
            logger.exception(f"🚨 Ошибка запроса к DALL·E: {e}")
            raise

        except Exception as e:
            logger.exception(f"🚫 Непредвиденная ошибка: {e}")
            raise

def edit_photo(image_path: str, prompt: str) -> str:
    """
    Универсальная функция, вызываемая из других частей кода.
    """
    return edit_image_with_dalle(image_path, prompt)
