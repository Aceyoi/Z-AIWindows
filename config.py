import os

# API ключи
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')
PROGRAMS_LOG_FILE = "programs_log.json"
VOSK_MODEL_PATH = "vosk-model-small-ru-0.22"

# Пути для поиска программ
SEARCH_PATHS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Windows",
    lambda: os.path.expanduser(r"~\Desktop"),
    lambda: os.path.expanduser(r"~\Downloads"),
    lambda: os.path.join(os.path.expanduser("~"), "AppData", "Local"),
    lambda: os.path.join(os.path.expanduser("~"), "AppData", "Roaming"),
    lambda: os.getenv('APPDATA'),
    lambda: os.getenv('LOCALAPPDATA')
]

# Системные команды
SYSTEM_COMMANDS = {
    'блокнот': 'notepad.exe',
    'ноутпад': 'notepad.exe',
    'калькулятор': 'calc.exe',
    'диспетчер': 'taskmgr.exe',
    'задачи': 'taskmgr.exe'
}
