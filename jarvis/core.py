import os
import json
import speech_recognition as sr
import pyttsx3
import openai
from threading import Thread

from jarvis_core import JarvisCore

__all__ = ["JarvisCore"]

class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(self, log_callback=None):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.log_callback = log_callback
        
        # Load configuration and set up OpenAI API key
        config = self._load_config()
        api_key = config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key
        
        # Model settings
        self.model = config.get("MODEL") or os.getenv("MODEL", "gpt-3.5-turbo")
        
        # Chat history (conversation context)
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, an advanced AI assistant. Respond in a polite,"
                    " concise manner."
                ),
            }
        ]

    @staticmethod
    def _load_config():
        """Load configuration from config.json if present."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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
        else:
            response = self._chatgpt_response(command)
            if self.log_callback:
                self.log_callback(f"JARVIS: {response}")
            self._speak(response)

    def start(self):
        """Start listening in a separate thread."""
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        return thread

    def _chatgpt_response(self, prompt: str) -> str:
        """Query the OpenAI ChatGPT API for a response."""
        self.conversation.append({"role": "user", "content": prompt})
        try:
            response = openai.ChatCompletion.create(
                model=self.model, messages=self.conversation
            )
            reply = response.choices[0].message["content"].strip()
        except Exception as exc:
            reply = f"I'm sorry, I encountered an error: {exc}"
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
