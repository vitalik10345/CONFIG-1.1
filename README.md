# Эмулятор оболочки ОС

## Библиотеки, не входящие в стандартную библиотеку Python

- **pytest**: Используется для написания и выполнения тестов.
- **tkinter**: Библиотека для создания графического пользовательского интерфейса (GUI).
- **shlex**: Модуль для разбиения строк команд в соответствии с синтаксисом оболочки.

---

## 1. Общее описание

Данный проект представляет собой **эмулятор языка оболочки операционной системы**, стремящийся максимально имитировать сеанс работы shell в UNIX-подобной ОС. Эмулятор запускается из реальной командной строки и предоставляет графический интерфейс (GUI) для взаимодействия с пользователем. Виртуальная файловая система загружается из tar-архива без необходимости его распаковки пользователем.

**Особенности:**
- Поддержка основных команд оболочки: `ls`, `cd`, `exit`.
- Дополнительные команды: `chown`, `history`.
- Виртуальная файловая система загружается из tar-архива без распаковки.
- Графический интерфейс для взаимодействия с пользователем.
- Логирование всех действий пользователя с сохранением в формате JSON.
- Стартовый скрипт для выполнения набора команд при запуске эмулятора.
- Полное покрытие функционала тестами с использованием `pytest`.

---

## 2. Описание всех функций и настроек

### Основные компоненты

- **`shell_emulator.py`**: Главный скрипт эмулятора, реализующий весь функционал.
- **`test_shell_emulator.py`**: Скрипт с тестами для проверки функциональности эмулятора.
- **`config.ini`**: Конфигурационный файл в формате INI.
- **`log.json`**: Лог-файл в формате JSON, содержащий записи всех действий пользователя.
- **`startup.sh`**: Стартовый скрипт для начального выполнения команд при запуске эмулятора.

---

### Классы и методы

#### Класс `VirtualFileSystem`

#### Управляет виртуальной файловой системой, загруженной из tar-архива. 
  ```python
  def __init__(self, tar_path):
      self.root = {'type': 'dir', 'contents': {}, 'owner': 'root'}
      self.current_path = '/'
      self.load_tar(tar_path)
  ```
  Описание: Инициализирует виртуальную файловую систему и загружает содержимое из указанного tar-архива.
#### Загрузка виртуальных файлов в систему

```python
def load_tar(self, tar_path):
    with tarfile.open(tar_path, 'r') as tar:
        for member in tar.getmembers():
            self._add_member(member)

```
Описание: Загружает виртуальную файловую систему из tar-архива без необходимости распаковки его пользователем. Открывает tar-архив и обрабатывает каждый его член (файл или каталог), добавляя его в структуру виртуальной файловой системы.

#### Добавляет файлы и директории из tar-архива

```python
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

```
Описание: Добавляет файлы и директории из tar-архива в виртуальную файловую систему. Разбирает путь каждого члена tar-архива, создавая необходимые каталоги и файлы в структуре `self.root`.

#### Возвращает содержимое католога

```python
def list_dir(self):
    dir_contents = self._navigate_to(self.current_path)['contents']
    return '  '.join(dir_contents.keys())

```
Описание: Возвращает содержимое текущего каталога в виде строки с именами файлов и папок, разделенными пробелами.

#### Изменяет владельца
```python
def chown(self, path, owner):
    target = self._navigate_to(posixpath.join(self.current_path, path))
    if target:
        target['owner'] = owner
        return f"Changed owner of {path} to {owner}"
    else:
        return f"No such file or directory: {path}"
```
Описание: Изменяет владельца указанного файла или каталога. Обновляет поле owner в структуре виртуальной файловой системы.
#### Параметры:
- `path` (str): Путь к файлу или каталогу.
- `owner` (str): Имя нового владельца.

#### Переходит у указанному пути в файловой системе

```python
def _navigate_to(self, path):
    path_parts = path.strip('/').split('/') if path.strip('/') else []
    current = self.root
    for part in path_parts:
        if part in current['contents']:
            current = current['contents'][part]
        else:
            return None
    return current
```
Описание: Возвращает объект каталога или файла, если путь существует, иначе `None`.

