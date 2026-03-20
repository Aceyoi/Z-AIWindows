import grpc
import io
import pydub
from cloudapi.output.yandex.cloud.ai.tts.v3 import tts_service_pb2_grpc, tts_pb2
from playsound import playsound
import os
import tempfile


def synthesize(iam_token, text) -> pydub.AudioSegment:
    request = tts_pb2.UtteranceSynthesisRequest(
        text=text,
        output_audio_spec=tts_pb2.AudioFormatOptions(
            container_audio=tts_pb2.ContainerAudio(
                container_audio_type=tts_pb2.ContainerAudio.WAV
            )
        ),
        hints=[
            tts_pb2.Hints(voice='alexander'),
            tts_pb2.Hints(role='good'),
            tts_pb2.Hints(speed=1.1),
        ],
        loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS
    )

    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', cred)
    stub = tts_service_pb2_grpc.SynthesizerStub(channel)

    it = stub.UtteranceSynthesis(request, metadata=(
        ('authorization', f'Bearer {iam_token}'),
    ))

    try:
        audio = io.BytesIO()
        for response in it:
            audio.write(response.audio_chunk.data)
        audio.seek(0)
        return pydub.AudioSegment.from_wav(audio)
    except grpc._channel._Rendezvous as err:
        print(f'Ошибка TTS: {err._state.code}, сообщение: {err._state.details}')
        raise err


def play_audio(audio_segment):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmpfile.close()
        audio_segment.export(tmpfile.name, format="wav")
        playsound(tmpfile.name)
        os.remove(tmpfile.name)