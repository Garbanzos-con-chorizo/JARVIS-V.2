"""High-level voice interface for the JARVIS assistant.

Example
-------
>>> from jarvis.core import JarvisCore
>>> core = JarvisCore()
>>> core.start()  # begins listening in a background thread
"""

import os
import json
import speech_recognition as sr
import pyttsx3
import openai
from threading import Thread
import time

from jarvis_core import JarvisCore

__all__ = ["JarvisCore"]

class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(self, log_callback=None):
        self.recognizer = sr.Recognizer()
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
        
        # Initialize text-to-speech (TTS)
        try:
            self.tts_engine = pyttsx3.init()
        except Exception as exc:
            self.tts_engine = None
            if self.log_callback:
                self.log_callback(f"TTS initialization error: {exc}")
        self.listening = False

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
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"TTS error: {exc}")
                print(text)
        else:
            print(text)

    def listen(self):
        """Continuously listen for voice commands."""
        self.listening = True
        greeting = "How may I assist you?"
        if self.log_callback:
            self.log_callback(f"JARVIS: {greeting}")
        self._speak(greeting)
        while self.listening:
            try:
                try:
                    with sr.Microphone() as source:
                        audio = self.recognizer.listen(source)
                except Exception as exc:
                    if self.log_callback:
                        self.log_callback(f"Microphone error: {exc}")
                    self._speak("I'm unable to access the microphone, sir.")
                    time.sleep(1)
                    continue
                try:
                    command = self.recognizer.recognize_google(audio)
                except Exception as exc:
                    if self.log_callback:
                        self.log_callback(f"Error recognizing speech: {exc}")
                    self._speak("I'm having trouble understanding you, sir.")
                    continue
                self._handle_command(command)
            except sr.UnknownValueError:
                self._speak("I beg your pardon, sir, I did not catch that.")
            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"Listening error: {exc}")
                self._speak("An unexpected error occurred, but I will continue assisting.")
                time.sleep(1)

    def stop_listening(self):
        self.listening = False

    def stop(self):
        """Stop the assistant via the public interface."""
        self.stop_listening()

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
            self.stop()
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

        if not openai.api_key:
            if self.log_callback:
                self.log_callback("OPENAI_API_KEY not configured.")
            reply = "Apologies, I'm currently unable to access my knowledge base."
            self.conversation.append({"role": "assistant", "content": reply})
            return reply
        
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model, messages=self.conversation
                )
                reply = response.choices[0].message["content"].strip()
                break
            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"ChatGPT error (attempt {attempt}): {exc}")
                if attempt == max_retries:
                    reply = (
                        "Apologies, I'm experiencing difficulties reaching my knowledge base."
                    )
                    break
                time.sleep(1)
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
