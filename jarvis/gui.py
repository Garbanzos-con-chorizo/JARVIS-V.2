import tkinter as tk
from tkinter import messagebox, ttk
from jarvis_core import JarvisCore

class JarvisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JARVIS Assistant")
        self.geometry("500x400")
        self.configure(bg="black")

        self.log_text = None
        self.loading_frame = None
        self.main_frame = None

        self._show_loading()
        # Initialize core with callback
        self.core = JarvisCore(log_callback=self.log_message)

    def _show_loading(self):
        """Display a temporary loading screen."""
        self.loading_frame = tk.Frame(self, bg="black")
        self.loading_frame.pack(fill="both", expand=True)

        try:
            self.loading_img = tk.PhotoImage(file="jarvis/assets/loading.gif")
            tk.Label(self.loading_frame, image=self.loading_img, bg="black").pack(expand=True)
        except Exception:
            tk.Label(self.loading_frame, text="Loading...", fg="cyan", bg="black", font=("Arial", 18)).pack(expand=True)

        self.after(2000, self._init_main_screen)

    def _init_main_screen(self):
        """Create the main interactive interface."""
        if self.loading_frame:
            self.loading_frame.destroy()
        self.main_frame = tk.Frame(self, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        try:
            self.bg_img = tk.PhotoImage(file="jarvis/assets/background.gif")
            bg_label = tk.Label(self.main_frame, image=self.bg_img)
            bg_label.place(relwidth=1, relheight=1)
        except Exception:
            self.main_frame.configure(bg="black")

        self.log_text = tk.Text(self.main_frame, state=tk.DISABLED, bg="black", fg="cyan")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = tk.Frame(self.main_frame, bg="black")
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start", command=self.start_listening)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def log_message(self, message: str):
        """Append a message to the log view in a thread-safe way."""
        if not self.log_text:
            return

        def append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        # Ensure updates from background threads do not interfere with Tkinter
        self.after(0, append)

    def start_listening(self):
        """Start the JARVIS core."""
        self.core.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_listening(self):
        """Stop the JARVIS core."""
        self.core.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("JARVIS: Assistant stopped.")
        messagebox.showinfo("JARVIS", "Assistant stopped.")

    def start(self):
        """Run the GUI event loop."""
        self.mainloop()

    def stop(self):
        """Stop the assistant and close the window."""
        self.core.stop()
        self.destroy()
