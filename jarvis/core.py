import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import speech_recognition as sr
import pyttsx3
import openai

class JarvisCore:
    """Core functionality for the JARVIS assistant with ChatGPT integration."""

    def __init__(self, log_callback=None, loop: asyncio.AbstractEventLoop | None = None):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.listening = False
        self.log_callback = log_callback
        self.loop = loop or asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
        self.tasks: list[asyncio.Future] = []
        self.loop_thread = None
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, an advanced AI assistant. Respond in a polite,"
                    " concise manner."
                ),
            }
        ]

    def _speak_blocking(self, text: str):
        """Blocking text-to-speech helper."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    async def _speak(self, text: str):
        """Speak text asynchronously."""
        await self.loop.run_in_executor(self.executor, self._speak_blocking, text)

    async def listen(self):
        """Continuously listen for voice commands."""
        self.listening = True
        greeting = "How may I assist you?"
        if self.log_callback:
            self.log_callback(f"JARVIS: {greeting}")
        await self._speak(greeting)
        while self.listening:
            try:
                with sr.Microphone() as source:
                    audio = await self.loop.run_in_executor(
                        self.executor, self.recognizer.listen, source
                    )
                command = await self.loop.run_in_executor(
                    self.executor, self.recognizer.recognize_google, audio
                )
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

    def _ensure_loop_thread(self):
        if not self.loop_thread:
            self.loop_thread = Thread(target=self.loop.run_forever, daemon=True)
            self.loop_thread.start()

    def start(self):
        """Start the voice listener as an asynchronous task."""
        self._ensure_loop_thread()
        task = asyncio.run_coroutine_threadsafe(self.listen(), self.loop)
        self.tasks.append(task)
        return task

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
        try:
            response = await self.loop.run_in_executor(
                self.executor,
                lambda: openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=self.conversation
                ),
            )
            reply = response.choices[0].message["content"].strip()
        except Exception as exc:
            reply = f"I'm sorry, I encountered an error: {exc}"
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
