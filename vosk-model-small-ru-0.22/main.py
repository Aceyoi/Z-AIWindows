import speech_to_text
import text_to_speech

API_KEY = 'AQVN2mU0rIOJ2nAexS8Lp92oSCP0wQ98kUekF7rK'

if __name__ == "__main__":
    while True:
        print("\nОжидаю команду...")
        recognized_text = speech_to_text.recognize_speech()
        if not recognized_text:
            continue

        if recognized_text.lower() in ["выход", "стоп", "exit"]:
            print("Завершение работы.")
            break

        print("Синтезируем речь...")
        try:
            audio = text_to_speech.synthesize(API_KEY, recognized_text)
            text_to_speech.play_audio(audio)
        except Exception as e:
            print("Ошибка синтеза или воспроизведения:", e)