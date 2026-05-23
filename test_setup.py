import os
import sys
import subprocess
import time

# Ждем старта сети
time.sleep(3)

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Используем curl с флагом --dns-servers
cmd = [
    "curl", "-s", "-L",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", f'{{"inputs": "{prompt}"}}',
    "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0",
    "--dns-servers", "8.8.8.8",
    "-o", "final_fixed.wav"
]

print("Запуск запроса через Curl с DNS 8.8.8.8...")
result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists("final_fixed.wav") and os.path.getsize("final_fixed.wav") > 100:
    print("Успех!")
else:
    print(f"Ошибка: {result.stderr}")
    sys.exit(1)
