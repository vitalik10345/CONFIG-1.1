import pytest
import os
import configparser
import tarfile
import io
import tkinter as tk
from shell_emulator import ShellEmulator, VirtualFileSystem

from unittest.mock import MagicMock

# Мок-объект для output_area
class MockOutputArea:
    def __init__(self):
        self.content = ""

    def insert(self, index, text):
        self.content += text

    def get(self, start, end):
        return self.content

# Фикстура для VirtualFileSystem
@pytest.fixture
def virtual_fs():
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        # Добавляем директорию dir1
        info = tarfile.TarInfo(name='dir1/')
        info.type = tarfile.DIRTYPE
        tar.addfile(info)
        # Добавляем файл в dir1
        info = tarfile.TarInfo(name='dir1/file1.txt')
        info.size = len(b'Hello World')
        tar.addfile(info, io.BytesIO(b'Hello World'))
        # Добавляем файл в корне
        info = tarfile.TarInfo(name='file2.txt')
        info.size = len(b'Test File')
        tar.addfile(info, io.BytesIO(b'Test File'))
    tar_stream.seek(0)
    tar_path = 'test_fs.tar'
    with open(tar_path, 'wb') as f:
        f.write(tar_stream.read())
    fs = VirtualFileSystem(tar_path)
    print("Loaded Virtual File System Structure:", fs.root)  # Для отладки структуры
    yield fs
    os.remove(tar_path)

# Фикстура для ShellEmulator
@pytest.fixture
def shell_emulator():
    config_path = 'test_config.ini'
    config = configparser.ConfigParser()
    config['Settings'] = {
        'computer_name': 'my_computer',
        'vfs_path': 'test_fs.tar',
        'log_file': 'test_log.json',
        'startup_script': 'startup.sh'
    }
    with open(config_path, 'w') as f:
        config.write(f)
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        # Добавляем директорию dir1
        info = tarfile.TarInfo(name='dir1/')
        info.type = tarfile.DIRTYPE
        tar.addfile(info)
        # Добавляем файл в dir1
        info = tarfile.TarInfo(name='dir1/file1.txt')
        info.size = len(b'Hello World')
        tar.addfile(info, io.BytesIO(b'Hello World'))
        # Добавляем файл в корне
        info = tarfile.TarInfo(name='file2.txt')
        info.size = len(b'Test File')
        tar.addfile(info, io.BytesIO(b'Test File'))
    tar_stream.seek(0)
    tar_path = 'test_fs.tar'
    with open(tar_path, 'wb') as f:
        f.write(tar_stream.read())
    emulator = ShellEmulator(config_path)

    # Отключаем GUI для тестов и заменяем output_area на мок-объект
    emulator.setup_gui = lambda: None
    emulator.output_area = MockOutputArea()

    yield emulator
    os.remove(config_path)
    os.remove(tar_path)
    if os.path.exists('test_log.json'):
        os.remove('test_log.json')

# Тесты для VirtualFileSystem
def test_list_directory_root(virtual_fs):
    virtual_fs.current_path = '/'  # Устанавливаем начальный путь
    entries = virtual_fs.list_dir()  # Используем корректный метод
    entry_list = entries.split('  ')
    assert 'dir1' in entry_list
    assert 'file2.txt' in entry_list

def test_change_directory(virtual_fs):
    # Проверяем текущий путь
    assert virtual_fs.current_path == '/'
    # Переход в dir1
    success = virtual_fs.change_dir('dir1')
    assert success == ''  # Успешный переход
    assert virtual_fs.current_path == '/dir1'  # Проверяем текущий путь

# Тесты для ShellEmulator
def test_cd_command(shell_emulator):
    # Проверяем начальный путь
    assert shell_emulator.vfs.current_path == '/'
    # Выполняем команду cd dir1
    shell_emulator.process_command('cd dir1')
    # Проверяем, что путь обновился
    assert shell_emulator.vfs.current_path == '/dir1'

def test_ls_command(shell_emulator):
    shell_emulator.process_command('ls')  # Выполняем команду ls
    output = shell_emulator.output_area.get("1.0", tk.END).strip()
    # Разделяем вывод по пробелам
    entries = output.split()
    assert 'dir1' in entries
    assert 'file2.txt' in entries

def test_chown_command(shell_emulator):
    shell_emulator.process_command('chown newuser file2.txt')  # Используем process_command
    output = shell_emulator.output_area.get("1.0", tk.END).strip().split('\n')[-1]
    assert output == "Changed owner of file2.txt to newuser"
    file_info = shell_emulator.vfs._navigate_to('/file2.txt')
    assert file_info['owner'] == 'newuser'


def test_history_command(shell_emulator):
    shell_emulator.process_command('ls')
    shell_emulator.process_command('cd dir1')
    shell_emulator.process_command('history')
    output = shell_emulator.output_area.get("1.0", tk.END).strip()
    # История команд хранится в shell_emulator.history
    assert 'ls' in shell_emulator.history
    assert 'cd dir1' in shell_emulator.history
    assert 'history' in shell_emulator.history
