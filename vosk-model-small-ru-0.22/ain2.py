import os
import pyautogui
import psutil
import signal
import pygetwindow as gw


def open_process_by_name(process_name):
    os.startfile(process_name)

def close_active_window():
    pyautogui.hotkey('alt', 'f4')

def kill_process_by_name(process_name):
    window = gw.getWindowsWithTitle(process_name)
    if window:
        window[0].close()

def handle_command(text):
    text = text.lower()

    if "закрой блокнот" in text or "выключи блокнот" in text:
        kill_process_by_name("notepad.exe")

    elif "закрой окно" in text or "закрой текущее окно" in text:
        close_active_window()

    elif "выйди из музыки" in text or "выключи музыку" in text:
        kill_process_by_name("yandexmusic.exe")


#open_process_by_name("yandexmusic:")
#kill_process_by_name("yandexmusic")
kill_process_by_name("Яндекс Музыка")