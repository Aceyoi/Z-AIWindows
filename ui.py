import tkinter as tk
from tkinter import scrolledtext, font
import time
import threading


class VoiceAssistantUI:
    def __init__(self, root, speech, tts, programs):
        self.root = root
        self.speech = speech
        self.tts = tts
        self.programs = programs
        self.is_listening = False
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Голосовой Помощник")
        self.root.geometry("850x750")
        self.root.configure(bg='#1e272e')  # Темная тема

        # Настройка шрифтов
        self.main_font = font.Font(family="Segoe UI", size=11)
        self.header_font = font.Font(family="Segoe UI Semibold", size=18)

        # Консоль вывода (Лог)
        self.output = scrolledtext.ScrolledText(
            self.root, bg='#2f3542', fg='#ffffff',
            font=('Consolas', 10), borderwidth=0, padx=10, pady=10
        )
        self.output.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Поле ввода команд
        input_label = tk.Label(self.root, text="Введите команду вручную:",
                               bg='#1e272e', fg='#d2dae2', font=self.main_font)
        input_label.pack(padx=20, anchor='w')

        self.text_input = tk.Entry(
            self.root, bg='#ffffff', fg='#2f3542',
            font=self.main_font, borderwidth=5, relief=tk.FLAT
        )
        self.text_input.pack(fill=tk.X, padx=20, pady=5)
        self.text_input.bind('<Return>', lambda e: self.execute())

        # Панель кнопок
        btn_frame = tk.Frame(self.root, bg='#1e272e')
        btn_frame.pack(pady=20)

        # Стили кнопок
        btn_opts = {"font": self.main_font, "width": 18, "height": 2, "fg": "white", "relief": tk.FLAT}

        self.btn_mic = tk.Button(btn_frame, text="Слушать", command=self.toggle_mic,
                                 bg='#ff3f34', activebackground='#ff5e57', **btn_opts)
        self.btn_mic.pack(side=tk.LEFT, padx=10)

        self.btn_run = tk.Button(btn_frame, text="Выполнить", command=self.execute,
                                 bg='#05c46b', activebackground='#4bc233', **btn_opts)
        self.btn_run.pack(side=tk.LEFT, padx=10)

        self.btn_scan = tk.Button(btn_frame, text="Обновить кэш", command=self.scan,
                                  bg='#3c40c6', activebackground='#575fcf', **btn_opts)
        self.btn_scan.pack(side=tk.LEFT, padx=10)

        # Статус-бар
        self.status = tk.Label(self.root, text="Система готова к работе",
                               bg='#2f3542', fg='#0be881', font=('Segoe UI', 10))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.log("Ассистент успешно запущен!")

    def log(self, msg):
        """Безопасная запись в лог с временем"""

        def _update():
            t = time.strftime('%H:%M:%S')
            self.output.insert(tk.END, f"[{t}] {msg}\n")
            self.output.see(tk.END)

        self.root.after(0, _update)

    def set_status(self, text, color="#0be881"):
        """Обновление текста в статус-баре"""
        self.root.after(0, lambda: self.status.config(text=text, fg=color))

    def on_voice_command(self, text):
        """Гарантированная передача текста и запуск выполнения"""
        if not text:
            return

        # 1. Сразу останавливаем микрофон (внутренний флаг)
        self.is_listening = False
        self.speech.stop_listening()

        # 2. Обновляем визуальную часть через .after (потокобезопасно)
        self.root.after(0, self._process_and_run, text)

    def _process_and_run(self, text):
        """Вспомогательный метод для работы в главном потоке UI"""
        # Обновляем кнопку и статус
        self.btn_mic.config(text="🎤 Слушать", bg='#ff3f34')
        self.set_status("✅ Команда принята", "#0be881")

        # Записываем текст
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, text)
        self.log(f"🎤 Распознано: {text}")

        # Запускаем выполнение
        self.execute()

    def toggle_mic(self):
        if not self.is_listening:
            self.is_listening = True
            self.speech.start_listening(self.on_voice_command)
            self.btn_mic.config(text="Стоп", bg='#ef5777')
            self.log("Микрофон включен. Говорите...")
            self.set_status("Идет запись голоса...", "#ff3f34")
        else:
            self.is_listening = False
            self.speech.stop_listening()
            self.btn_mic.config(text="Слушать", bg='#ff3f34')
            self.log("Микрофон отключен.")
            self.set_status("Режим ожидания")

    def execute(self):
        cmd = self.text_input.get().strip()
        if not cmd:
            return

        # Запускаем выполнение в отдельном потоке, чтобы UI не завис на время старта программы
        threading.Thread(target=self.programs.execute_command,
                         args=(cmd, self.log, self.tts.speak), daemon=True).start()

    def scan(self):
        self.btn_scan.config(state=tk.DISABLED)
        self.set_status("Идет сканирование системы...", "#ffc048")

        def run_scan():
            self.programs.scan_all(self.log)
            self.root.after(0, lambda: self.btn_scan.config(state=tk.NORMAL))
            self.set_status("Сканирование завершено")

        threading.Thread(target=run_scan, daemon=True).start()