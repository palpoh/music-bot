import os
import sys
import requests
import time
import dns.resolver

# Ждем старта сети
time.sleep(5)

# Настройка DNS через Google
resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8']

def get_ip_from_dns(host):
    try:
        answers = resolver.resolve(host, 'A')
        return str(answers[0])
    except:
        return host # Если DNS Google не помог, вернем имя как есть

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Резолвим IP перед запросом
hostname = "api-inference.huggingface.co"
ip = get_ip_from_dns(hostname)
API_URL = f"https://{ip}/models/stabilityai/stable-audio-open-1.0"

print(f"Запрос к {hostname} (IP: {ip})")

try:
    response = requests.post(
        API_URL, 
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Host": hostname  # ОБЯЗАТЕЛЬНО передаем имя хоста в заголовке
        }, 
        json={"inputs": prompt},
        timeout=120
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
