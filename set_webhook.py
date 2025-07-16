import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")  # Добавь в .env этот параметр

# Установить webhook
def set_webhook():
    webhook_url = f"{RAILWAY_URL}/webhook"
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(telegram_url, json={"url": webhook_url})

    if response.ok:
        print(f"✅ Webhook установлен: {webhook_url}")
    else:
        print(f"❌ Ошибка установки webhook: {response.text}")

if __name__ == "__main__":
    set_webhook()
