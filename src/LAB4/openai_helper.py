import openai
import os
from pathlib import Path

# Путь к файлу относительно местоположения скрипта
KEY_FILE = "openai_key.txt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, KEY_FILE)

# Чтение ключа
try:
    with open(KEY_PATH, "r") as key_file:
        openai.api_key = key_file.read().strip()
except FileNotFoundError:
    raise RuntimeError(f"Файл {KEY_PATH} не найден. Убедитесь, что он существует и содержит API-ключ OpenAI.")

def ask_computer(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты — эксперт по нейронным сетям. Отвечай только по теме нейронных сетей, глубокого обучения и машинного обучения. Если вопрос не по теме, вежливо сообщи, что он выходит за рамки твоей компетенции и предложи пообщаться на тему глубокого обучения."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def transcribe_audio_remote(recorded_voice_file):
    with open(recorded_voice_file, "rb") as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="json"
        )
    return response.text