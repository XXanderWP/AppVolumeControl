import tkinter as tk
from tkinter import ttk
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from comtypes import CLSCTX_ALL
import keyboard
import os
import pygetwindow as gw
import win32gui
import win32process

current_volume_text = "Current volume"
set_volume_min_text = "Set min volume:"
set_volume_max_text = "Set max volume:"
default_hotkey = "ctrl+f2"

hotkey_prefix = {"ctrl","alt","shift"}
hotkeys_dict = {}

for prefix in hotkey_prefix:
    for i in range(1, 13):
        hotkeys_dict[f"{prefix}+f{i}"]=f"{prefix.capitalize()} + F{i}"


def get_window_title_by_pid(pid):
    def callback(hwnd, pid):
        try:
            # Получение PID окна
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            # Если PID совпадает, возвращаем заголовок окна
            if found_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                if title:
                    return title
        except Exception:
            pass
        return None

    def enum_windows_proc(hwnd, pid):
        title = callback(hwnd, pid)
        if title:
            titles.append(title)
        return True

    titles = []
    win32gui.EnumWindows(enum_windows_proc, pid)
    
    return titles

def get_window_title_by_process_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return get_window_title_by_pid(proc.info['pid'])
    return None
class VolumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Volume Control App")
        
        self.set_dark_theme(self.root)

        self.original_volume = None
        self.is_volume_toggled = False

        self.process_file = "process.txt"
        self.hotkey_file = "hotkey.txt"

        self.hotkey_value = self.load_hotkey_from_file() or default_hotkey

        self.hotkey_label = ttk.Label(root, text="Choose hotkey:")
        self.hotkey_label.pack(pady=5)

        self.hotkey_combo = ttk.Combobox(root, values=list(hotkeys_dict.values()), style="TCombobox")
        self.hotkey_combo.set(hotkeys_dict[self.hotkey_value])
        self.hotkey_combo.pack(pady=5)
        self.hotkey_combo.bind("<<ComboboxSelected>>", self.update_hotkey)

        # self.hotkey_current_label = ttk.Label(root, text=f"Current hotkey: {self.hotkey_value}")
        # self.hotkey_current_label.pack(pady=10)

        process = ttk.Frame(root)
        process.pack(pady=5)

        self.process_label = ttk.Label(process, text="Choose process")
        self.process_label.pack(side="left", pady=5)
        self.update_button = ttk.Button(process, text="Update", command=self.update_process_list)
        self.update_button.pack(side="right", padx=5)

        self.process_combo = ttk.Combobox(root, values=self.get_processes(), style="TCombobox")
        self.process_combo.pack(pady=5)
        self.process_combo.bind("<<ComboboxSelected>>", self.update_current_volume)

        self.current_volume_label = ttk.Label(root, text=f"{current_volume_text}: N/A")
        self.current_volume_label.pack_forget()

        self.volume_label_1 = ttk.Label(root, text=set_volume_min_text)
        self.volume_label_1.pack(pady=5)

        self.volume_slider_1 = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_label_1)
        self.volume_slider_1.pack(pady=5)

        self.volume_value_1 = ttk.Label(root, text="0%")
        self.volume_value_1.pack(pady=5)

        self.volume_label_2 = ttk.Label(root, text=set_volume_max_text)
        self.volume_label_2.pack(pady=5)

        self.volume_slider_2 = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_label_2)
        self.volume_slider_2.pack(pady=5)

        self.volume_value_2 = ttk.Label(root, text="100%")
        self.volume_value_2.pack(pady=5)

        keyboard.add_hotkey(self.hotkey_value, self.toggle_volume)
        self.load_process_from_file()

        self.contacts_button = ttk.Button(root, text="Contacts", command=lambda: self.open_contacts_window())
        self.contacts_button.pack(pady=10)

    def update_process_list(self):
        # Обновляем список процессов
        processes = self.get_processes()
        self.process_combo['values'] = processes

    def set_dark_theme(self, target):
        style = ttk.Style(target)
        target.configure(bg="#2e2e2e")
        
        style.theme_use('clam')

        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("TFrame", background="#2e2e2e", foreground="white")
        style.configure("TCombobox", background="#2e2e2e", foreground="white", fieldbackground="#1e1e1e")
        style.configure("TScale", background="#2e2e2e", troughcolor="#4a4a4a", sliderrelief="flat", sliderthickness=20)
        style.configure("TButton", background="#2e2e2e", foreground="white", relief="flat")
        style.map("TButton", background=[("active", "#4a4a4a")], relief=[("pressed", "sunken")])

    def get_processes(self):
        process_double: list[str] = []
        processes: list[str] = []
        for proc in psutil.process_iter(['pid', 'name']):
            if not proc.info['name'] in process_double:
                title = get_window_title_by_pid(proc.info['pid'])
                if len(title) > 0:
                    volume = self.get_current_volume(proc.info['name'])
                    if volume is not None:
                        process_double.append(proc.info['name'])
                        restitle = title[0]
                        processes.append(f"{proc.info['name']} || {restitle}")
        
        # Сортировка по имени процесса и заголовку окна
        processes = sorted(processes, key=lambda x: (x.split(" || ")[0].lower(), x.split(" || ")[1].lower()))
        return processes


    def save_process_to_file(self, process_name):
        with open(self.process_file, 'w') as f:
            f.write(process_name)

    def load_process_from_file(self):
        if os.path.isfile(self.process_file):
            with open(self.process_file, 'r') as f:
                process_name = f.read().strip()
                processes = self.get_processes()
                for q in processes:
                    if q.startswith(f"{process_name} || "):
                        self.process_combo.set(q)
                        self.update_current_volume(None, updateLabel=True)

    def save_hotkey_to_file(self, hotkey):
        with open(self.hotkey_file, 'w') as f:
            f.write(hotkey)

    def load_hotkey_from_file(self):
        if os.path.isfile(self.hotkey_file):
            with open(self.hotkey_file, 'r') as f:
                return f.read().strip()
        return None

    def update_hotkey(self, event=None):
        selected_name = self.hotkey_combo.get()

        for key, name in hotkeys_dict.items():
            if name == selected_name:
                print(f"Selected Key: {key}")
                keyboard.remove_hotkey(self.hotkey_value)
                
                self.hotkey_value = key
                keyboard.add_hotkey(self.hotkey_value, self.toggle_volume)
                
                # self.hotkey_current_label.config(text=f"Current hotkey: {self.hotkey_value}")
                self.save_hotkey_to_file(self.hotkey_value)
                break

        

    def set_volume(self, app_name, volume_level):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == app_name:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(volume_level / 100, None)
                return True
        return False

    def get_current_volume(self, app_name):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == app_name:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                return volume.GetMasterVolume() * 100
        return None

    def update_current_volume(self, event, updateLabel=True):
        app_name = self.process_combo.get().split(" || ")[0]
        current_volume = self.get_current_volume(app_name)

        if current_volume is not None:
            self.current_volume_label.config(text=f"{current_volume_text}: {int(current_volume)}%")
            if updateLabel:
                self.volume_slider_2.set(current_volume)
                self.volume_value_2.config(text=f"{int(current_volume)}%")
        else:
            self.current_volume_label.config(text=f"{current_volume_text}: N/A")

        if not self.is_volume_toggled:
            self.volume_value_2.config(foreground="red")
            self.volume_value_1.config(foreground="black")
        else:
            self.volume_value_1.config(foreground="red")
            self.volume_value_2.config(foreground="black")
        self.current_volume_label.pack()
        self.save_process_to_file(app_name)

    def update_label_1(self, value):
        self.volume_value_1.config(text=f"{int(float(value))}%")

    def update_label_2(self, value):
        self.volume_value_2.config(text=f"{int(float(value))}%")

    def toggle_volume(self):
        app_name = self.process_combo.get().split(" || ")[0]
        print(f"Toggle volume {app_name}")

        if app_name:
            if not self.is_volume_toggled:
                self.original_volume = self.get_current_volume(app_name)
                if self.original_volume is not None:
                    new_volume = self.volume_slider_1.get()
                    self.set_volume(app_name, new_volume)
                    self.is_volume_toggled = True
                    self.save_process_to_file(app_name)  # Save the selected process
            else:
                if self.original_volume is not None:
                    second_volume = self.volume_slider_2.get()
                    self.set_volume(app_name, second_volume)
                    self.is_volume_toggled = False
            self.update_current_volume(None, updateLabel=False)


    def open_contacts_window(self):
        contacts_window = tk.Toplevel(self.root)
        self.set_dark_theme(contacts_window)
        contacts_window.title("Contacts")
        contacts_window.minsize(300, 200)

        contacts_label = ttk.Label(contacts_window, text="This app was created in a few hours\nfor personal use.", justify="center")
        contacts_label.pack(pady=20)

        github_button = ttk.Button(contacts_window, text="Open Developer page", command=lambda: os.system("start https://xanderwp.site/"))
        github_button.pack(pady=10)
        github_button = ttk.Button(contacts_window, text="Open Project GitHub", command=lambda: os.system("start https://github.com/XXanderWP/AppVolumeControl"))
        github_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(280, 330)

    # root.resizable(False, False)
    app = VolumeApp(root)
    root.mainloop()
