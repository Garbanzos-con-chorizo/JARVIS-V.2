import speech_recognition as sr
import pyttsx3
from threading import Thread

class JarvisCore:
    """Core functionality for the JARVIS assistant."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.listening = False

    def _speak(self, text: str):
        """Speak text using text-to-speech."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        """Continuously listen for voice commands."""
        self.listening = True
        self._speak("How may I assist you?")
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
        if "shutdown" in command:
            self._speak("Shutting down. Goodbye, sir.")
            self.stop_listening()
        else:
            self._speak(f"You said: {command}")

    def start(self):
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        return thread
