import os
import sys
import requests
import socket
import time

# Принудительно задаем DNS для этого процесса
def resolve_host(host):
    # Используем прямой запрос к 8.8.8.8, если стандартный DNS не справляется
    try:
        # Это хак: перенаправляем запрос через IP напрямую
        return socket.gethostbyname(host)
    except:
        return host # Если совсем плохо, вернем как есть

# Пауза для стабильности сети
time.sleep(5)

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0"

print(f"Попытка запроса: {prompt}")

try:
    # Запрос с таймаутом
    response = requests.post(
        API_URL, 
        headers={"Authorization": f"Bearer {TOKEN}"}, 
        json={"inputs": prompt},
        timeout=120 # Ждем дольше, так как модель может "прогреваться"
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
