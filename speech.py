import threading
import pyaudio
import json
import os
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH

class SpeechManager:
    def __init__(self, log_func):
        self.log = log_func
        self.model = None
        self.is_listening = False
        self.init_vosk()

    def init_vosk(self):
        if not os.path.exists(VOSK_MODEL_PATH):
            self.log("[ERROR] VOSK model not found")
            return
        self.model = Model(VOSK_MODEL_PATH)
        self.log("[OK] VOSK model loaded")

    def start_listening(self, on_result_func):
        if self.is_listening: return
        self.is_listening = True
        threading.Thread(target=self._loop, args=(on_result_func,), daemon=True).start()

    def stop_listening(self):
        self.is_listening = False

    def _loop(self, callback):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            rec = KaldiRecognizer(self.model, 16000)
            while self.is_listening:
                data = stream.read(4000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get("text", "").strip()
                    if text:
                        callback(text)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            self.log(f"[ERROR] Mic: {e}")
        finally:
            p.terminate()