import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import json
import pyaudio

def recognize_with_vosk(model_path):
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    print("Слушаю...")

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    final_result = ""

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = json.loads(result)
            text = result_json.get("text", "")
            if text:
                print("Вы сказали: " + text)
                final_result = text
                break

    stream.stop_stream()
    mic.terminate()

    return final_result


def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("\nВыберите способ распознавания:")
    print("1 - Whisper")
    print("2 - Vosk")

    choice = input("Введите номер: ")


    if choice == "1":
        print("Говорите...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_whisper(audio, language="russian")
            print("Вы сказали:", text)
            return text
        except Exception as e:
            print("Ошибка:", e)
            return ""

    elif choice == "2":
        vosk_model_path = "vosk-model-small-ru-0.22"
        return recognize_with_vosk(vosk_model_path)

    else:
        print("Неверный выбор")
        return ""