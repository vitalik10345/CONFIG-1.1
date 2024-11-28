import posixpath
import os
import sys
import tarfile
import configparser
import json
import tkinter as tk
from tkinter import scrolledtext

import shlex

class VirtualFileSystem:
    def __init__(self, tar_path):
        self.root = {'type': 'dir', 'contents': {}, 'owner': 'root'}
        self.current_path = '/'
        self.load_tar(tar_path)

    def load_tar(self, tar_path):
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                self._add_member(member)

    def _add_member(self, member):
        path_parts = member.name.strip('/').split('/')
        current = self.root
        for part in path_parts[:-1]:
            current = current['contents'].setdefault(part, {'type': 'dir', 'contents': {}, 'owner': 'root'})
        name = path_parts[-1]
        if member.isdir():
            current['contents'][name] = {'type': 'dir', 'contents': {}, 'owner': 'root'}
        else:
            current['contents'][name] = {'type': 'file', 'owner': 'root'}

    def list_dir(self):
        dir_contents = self._navigate_to(self.current_path)['contents']
        return '  '.join(dir_contents.keys())

    def change_dir(self, path):
        new_path = posixpath.normpath(posixpath.join(self.current_path, path))
        if not new_path.startswith('/'):
            new_path = '/' + new_path
        target = self._navigate_to(new_path)
        if target and target['type'] == 'dir':
            self.current_path = new_path
            return ''
        elif not target:
            return f"No such directory: {path}"
        else:
            return f"Not a directory: {path}"

    def chown(self, path, owner):
        target = self._navigate_to(posixpath.join(self.current_path, path))
        if target:
            target['owner'] = owner
            return f"Changed owner of {path} to {owner}"
        else:
            return f"No such file or directory: {path}"

    def _navigate_to(self, path):
        path_parts = path.strip('/').split('/') if path.strip('/') else []
        current = self.root
        for part in path_parts:
            if part in current['contents']:
                current = current['contents'][part]
            else:
                return None
        return current

class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.vfs = VirtualFileSystem(self.vfs_path)
        self.history = []
        self.log_data = []
        self.running = True
        self.setup_gui()
        self.run_startup_script()

    def load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.computer_name = config.get('Settings', 'computer_name')
        self.vfs_path = config.get('Settings', 'vfs_path')
        self.log_file = config.get('Settings', 'log_file')
        self.startup_script = config.get('Settings', 'startup_script')

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title('Shell Emulator')
        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
        self.output_area.pack(expand=True, fill='both')
        self.input_entry = tk.Entry(self.root)
        self.input_entry.pack(fill='x')
        self.input_entry.bind('<Return>', self.handle_command)
        self.update_prompt()

    def update_prompt(self):
        self.output_area.insert(tk.END, f"{self.computer_name}:{self.vfs.current_path}$ ")
        self.output_area.see(tk.END)

    def handle_command(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.output_area.insert(tk.END, command + '\n')
        self.process_command(command)
        if self.running:
            self.update_prompt()
        else:
            self.root.quit()

    def process_command(self, command):
        self.history.append(command)
        self.log_data.append({'command': command})
        tokens = shlex.split(command)
        if not tokens:
            return
        cmd = tokens[0]
        args = tokens[1:]
        if cmd == 'ls':
            output = self.vfs.list_dir()
        elif cmd == 'cd':
            output = self.vfs.change_dir(args[0] if args else '/')
        elif cmd == 'chown':
            if len(args) >= 2:
                output = self.vfs.chown(args[1], args[0])
            else:
                output = "Usage: chown owner file"
        elif cmd == 'history':
            output = '\n'.join(self.history)
        elif cmd == 'exit':
            self.running = False
            output = ''
        else:
            output = f"{cmd}: command not found"
        self.output_area.insert(tk.END, output + '\n')

    def run_startup_script(self):
        if os.path.exists(self.startup_script):
            with open(self.startup_script, 'r') as f:
                for line in f:
                    command = line.strip()
                    if command:
                        self.output_area.insert(tk.END, f"{self.computer_name}:{self.vfs.current_path}$ {command}\n")
                        self.process_command(command)
        self.update_prompt()

    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log_data, f, indent=4)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.running = False
        self.save_log()
        self.root.destroy()

# Точка входа
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python shell_emulator.py <test_config.ini>")
        sys.exit(1)
    emulator = ShellEmulator(sys.argv[1])
    emulator.run()
    emulator.save_log()
