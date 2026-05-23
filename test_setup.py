import os
import sys
import requests
import json

# Теперь скрипт берет токен из настроек Render (HF_TOKEN)
TOKEN = os.getenv("HF_TOKEN")

if not TOKEN:
    print("Ошибка: HF_TOKEN не найден в переменных окружения!")
    sys.exit(1)

prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0"
headers = {"Authorization": f"Bearer {TOKEN}"}

print(f"Отправка запроса: {prompt}")

try:
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    # Если статус 200 - это музыка
    if response.status_code == 200:
        with open("final_fixed.wav", "wb") as f:
            f.write(response.content)
        print("Успех: файл final_fixed.wav сохранен.")
    else:
        # Если что-то пошло не так (например, модель грузится)
        print(f"Ошибка API (код {response.status_code}): {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"Ошибка при запросе: {e}")
    sys.exit(1)
