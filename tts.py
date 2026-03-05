import threading
import grpc
import io
import pydub
from playsound import playsound
import tempfile
import os
from cloudapi.output.yandex.cloud.ai.tts.v3 import tts_service_pb2_grpc, tts_pb2
from config import YANDEX_API_KEY


class TTSManager:
    def __init__(self):
        self.api_key = YANDEX_API_KEY

    def speak(self, text):
        """Синхронное воспроизведение"""
        try:
            audio = self._synthesize_speech(text)
            if audio:
                self._play_audio(audio)
        except Exception as e:
            print(f"TTS ошибка: {e}")

    def speak_async(self, text):
        """Асинхронное воспроизведение"""
        threading.Thread(target=self.speak, args=(text,), daemon=True).start()

    def _synthesize_speech(self, text):
        try:
            request = tts_pb2.UtteranceSynthesisRequest(
                text=text,
                output_audio_spec=tts_pb2.AudioSynthesizerSpec(container_audio=tts_pb2.ContainerAudio.WAV),
                hints=tts_pb2.Hints(voice="alexander", role=tts_pb2.Hints.GOOD, speed=1.1),
                loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS
            )
            creds = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', creds)
            stub = tts_service_pb2_grpc.SynthesizerStub(channel)
            audio_data = io.BytesIO()

            for response in stub.UtteranceSynthesis(request, metadata=[('authorization', f'Bearer {self.api_key}')]):
                audio_data.write(response.audio_chunk.data)
            audio_data.seek(0)
            return pydub.AudioSegment.from_wav(audio_data)
        except Exception:
            return None

    def _play_audio(self, audio_segment):
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.close()
                audio_segment.export(tmp.name, format='wav')
                playsound(tmp.name)
                os.remove(tmp.name)
        except Exception:
            pass
