import requests
import time

# 👉 ВСТАВЬ СЮДА СВОЙ АКТУАЛЬНЫЙ КЛЮЧ
DID_API_KEY = "bWFyaXlhLmlueWFrb3ZhQGdtYWlsLmNvbQ:S-ezdVCgBkwfSJmLgcnEa"  # пример

headers = {
    "Authorization": f"Bearer {DID_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "script": {
        "type": "text",
        "input": "Привет! Это тестовая анимация.",
        "provider": {
            "type": "google",
            "voice_id": "ru-RU-Wavenet-C"
        }
    },
    "source_url": "https://i.imgur.com/4Z3ZKvw.jpeg"  # можешь заменить на свою ссылку
}

# 1. Запрос на создание анимации
print("⏳ Отправка запроса на создание анимации...")
response = requests.post("https://api.d-id.com/talks", headers=headers, json=data)
print("Статус ответа:", response.status_code)
print("Ответ:", response.text)

# 2. Проверка готовности и получение результата
if response.status_code == 201:
    talk_id = response.json().get("id")
    print(f"✅ Анимация создана. ID: {talk_id}")
    print("⏳ Ожидаем готовность видео...")

    for i in range(30):
        time.sleep(2)
        status_response = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
        result = status_response.json()

        if result.get("result_url"):
            print("✅ Готово! Вот ссылка на видео:")
            print(result["result_url"])
            break
        else:
            print(f"⏳ Попытка {i + 1}: пока не готово...")
else:
    print("❌ Ошибка при создании анимации. Проверь ключ, тариф и параметры запроса.")