#### Класс `Shell_Emulator`
Описание: Управляет взаимодействием с пользователем через GUI и обрабатывает команды. Отвечает за инициализацию эмулятора, обработку пользовательского ввода, выполнение команд и логирование действий.

#### Инициализирует эмулятор

```python
def __init__(self, config_path):
    self.load_config(config_path)
    self.vfs = VirtualFileSystem(self.vfs_path)
    self.history = []
    self.log_data = []
    self.running = True
    self.setup_gui()
    self.run_startup_script()

```
Описание: Загружает конфигурацию и устанавливает GUI.

#### Загружает настройки 
```python
def load_config(self, config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    self.computer_name = config.get('Settings', 'computer_name')
    self.vfs_path = config.get('Settings', 'vfs_path')
    self.log_file = config.get('Settings', 'log_file')
    self.startup_script = config.get('Settings', 'startup_script')

```
Описание: Загружает настройки из конфигурационного файла `test_config.ini`. Извлекает имя компьютера, путь к виртуальной файловой системе, путь к лог-файлу и путь к стартовому скрипту.

#### Настройка графического интерфейса
```python
def setup_gui(self):
    self.root = tk.Tk()
    self.root.title('Shell Emulator')
    self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
    self.output_area.pack(expand=True, fill='both')
    self.input_entry = tk.Entry(self.root)
    self.input_entry.pack(fill='x')
    self.input_entry.bind('<Return>', self.handle_command)
    self.update_prompt()

```
Описание: Настраивает графический интерфейс пользователя с областью вывода команд и полем ввода для пользовательских команд. Привязывает обработчик нажатия клавиши Enter для выполнения команд.

#### Обновляет ввод команд 
```python
def update_prompt(self):
    self.output_area.insert(tk.END, f"{self.computer_name}:{self.vfs.current_path}$ ")
    self.output_area.see(tk.END)

```
Описание: Обновляет приглашение к вводу команды в GUI, отображая имя компьютера и текущий путь.

#### Обрабатывает введенные пользователем команды
```python
def handle_command(self, event):
    command = self.input_entry.get()
    self.input_entry.delete(0, tk.END)
    self.output_area.insert(tk.END, command + '\n')
    self.process_command(command)
    if self.running:
        self.update_prompt()
    else:
        self.root.quit()

```
Описание: Считывает команду из поля ввода, отображает ее в области вывода, выполняет команду и обновляет приглашение. Если команда `exit` была введена, закрывает GUI.

#### Обработка команд
```python
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

```
Описание: Выполняет соответствующие действия в зависимости от введенной команды и выводит результат в интерфейс. Также сохраняет команду в истории и лог-файле.

#### команды из стартового скрипта
```python
def run_startup_script(self):
    if os.path.exists(self.startup_script):
        with open(self.startup_script, 'r') as f:
            for line in f:
                command = line.strip()
                if command:
                    self.output_area.insert(tk.END, f"{self.computer_name}:{self.vfs.current_path}$ {command}\n")
                    self.process_command(command)
    self.update_prompt()

```
Описание: Выполняет команды из стартового скрипта при запуске эмулятора. Считывает каждую строку из файла `startup.sh` и выполняет ее как команду оболочки.

#### Сохраняет действия
```python
def save_log(self):
    with open(self.log_file, 'w') as f:
        json.dump(self.log_data, f, indent=4)

```
Описание: Сохраняет все действия пользователя в лог-файл `log.json` в формате JSON. Записывает историю команд и другие действия в указанный файл.

#### Запускает цикл
```python
def run(self):
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.root.mainloop()

```
Описание: Запускает главный цикл GUI, обрабатывая события пользовательского интерфейса. Устанавливает обработчик закрытия окна.

#### Закрывает окна
```python
def on_closing(self):
    self.running = False
    self.save_log()
    self.root.destroy()

```
Описание: Обрабатывает закрытие окна GUI, сохраняя лог перед выходом из приложения.

---


## 3. Команды
### Основные команды

