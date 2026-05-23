import os
import sys
import subprocess

TOKEN = os.getenv("HF_TOKEN")
if not TOKEN:
    print("Ошибка: HF_TOKEN не найден!")
    sys.exit(1)

prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Используем curl с принудительными DNS 8.8.8.8 (Google)
# Это обходит внутренние проблемы DNS в облаке Render
cmd = [
    "curl", "-v", "--dns-servers", "8.8.8.8",
    "-X", "POST",
    "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", f'{{"inputs": "{prompt}"}}',
    "-o", "final_fixed.wav"
]

print(f"Отправка запроса через curl: {prompt}")

try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if os.path.exists("final_fixed.wav") and os.path.getsize("final_fixed.wav") > 100:
        print("Успех: файл сохранен.")
    else:
        print(f"Ошибка: Файл пуст. Лог curl: {result.stderr}")
        sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"Ошибка subprocess: {e.stderr}")
    sys.exit(1)
