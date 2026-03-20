import tkinter as tk
from ui import VoiceAssistantUI
from speech import SpeechManager
from tts import TTSManager
from programs import ProgramManager


def main():
    root = tk.Tk()

    # Инициализация менеджеров
    # Мы передаем заглушку в speech_manager, так как UI еще не создан
    tts_manager = TTSManager()
    program_manager = ProgramManager()

    # Создаем временную функцию лога, пока UI не инициализирован
    def temporary_log(msg): print(f"[INIT] {msg}")

    speech_manager = SpeechManager(temporary_log)

    # Создаем интерфейс
    app = VoiceAssistantUI(root, speech_manager, tts_manager, program_manager)

    # Обновляем логгер в speech_manager на логгер из интерфейса
    speech_manager.log = app.log

    root.mainloop()


if __name__ == "__main__":
    main()