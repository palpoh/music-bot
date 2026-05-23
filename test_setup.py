import os
import sys
import requests
import time

# Ждем старта сети
time.sleep(5)

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Используем IP-адрес Hugging Face напрямую, чтобы не зависеть от DNS Render
# 18.154.20.158 - это один из IP API Hugging Face
API_URL = "https://18.154.20.158/models/stabilityai/stable-audio-open-1.0"

# ВАЖНО: При запросе по IP сервер требует указать имя хоста в заголовке
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Host": "api-inference.huggingface.co"
}

print(f"Отправка запроса через IP: {prompt}")

try:
    response = requests.post(
        API_URL, 
        headers=headers, 
        json={"inputs": prompt},
        timeout=120,
        verify=False # Игнорируем SSL, так как используем IP
    )
    
    if response.status_code == 200:
        with open("final_fixed.wav", "wb") as f:
            f.write(response.content)
        print("Успех: файл записан.")
    else:
        print(f"Ошибка API (код {response.status_code}): {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"Ошибка соединения: {e}")
    sys.exit(1)
