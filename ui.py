import tkinter as tk
from tkinter import scrolledtext, messagebox
import time  # ✅ для timestamp
import threading  # ✅ для потоков сканирования
import os
from programs import ProgramManager


class VoiceAssistantUI:
    def __init__(self, root, speech_manager, tts_manager, program_manager):
        self.root = root
        self.speech_manager = speech_manager
        self.tts_manager = tts_manager
        self.program_manager = program_manager
        self.is_listening = False
        self.setup_ui()

    def setup_ui(self):
        self.root.title("🤖 Голосовой Ассистент VOSK")
        self.root.geometry("850x700")
        self.root.configure(bg='#2c3e50')

        # Заголовок
        title = tk.Label(self.root, text="🎤 Голосовой Ассистент - МОДУЛИ",
                         font=('Arial', 22, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=15)

        # Лог
        self.output = scrolledtext.ScrolledText(self.root, height=20, bg='#34495e', fg='white',
                                                font=('Consolas', 10), wrap=tk.WORD)
        self.output.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Поле ввода
        input_frame = tk.Frame(self.root, bg='#2c3e50')
        input_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(input_frame, text="💬 Команда:", bg='#2c3e50', fg='white',
                 font=('Arial', 11, 'bold')).pack(anchor='w')
        self.text_input = tk.Text(input_frame, height=3, bg='#ecf0f1', font=('Arial', 11))
        self.text_input.pack(fill=tk.X, pady=(5, 0))

        # Кнопки
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="🎤 Слушать", command=self.toggle_listening,
                  bg='#e74c3c', fg='white', font=('Arial', 13, 'bold'), width=14, height=2
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🔊 Сказать", command=self.speak_text,
                  bg='#27ae60', fg='white', font=('Arial', 13, 'bold'), width=14, height=2
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="⚡ Выполнить", command=self.execute_command,
                  bg='#3498db', fg='white', font=('Arial', 13, 'bold'), width=14, height=2
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🔍 Сканировать", command=self.scan_programs,
                  bg='#9b59b6', fg='white', font=('Arial', 11, 'bold'), width=14, height=2
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="❓ Проверить", command=self.check_program,
                  bg='#f1c40f', fg='black', font=('Arial', 11, 'bold'), width=14, height=2
                  ).pack(side=tk.LEFT, padx=5)

        # Статус
        self.status_label = tk.Label(self.root, text="⏳ Инициализация...",
                                     bg='#2c3e50', fg='#f39c12', font=('Arial', 14, 'bold'))
        self.status_label.pack(pady=10)

        self.log("🚀 Модульный ассистент готов!")

    def log(self, message):
        """✅ Логирование с timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.output.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output.see(tk.END)
        self.root.update()

    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.speech_manager.start_listening()
            self.status_label.config(text="🎤 СЛУШАЮ...", fg='#2ecc71')
            self.log("🎤 Слушаю голосовые команды...")
        else:
            self.is_listening = False
            self.speech_manager.stop_listening()
            self.status_label.config(text="⏸️ Остановлен", fg='#e67e22')
            self.log("🛑 Слушание остановлено")

    def speak_text(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.tts_manager.speak_async(text)
            self.log(f"🔊 Произношу: '{text[:50]}...'")

    def execute_command(self):
        """⚡ Выполнить текстовую команду"""
        text = self.text_input.get(1.0, tk.END).strip().lower()
        if not text:
            self.log("❌ Введите команду!")
            return

        self.log(f"⚡ Выполняю: '{text}'")
        self.program_manager.execute_command(text, self.log, self.tts_manager.speak)

    def scan_programs(self):
        """🔍 Сканировать программы в отдельном потоке"""
        threading.Thread(target=self.program_manager.scan_all, args=(self.log,), daemon=True).start()
        self.log("🔍 Запущено полное сканирование...")

    def check_program(self):
        """❓ Проверить наличие программы"""
        text = self.text_input.get(1.0, tk.END).strip().lower()
        if not text:
            messagebox.showwarning("Проверка", "Введите название программы!")
            return

        results = self.program_manager.find_program(text)
        if results:
            msg = "Найдены программы:\n\n" + "\n".join([f"• {r[0]} ({r[1]:.0%})" for r in results[:10]])
            messagebox.showinfo("✅ Найдено", msg)
            self.log(f"✅ Найдено {len(results)} совпадений")
        else:
            messagebox.showinfo("❌ Не найдено", "Программа не найдена в кэше")
