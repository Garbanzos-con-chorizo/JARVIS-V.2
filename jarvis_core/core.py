import os
import json
import speech_recognition as sr
import pyttsx3
from threading import Thread
from typing import Callable, Optional
from vosk import Model, KaldiRecognizer

from .chatgpt import ChatGPTModule


class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None,
        speech_detected_callback: Optional[Callable[[], None]] = None,
        model_path: str | None = None,
    ):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.log_callback = log_callback
        self.speech_detected_callback = speech_detected_callback

        from jarvis.data import DataManager

        DataManager.init_db()

        self.chatgpt = ChatGPTModule(log_callback=log_callback)

        model_path = model_path or os.getenv("VOSK_MODEL_PATH", "model")
        if os.path.exists(model_path):
            try:
                self.vosk_model = Model(model_path)
            except Exception as exc:
                self.vosk_model = None
                if self.log_callback:
                    self.log_callback(f"Vosk model error: {exc}")
        else:
            self.vosk_model = None

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
                if self.speech_detected_callback:
                    self.speech_detected_callback()
                if self.vosk_model:
                    result_json = self.recognizer.recognize_vosk(audio)
                    try:
                        command = json.loads(result_json).get("text", "")
                    except Exception:
                        command = result_json
                else:
                    command = self.recognizer.recognize_google(audio)
                if command:
                    self._handle_command(command)
            except sr.UnknownValueError:
                self._speak("I beg your pardon, sir, I did not catch that.")
            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"Listening error: {exc}")
                self._speak(f"An error occurred: {exc}")
                self.listening = False

    def stop_listening(self):
        self.listening = False

    def _handle_command(self, command: str):
        """Process a recognized voice command."""
        command = command.lower()
        if self.log_callback:
            self.log_callback(f"User: {command}")
        from jarvis.data import DataManager

        DataManager.log_conversation("user", command)
        if "shutdown" in command:
            reply = "Shutting down. Goodbye, sir."
            if self.log_callback:
                self.log_callback(f"JARVIS: {reply}")
            DataManager.log_conversation("jarvis", reply)
            self._speak(reply)
            self.stop_listening()
        else:
            response = self._chatgpt_response(command)
            if self.log_callback:
                self.log_callback(f"JARVIS: {response}")
            DataManager.log_conversation("jarvis", response)
            self._speak(response)

    def start(self):
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        return thread

    def _chatgpt_response(self, prompt: str) -> str:
        """Query the ChatGPT module for a response."""
        return self.chatgpt.ask(prompt)
