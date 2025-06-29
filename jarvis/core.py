import os
import speech_recognition as sr
import pyttsx3
from threading import Thread

from modules.chatgpt_module import ChatGPTModule
from modules.lab_module import LabModule

class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(self, log_callback=None):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.log_callback = log_callback

        self.modules = {}
        self._load_modules()

    def _load_modules(self):
        """Instantiate available modules."""
        self.modules["chatgpt"] = ChatGPTModule()
        self.modules["lab"] = LabModule()

    def call_module(self, name: str, *args, **kwargs):
        """Call a method on a loaded module."""
        module = self.modules.get(name)
        if not module:
            raise ValueError(f"Module {name} not loaded")
        if hasattr(module, "respond"):
            return module.respond(*args, **kwargs)
        if hasattr(module, "get_temperature"):
            return module.get_temperature(*args, **kwargs)
        raise AttributeError(f"Module {name} has no supported interface")

    def _speak(self, text: str):
        """Speak text using text-to-speech."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        """Continuously listen for voice commands."""
        self.listening = True
        greeting = "How may I assist you?"
        if self.log_callback:
            self.log_callback(f"JARVIS: {greeting}")
        self._speak(greeting)
        while self.listening:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source)
                command = self.recognizer.recognize_google(audio)
                self._handle_command(command)
            except sr.UnknownValueError:
                self._speak("I beg your pardon, sir, I did not catch that.")
            except Exception as exc:
                self._speak(f"An error occurred: {exc}")
                self.listening = False

    def stop_listening(self):
        self.listening = False

    def _handle_command(self, command: str):
        """Process a recognized voice command."""
        command = command.lower()
        if self.log_callback:
            self.log_callback(f"User: {command}")
        if "shutdown" in command:
            reply = "Shutting down. Goodbye, sir."
            if self.log_callback:
                self.log_callback(f"JARVIS: {reply}")
            self._speak(reply)
            self.stop_listening()
        elif "temperature" in command:
            temp = self.call_module("lab")
            response = f"The current temperature is {temp} degrees Celsius."
            if self.log_callback:
                self.log_callback(f"JARVIS: {response}")
            self._speak(response)
        else:
            response = self._chatgpt_response(command)
            if self.log_callback:
                self.log_callback(f"JARVIS: {response}")
            self._speak(response)

    def start(self):
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        return thread

    def _chatgpt_response(self, prompt: str) -> str:
        """Query the ChatGPT module for a response."""
        try:
            return self.call_module("chatgpt", prompt)
        except Exception as exc:
            return f"I'm sorry, I encountered an error: {exc}"
