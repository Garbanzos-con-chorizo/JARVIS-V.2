import os
import time
import openai
from openai import APIConnectionError, APITimeoutError, RateLimitError, OpenAIError


class ChatGPTModule:
    """Handle ChatGPT API interactions with fallback behavior."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-3.5-turbo", log_callback=None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = model
        self.log_callback = log_callback
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, Tony Stark's AI assistant from the Iron Man films. "
                    "Respond politely using natural, conversational language."
                ),
            }
        ]

    def ask(self, prompt: str) -> str:
        """Send a prompt to ChatGPT and return the reply."""
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
            except RateLimitError as exc:
                if self.log_callback:
                    self.log_callback(
                        f"ChatGPT rate limit (attempt {attempt}): {exc}"
                    )
                if attempt == max_retries:
                    reply = "Sorry, the network is busy right now."
                    break
                time.sleep(2 * attempt)
            except (APIConnectionError, APITimeoutError) as exc:
                if self.log_callback:
                    self.log_callback(
                        f"ChatGPT network error (attempt {attempt}): {exc}"
                    )
                if attempt == max_retries:
                    reply = "Sorry, the network is busy right now."
                    break
                time.sleep(attempt)
            except OpenAIError as exc:
                if self.log_callback:
                    self.log_callback(f"ChatGPT error: {exc}")
                reply = (
                    "Apologies, I'm experiencing difficulties reaching my knowledge base."
                )
                break
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
