import wave
import pyaudio
import os
import audioop
import whisper

import warnings
warnings.filterwarnings("ignore")

from openai_helper import ask_computer
from openai_helper import transcribe_audio_remote

# Параметры
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(SCRIPT_DIR, "recorded.wav")
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 1024
SILENCE_THRESHOLD = 1000
MAX_SILENCE_SECONDS = 8 # Сколько секунд тишины в конце запроса

MAX_SILENCE_BUFFERS = int(RATE / FRAMES_PER_BUFFER * MAX_SILENCE_SECONDS) 

# Запись аудио с автоостановкой по тишине
def record_until_silence():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=FRAMES_PER_BUFFER)

    print("Говорите. Запись остановится после паузы...")
    frames = []
    silence_count = 0

    while True:
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frames.append(data)
        sound_volume = audioop.rms(data, 2)  # Оценка громкости
        
        #Если громкость меньше порога, длительность тишины увеличивается
        if sound_volume < SILENCE_THRESHOLD:
            silence_count += 1
        else:
            silence_count = 0

        if silence_count > MAX_SILENCE_BUFFERS:
            break

    #Окончание записи запроса
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        
    print("Запись завершена.")

#Распознавание речи через локальный Whisper medium модели
def transcribe_audio_local(recorded_voice_file, whisper_model):
    result = whisper_model.transcribe(recorded_voice_file)
    return result["text"]

if __name__ == "__main__":
    model = None
    use_remote = input("Использовать удалённую версию Whisper через OpenAI API? y/n: ").strip().lower() == "y"
    if use_remote:
        print("Используется удаленная вресия Whisper")
    else:
        print("Загрузка локальной модели Whisper medium...")
        model = whisper.load_model("medium")
    
    try:
        while True:
            #Запись до окончания речи
            print("Запись голосового запроса... (Ctrl+C для выхода)")
            record_until_silence()
            
            #Расшифровка сообщения
            if use_remote:
                text = transcribe_audio_remote(FILENAME)
            else:
                text = transcribe_audio_local(FILENAME, model)
            print("Вы сказали:", text)
            
            #Ответ от Chat GPT
            response = ask_computer(text)
            print("Ответ:")
            print(response)
            
            #Повторный запрос
            print("Нажмите Enter, чтобы спросить еще раз... (Ctrl+C для выхода)")
            input()
    except KeyboardInterrupt:
        print("Завершение работы.")