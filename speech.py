import threading
import pyaudio
import json
import os
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH


class SpeechManager:
    def __init__(self, callback):
        self.callback = callback
        self.model = None
        self.recognizer = None
        self.mic = None
        self.stream = None
        self.is_listening = False
        self.init_vosk()

    def init_vosk(self):
        if not os.path.exists(VOSK_MODEL_PATH):
            self.callback("❌ Скачайте vosk-model-small-ru-0.22")
            return

        try:
            self.model = Model(VOSK_MODEL_PATH)
            self.callback("✅ VOSK модель загружена")
        except Exception as e:
            self.callback(f"❌ VOSK ошибка: {e}")

    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False

    def _listen_loop(self):
        try:
            if not self.model:
                return

            self.mic = pyaudio.PyAudio()
            self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                                        input=True, frames_per_buffer=4096)
            self.stream.start_stream()
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.callback("🔊 Микрофон активен")

            while self.is_listening:
                data = self.stream.read(4096, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip().lower()
                    if text:
                        threading.Thread(target=self.callback, args=(f"🎤 '{text}'",), daemon=True).start()
                        # Передаём распознанный текст в UI для обработки
                        self._process_command(text)
        except Exception as e:
            self.callback(f"❌ Микрофон ошибка: {e}")
        finally:
            self._cleanup()

    def _process_command(self, text):
        """Передача команды в UI для обработки"""
        # Здесь можно добавить прямую обработку или передать в UI
        pass

    def _cleanup(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
        self.is_listening = False
