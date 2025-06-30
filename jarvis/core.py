import os
import json
import speech_recognition as sr
import pyttsx3
import openai
from threading import Thread
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from jarvis_core import JarvisCore

__all__ = ["JarvisCore"]

class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(self, log_callback=None, loop: asyncio.AbstractEventLoop | None = None):
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
        
        # AsyncIO and ThreadPoolExecutor setup for parallel execution
        self.loop = loop or asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
        self.tasks: list[asyncio.Future] = []
        self.loop_thread = None

    @staticmethod
    def _load_config():
        """Load configuration from config.json if present."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _speak_blocking(self, text: str):
        """Blocking text-to-speech helper."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    async def _speak(self, text: str):
        """Speak text asynchronously."""
        await self.loop.run_in_executor(self.executor, self._speak_blocking, text)

    def listen(self):
        """Continuously listen for voice commands."""
        self.listening = True
        greeting = "How may I assist you?"
        if self.log_callback:
            self.log_callback(f"JARVIS: {greeting}")
        self._speak(greeting)
        
        while self.listening:
            try:
                # Async microphone listening
                with sr.Microphone() as source:
                    audio = await self.loop.run_in_executor(self.executor, self.recognizer.listen, source)
                
                command = await self.loop.run_in_executor(self.executor, self.recognizer.recognize_google, audio)
                await self._handle_command(command)
            
            except sr.UnknownValueError:
                await self._speak("I beg your pardon, sir, I did not catch that.")
            except Exception as exc:
                await self._speak(f"An error occurred: {exc}")
                self.listening = False

    def stop_listening(self):
        self.listening = False

    async def _handle_command(self, command: str):
        """Process a recognized voice command."""
        command = command.lower()
        if self.log_callback:
            self.log_callback(f"User: {command}")
        if "shutdown" in command:
            reply = "Shutting down. Goodbye, sir."
            if self.log_callback:
                self.log_callback(f"JARVIS: {reply}")
            await self._speak(reply)
            self.stop_listening()
        else:
            response = await self._chatgpt_response(command)
            if self.log_callback:
                self.log_callback(f"JARVIS: {response}")
            await self._speak(response)

    def start(self):
        """Start the voice listener as an asynchronous task."""
        self._ensure_loop_thread()
        task = asyncio.run_coroutine_threadsafe(self.listen(), self.loop)
        self.tasks.append(task)
        return task

    def _ensure_loop_thread(self):
        if not self.loop_thread:
            self.loop_thread = Thread(target=self.loop.run_forever, daemon=True)
            self.loop_thread.start()

    def stop(self):
        """Stop all running tasks."""
        self.stop_listening()
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        if self.loop_thread:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop_thread.join()
            self.loop_thread = None
        self.executor.shutdown(wait=False)

    async def _chatgpt_response(self, prompt: str) -> str:
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
                response = await self.loop.run_in_executor(
                    self.executor,
                    lambda: openai.ChatCompletion.create(
                        model=self.model, messages=self.conversation
                    ),
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
                await asyncio.sleep(1)
        
        self.conversation.append({"role": "assistant", "content": reply})
        return reply

