import os

# API и Пути
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')
PROGRAMS_LOG_FILE = "programs_log.json"
VOSK_MODEL_PATH = "vosk-model-small-ru-0.22"

# Пути поиска
SEARCH_PATHS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Windows",
    r"Z:\Steam",
    r"Z:",
    r"D:",
    lambda: os.path.expanduser(r"~\Desktop"),
    lambda: os.path.join(os.path.expanduser("~"), "AppData", "Local"),
    lambda: os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
]

# Словари фраз для "общения"
GREETINGS = {
    'привет': 'Здравствуйте! Чем могу помочь?',
    'здравствуй': 'Приветствую. Жду ваших указаний.',
    'как дела': 'У меня всё отлично, я готов к работе.',
    'кто ты': 'Я ваш персональный голосовой помощник.',
    'пока': 'До свидания! Завершаю работу.' # Новая команда
}

# Команды на закрытие программ (имена процессов)
EXIT_COMMANDS = {
    'закрой блокнот': 'notepad.exe',
    'закрой калькулятор': 'calc.exe',
    'закрой браузер': 'chrome.exe',
    'закрой проводник': 'explorer.exe',
    'закрой папку': 'explorer.exe',
    'закрой задачи': 'taskmgr.exe'
}

# Расширенный список системных программ
SYSTEM_COMMANDS = {
    'блокнот': 'notepad.exe',
    'калькулятор': 'calc.exe',
    'диспетчер': 'taskmgr.exe',
    'задачи': 'taskmgr.exe',
    'командная строка': 'cmd.exe',
    'панель управления': 'control.exe',
    'ножницы': 'SnippingTool.exe',
    'рисование': 'mspaint.exe',
    'браузер': 'chrome.exe', # или msedge.exe
    'папку': 'explorer.exe',
    'проводник': 'explorer.exe',
    'тим':'steam.exe'
}