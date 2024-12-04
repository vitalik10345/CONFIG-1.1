import subprocess
import sys

# Функция для установки пакетов через pip
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Функция для проверки и установки библиотеки
def check_and_install(package, lib_name):
    try:
        __import__(lib_name)
        print(f"У вас есть библиотека: {lib_name}")
    except ImportError:
        print(f"{lib_name} не найден, устанавливаю...")
        install(package)

# Проверяем и устанавливаем библиотеки

# Для pytest
check_and_install('pytest', 'pytest')

# Для tkinter
# tkinter является стандартной библиотекой, но для некоторых систем её могут нужно установить
try:
    import tkinter
    print("У вас есть библиотека: tkinter")
except ImportError:
    print("tkinter не найден, устанавливаю...")
    install("tkinter")

# Для shlex
try:
    import shlex
    print("У вас есть библиотека: shlex")
except ImportError:
    print("shlex не найден, устанавливаю...")
    install("shlex")