#### Команда `ls`
```python
def list_dir(self):
    dir_contents = self._navigate_to(self.current_path)['contents']
    return '  '.join(dir_contents.keys())

```
Описание: Отображает содержимое текущего каталога. Возвращает имена файлов и папок, разделенные пробелами.

#### Команда `cd`
```python
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

```
Описание: Изменяет текущий каталог на указанный. Проверяет существование каталога и его тип. Если каталог существует и является директорией, обновляет текущий путь.

### Команда `exit`
```python
def process_command(self, command):
    # ...
    elif cmd == 'exit':
        self.running = False
        output = ''
    # ...

```
Описание: Завершает сеанс работы эмулятора. Устанавливает флаг `self.running` в `False` и закрывает GUI.

---

###  Дополнительные команды

#### Команда `chown`

```python
def chown(self, path, owner):
    target = self._navigate_to(posixpath.join(self.current_path, path))
    if target:
        target['owner'] = owner
        return f"Changed owner of {path} to {owner}"
    else:
        return f"No such file or directory: {path}"

```
Описание: Эмулирует изменение владельца указанного файла или каталога. Обновляет поле `owner` в структуре виртуальной файловой системы для указанного объекта.

#### Команда `history`

```python
def process_command(self, command):
    # ...
    elif cmd == 'history':
        output = '\n'.join(self.history)
    # ...

```
Описание: Отображает историю всех введенных команд за текущий сеанс работы. Выводит список команд, которые были введены пользователем в ходе текущего использования эмулятора.


---

### 4. Настрйоки

#### Файл test_config.ini

```ini
[Settings]
computer_name = my_computer
vfs_path = virtual_fs.tar
log_file = log.json
startup_script = startup.sh

```
- `computer_name`: Имя компьютера, отображаемое в приглашении к вводу. Используется для формирования строки приглашения, например, `my_computer:/$`
- `vfs_path`: Путь к архиву виртуальной файловой системы в формате tar. Эмулятор загружает файловую систему из этого архива при запуске.
- `log_file`: Путь к JSON-файлу, где записываются действия пользователя. Лог-файл сохраняет историю команд и другие действия в формате JSON.
- `startup_script`: Путь к стартовому скрипту для выполнения начального набора команд. Позволяет автоматически выполнять команды при запуске эмулятора, например, для настройки среды или предварительного перехода в определенный каталог.

#### Файл `startup.sh`:
```startup.sh
echo "Welcome to the Shell Emulator!"
ls
```

## 5. Примеры использования

### Запуск эмулятора:

```python
python shell_emulator.py test_config.ini

```
### Использование команд
#### 1. Использование команды `ls`:
![image](https://github.com/user-attachments/assets/d94918d1-8a07-4b97-a033-961186566ea5)

#### 2. Использование команды `cd`:
![image](https://github.com/user-attachments/assets/b13525cf-6927-4c23-b1f9-814ad561f9d2)

#### 3. Использование команды `chown`:
![image](https://github.com/user-attachments/assets/8f4cf62b-9078-4f9d-bc6e-a4a9123e2a23)

#### 4. Использование команды `history`:
![image](https://github.com/user-attachments/assets/c6fa8f03-bbfd-43f7-a2fb-f88ba60c6f9d)






## 6. Результаты тестирования

### Запуск тестов:

```python
python -m pytest test_shell_emulator.py

```
![image](https://github.com/user-attachments/assets/6e5907de-66b1-41aa-b71a-89095fb973a8)

Покрытие тестов:
- **Тесты для `VirtualFileSystem`**:

- `test_list_directory_root`: Проверяет корректность вывода команды `ls` в корневом каталоге.
- `test_change_directory`: Проверяет переход в существующий каталог и обновление текущего пути.
- **Тесты для `ShellEmulator`**:

- `test_cd_command`: Проверяет выполнение команды `cd` и изменение текущего пути.
- `test_ls_command`: Проверяет выполнение команды `ls` и правильность отображения содержимого каталога.
- `test_chown_command`: Проверяет выполнение команды `chown` и изменение владельца файла.
- `test_history_command`: Проверяет выполнение команды `history` и корректное отображение истории команд.





























