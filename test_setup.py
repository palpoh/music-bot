import os
import sys
import time
import requests

time.sleep(3) # Пауза для сети

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0"

# Пытаемся сделать запрос с явным указанием таймаутов
try:
    print(f"Отправка запроса: {prompt}")
    response = requests.post(
        API_URL, 
        headers={"Authorization": f"Bearer {TOKEN}"}, 
        json={"inputs": prompt},
        timeout=60 # Увеличили таймаут
    )
    
    if response.status_code == 200:
        with open("final_fixed.wav", "wb") as f:
            f.write(response.content)
        print("Успех.")
    else:
        print(f"Ошибка API {response.status_code}: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"Критическая ошибка сети: {e}")
    sys.exit(1)
