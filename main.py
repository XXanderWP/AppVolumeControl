import tkinter as tk
from tkinter import ttk
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from comtypes import CLSCTX_ALL
import keyboard
import os

current_volume_text = "Current volume"
set_volume_min_text = "Set min volume:"
set_volume_max_text = "Set max volume:"

class VolumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Volume Control App")

        self.original_volume = None
        self.is_volume_toggled = False

        self.process_file = "process.txt"

        self.process_label = ttk.Label(root, text="Choose process:")
        self.process_label.pack()

        self.process_combo = ttk.Combobox(root, values=self.get_processes())
        self.process_combo.pack()
        self.process_combo.bind("<<ComboboxSelected>>", self.update_current_volume)

        self.current_volume_label = ttk.Label(root, text=f"{current_volume_text}: N/A")
        self.current_volume_label.pack_forget()

        self.volume_label_1 = ttk.Label(root, text=set_volume_min_text)
        self.volume_label_1.pack()

        self.volume_slider_1 = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_label_1)
        self.volume_slider_1.pack()

        self.volume_value_1 = ttk.Label(root, text="0%")
        self.volume_value_1.pack()

        self.volume_label_2 = ttk.Label(root, text=set_volume_max_text)
        self.volume_label_2.pack()

        self.volume_slider_2 = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_label_2)
        self.volume_slider_2.pack()

        self.volume_value_2 = ttk.Label(root, text="100%")
        self.volume_value_2.pack()

        keyboard.add_hotkey('ctrl+f2', self.toggle_volume)
        self.load_process_from_file()

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(proc.info['name'])
        return processes

    def save_process_to_file(self, process_name):
        with open(self.process_file, 'w') as f:
            f.write(process_name)

    def load_process_from_file(self):
        if os.path.isfile(self.process_file):
            with open(self.process_file, 'r') as f:
                process_name = f.read().strip()
                if process_name in self.get_processes():
                    self.process_combo.set(process_name)
                    self.update_current_volume(None, updateLabel=True)

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
        app_name = self.process_combo.get()
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
        app_name = self.process_combo.get()

        if app_name:
            if not self.is_volume_toggled:
                self.original_volume = self.get_current_volume(app_name)
                if self.original_volume is not None:
                    new_volume = self.volume_slider_1.get()
                    self.set_volume(app_name, new_volume)
                    self.is_volume_toggled = True
                    self.save_process_to_file(app_name)  # Сохранение выбранного процесса
            else:
                if self.original_volume is not None:
                    second_volume = self.volume_slider_2.get()
                    self.set_volume(app_name, second_volume)
                    self.is_volume_toggled = False
            self.update_current_volume(None, updateLabel=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeApp(root)
    root.mainloop()
