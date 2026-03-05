import tkinter as tk
import threading
from ui import VoiceAssistantUI
from speech import SpeechManager
from tts import TTSManager
from programs import ProgramManager
import time


def main():
    root = tk.Tk()

    # Инициализация менеджеров
    program_manager = ProgramManager()
    tts_manager = TTSManager()

    def log_callback(message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        # Лог передаётся в UI

    speech_manager = SpeechManager(log_callback)

    # UI
    app = VoiceAssistantUI(root, speech_manager, tts_manager, program_manager)

    # Обработка голосовых команд
    def process_voice(text):
        app.log(f"🎤 ГОЛОС: '{text}'")
        app.text_input.delete(1.0, tk.END)
        app.text_input.insert(1.0, text)
        program_manager.execute_command(text, app.log, tts_manager.speak)

    # Запуск
    root.protocol("WM_DELETE_WINDOW", lambda: (
        speech_manager.stop_listening(),
        root.destroy()
    ))
    root.mainloop()


if __name__ == "__main__":
    main()
