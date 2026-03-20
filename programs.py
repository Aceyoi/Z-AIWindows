import os
import json
import subprocess
from pathlib import Path
from config import PROGRAMS_LOG_FILE, SEARCH_PATHS, SYSTEM_COMMANDS, GREETINGS, EXIT_COMMANDS


class ProgramManager:
    def __init__(self):
        self.db = {}
        self.load_cache()

    def load_cache(self):
        if os.path.exists(PROGRAMS_LOG_FILE):
            try:
                with open(PROGRAMS_LOG_FILE, 'r', encoding='utf-8') as f:
                    self.db = json.load(f)
            except:
                pass

    def save_cache(self):
        with open(PROGRAMS_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

    def execute_command(self, text, log_cb, speak_cb):
        # Очистка текста от лишних знаков
        text = text.lower().strip()
        if not text: return

        # 1. Проверка на "Пока" (Выход из программы)
        if 'пока' in text or 'выход' in text:
            log_cb("[EXIT] Завершение работы...")
            speak_cb("До свидания! Выключаюсь.")
            # Даем небольшую паузу, чтобы успела прозвучать фраза, и закрываем
            import time
            time.sleep(2)
            os._exit(0)  # Жесткое завершение всех потоков и окна
            return

        # 1. Проверка на приветствия (поиск подстроки)
        for word, response in GREETINGS.items():
            if word in text:
                log_cb(f"[INFO] Общение: {word}")
                speak_cb(response)
                return

        # 2. Проверка на команды закрытия
        if any(word in text for word in ['закрой', 'выключи', 'заверши']):
            for cmd_trigger, process in EXIT_COMMANDS.items():
                # Ищем ключевое слово программы в тексте
                prog_label = cmd_trigger.replace('закрой ', '')
                if prog_label in text:
                    os.system(f"taskkill /f /im {process}")
                    log_cb(f"[OK] Закрыто: {process}")
                    speak_cb(f"Закрываю {prog_label}")
                    return

        # 3. Системные команды на открытие (без жесткой привязки к началу строки)
        for cmd, exe in SYSTEM_COMMANDS.items():
            if cmd in text:
                os.startfile(exe)
                log_cb(f"[OK] Запуск: {cmd}")
                speak_cb(f"Открываю {cmd}")
                return

        # 4. Поиск через ключевые слова 'открой' или 'запусти'
        keywords = ['открой', 'запусти', 'открыть']
        if any(k in text for k in keywords):
            # Убираем ключевое слово, оставляем только название
            clean_name = text
            for k in keywords:
                clean_name = clean_name.replace(k, '')
            self._launch(clean_name.strip(), log_cb, speak_cb)
        else:
            # Если ключевых слов нет, пробуем поискать всё предложение в базе
            self._launch(text, log_cb, speak_cb)

    def _launch(self, name, log_cb, speak_cb):
        # Поиск в кэше
        for k in self.db:
            if name in k or k in name:
                os.startfile(self.db[k])
                log_cb(f"[OK] Из кэша: {k}")
                speak_cb(f"Запускаю {k}")
                return

        # Поиск в реальном времени
        path = self._scan_for(name)
        if path:
            os.startfile(path)
            self.db[name] = path
            self.save_cache()
            log_cb(f"[OK] Найдено: {name}")
            speak_cb(f"Нашла и запускаю {name}")
        else:
            log_cb(f"[FAIL] Не найдено: {name}")
            speak_cb(f"Я не нашла программу {name}")

    def _scan_for(self, name):
        # Получаем все пути, включая результат выполнения lambda-функций
        paths = [p() if callable(p) else p for p in SEARCH_PATHS]

        name = name.lower()
        for base_path in paths:
            if not os.path.exists(base_path):
                continue

            try:
                # Рекурсивный обход
                for root, dirs, files in os.walk(base_path):
                    # Ограничение глубины (чтобы не уходить в дебри системных папок)
                    depth = root.count(os.sep) - base_path.count(os.sep)
                    if depth > 3:
                        del dirs[:]  # Перестаем заходить глубже в подпапки
                        continue

                    for f in files:
                        if f.lower().endswith('.exe'):
                            # Если имя файла содержит искомое слово (например, "steam")
                            if name in f.lower():
                                full_path = os.path.join(root, f)
                                return full_path
            except PermissionError:
                continue  # Пропускаем папки, куда нет доступа
            except Exception:
                continue
        return None

    def scan_all(self, log_cb):
        log_cb("[SCAN] Начато полное сканирование...")
        paths = [p() if callable(p) else p for p in SEARCH_PATHS]
        for p in paths:
            if not os.path.exists(p): continue
            try:
                for root, _, files in os.walk(p):
                    for f in files:
                        if f.lower().endswith('.exe'):
                            self.db[Path(f).stem.lower()] = os.path.join(root, f)
                    if root.count(os.sep) - p.count(os.sep) > 1: break
            except:
                continue
        self.save_cache()
        log_cb(f"[SCAN] Готово. В базе: {len(self.db)}")