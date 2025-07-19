import requests
from core.config import OPENAI_API_KEY

OPENAI_URL = "https://api.openai.com/v1/images/edits"


def edit_image_with_dalle(image_path: str, prompt: str) -> str:
    """
    Отправляет изображение и описание в DALL·E 2 (inpainting).
    Возвращает URL с готовым отредактированным изображением.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    with open(image_path, "rb") as image_file:
        files = {
            "image": ("image.png", image_file, "image/png"),
            "mask": (None, None)  # Без маски — редактируется всё изображение
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }

        response = requests.post(OPENAI_URL, headers=headers, files=files, data=data)

        try:
            response.raise_for_status()
            return response.json()["data"][0]["url"]
        except Exception as e:
            raise RuntimeError(f"Ошибка DALL·E 2: {response.text}") from e


def edit_photo(image_path: str, prompt: str) -> str:
    """
    Универсальная функция, вызываемая извне (из хендлера Telegram).
    """
    return edit_image_with_dalle(image_path, prompt)
