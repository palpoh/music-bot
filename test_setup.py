import os
import sys
import time
from huggingface_hub import InferenceClient

# Ждем старта сети
time.sleep(5)

TOKEN = os.getenv("HF_TOKEN")
prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hard drill rap beat"

# Используем официальный клиент, он сам управляет заголовками и соединениями
client = InferenceClient(token=TOKEN)

print(f"Запрос через InferenceClient: {prompt}")

try:
    # Официальный метод для text-to-audio
    audio_data = client.text_to_speech(
        model="stabilityai/stable-audio-open-1.0",
        text=prompt
    )
    
    # Сохраняем результат
    with open("final_fixed.wav", "wb") as f:
        f.write(audio_data)
    print("Успех: файл записан.")

except Exception as e:
    print(f"Ошибка при работе с InferenceClient: {e}")
    sys.exit(1)
