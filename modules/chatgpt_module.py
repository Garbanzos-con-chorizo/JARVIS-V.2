import os
import openai

class ChatGPTModule:
    """Simple wrapper around the OpenAI API."""

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, an advanced AI assistant. Respond in a polite,"\
                    " concise manner."
                ),
            }
        ]

    def respond(self, prompt: str) -> str:
        self.conversation.append({"role": "user", "content": prompt})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=self.conversation
            )
            reply = response.choices[0].message["content"].strip()
        except Exception as exc:
            reply = f"I'm sorry, I encountered an error: {exc}"
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
