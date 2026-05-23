import os
import sys
import requests
import json

TOKEN = os.getenv("HF_TOKEN") # Берем из переменных окружения, а не хардкодим!
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0"
headers = {"Authorization": f"Bearer {TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

print(f"Запрос к Hugging Face: {prompt}")
audio_bytes = query({"inputs": prompt})

# Проверяем, не вернулась ли ошибка
try:
    error_data = json.loads(audio_bytes.decode('utf-8'))
    print(f"Ошибка API: {error_data}")
    sys.exit(1)
except:
    # Если не удалось распарсить как JSON, значит это бинарные данные (аудио)
    with open("final_fixed.wav", "wb") as f:
        f.write(audio_bytes)
    print("Файл успешно сохранен как final_fixed.wav")
