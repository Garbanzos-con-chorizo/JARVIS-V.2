import tkinter as tk
from tkinter import messagebox
from .core import JarvisCore

class JarvisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JARVIS Assistant")
        self.geometry("300x150")

        self.core = JarvisCore()

        self.start_button = tk.Button(self, text="Start", command=self.start_listening)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

    def start_listening(self):
        self.core.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_listening(self):
        self.core.stop_listening()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("JARVIS", "Assistant stopped.")
