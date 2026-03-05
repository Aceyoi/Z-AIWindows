import os
import json
import threading
from pathlib import Path
from config import PROGRAMS_LOG_FILE, SEARCH_PATHS, SYSTEM_COMMANDS


class ProgramManager:
    def __init__(self):
        self.programs_db = {}
        self.load_cache()

    def load_cache(self):
        if os.path.exists(PROGRAMS_LOG_FILE):
            try:
                with open(PROGRAMS_LOG_FILE, 'r', encoding='utf-8') as f:
                    self.programs_db = json.load(f)
                print(f"📂 Загружено {len(self.programs_db)} программ из кэша")
            except:
                print("⚠️ Кэш сброшен")

    def save_cache(self):
        try:
            with open(PROGRAMS_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.programs_db, f, ensure_ascii=False, indent=2)
        except:
            pass

    def execute_command(self, text, log_callback, speak_callback=None):
        text_lower = text.lower()

        # Системные команды
        for cmd, exe in SYSTEM_COMMANDS.items():
            if cmd in text_lower:
                try:
                    os.startfile(exe)
                    log_callback(f"✅ {cmd.upper()} открыт")
                    if speak_callback:
                        speak_callback(f"Открываю {cmd}")
                    return
                except:
                    log_callback(f"❌ Ошибка запуска {cmd}")

        # Поиск программ
        if any(cmd in text_lower for cmd in ['открой', 'запусти', 'открыть']):
            words = text_lower.split()
            program_name = []
            for i, word in enumerate(words):
                if word in ['открой', 'открыть', 'запусти'] and i + 1 < len(words):
                    program_name = words[i + 1:]
                    break

            if program_name:
                self.execute_program(' '.join(program_name), log_callback)
            else:
                log_callback("❓ Укажите программу после команды")

    def execute_program(self, program_name, log_callback):
        program_name = program_name.strip().lower()
        log_callback(f"🔍 Поиск: '{program_name}'")

        # 1. Фаззи-поиск в кэше
        candidates = []
        for name in self.programs_db:
            a = set(program_name.split())
            b = set(name.split())
            similarity = len(a & b) / len(a | b) if a | b else 0
            if similarity > 0.3:
                candidates.append((name, similarity, self.programs_db[name]))

        candidates.sort(key=lambda x: x[1], reverse=True)

        # 2. Запуск из кэша
        for name, score, path in candidates[:3]:
            if os.path.exists(path):
                try:
                    os.startfile(path)
                    log_callback(f"✅ ОТКРЫТА: {name} ({score:.0%})")
                    return
                except:
                    continue

        # 3. Реал-тайм поиск
        found_path = self.find_exe_real_time(program_name)
        if found_path:
            try:
                os.startfile(found_path)
                name = Path(found_path).stem.lower()
                self.programs_db[name] = found_path
                self.programs_db[program_name] = found_path
                self.save_cache()
                log_callback(f"✅ НАЙДЕНА: {os.path.basename(found_path)}")
                return
            except:
                pass

        log_callback(f"❌ '{program_name}' не найдена")

    def find_exe_real_time(self, program_name):
        words = program_name.split()
        resolved_paths = [p() if callable(p) else p for p in SEARCH_PATHS]

        for base_path in resolved_paths:
            if not os.path.exists(base_path):
                continue
            try:
                for root, _, files in os.walk(base_path, max_depth=3):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            if any(word in file.lower() for word in words):
                                return os.path.join(root, file)
            except:
                continue
        return None

    def find_program(self, program_name):
        """Поиск для кнопки проверки"""
        candidates = []
        for name in self.programs_db:
            a = set(program_name.split())
            b = set(name.split())
            similarity = len(a & b) / len(a | b) if a | b else 0
            if similarity > 0.3:
                candidates.append((name, similarity))
        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def scan_all(self, log_callback):
        """🔍 Полное сканирование с логом"""
        log_callback("🔍 Полное сканирование...")
        programs = dict(self.programs_db)
        resolved_paths = [p() if callable(p) else p for p in SEARCH_PATHS]

        total_new = 0
        for root_path in resolved_paths:
            if os.path.exists(root_path):
                log_callback(f"📁 {os.path.basename(root_path) or root_path}")
                try:
                    for root_dir, _, files in os.walk(root_path, max_depth=2):
                        for file in files:
                            if file.lower().endswith('.exe'):
                                name = Path(file).stem.lower()
                                full_path = os.path.join(root_dir, file)
                                if name not in programs and os.path.exists(full_path):
                                    programs[name] = full_path
                                    total_new += 1
                except:
                    pass

        self.programs_db = programs
        self.save_cache()
        log_callback(f"✅ ДОБАВЛЕНО {total_new} ПРОГРАММ")
        log_callback(f"✅ ВСЕГО: {len(programs)}")

