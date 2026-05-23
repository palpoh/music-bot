import os
import sys
import subprocess

# Токен Hugging Face из настроек Render
HF_TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Формируем JSON-запрос в файл
with open("payload.json", "w") as f:
    f.write(f'{{"inputs": "{prompt}"}}')

# Используем curl с флагом --insecure (игнорирует SSL-ошибки) и через прокси, если нужно
# Если VPN работает в системе, curl его подхватит автоматически
cmd = [
    "curl", "-s", "--insecure",
    "-X", "POST",
    "https://api-inference.huggingface.co/models/stabilityai/stable-audio-open-1.0",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", f'{{"inputs": "{prompt}"}}',
    "-o", "final_fixed.wav"
]

print("Запуск через curl с обходом SSL...")
subprocess.run(cmd, check=True)

if os.path.exists("final_fixed.wav") and os.path.getsize("final_fixed.wav") > 100:
    print("Успех!")
else:
    print("Генерация провалилась. Проверь размер файла final_fixed.wav")
    sys.exit(1)
