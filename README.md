# JARVIS-V.2

A minimal voice assistant reminiscent of JARVIS from the Iron Man films. The project now integrates with OpenAI's ChatGPT API for more natural responses and features an enhanced Tkinter GUI.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

The assistant uses the default system microphone and speakers.

Set the `OPENAI_API_KEY` environment variable with your OpenAI API key to enable ChatGPT responses.

Optionally place `loading.gif` and `background.gif` in `jarvis/assets/` to customize the loading screen and animated background. If these files are not present the GUI falls back to simple colors.

## Usage

Run the main application:

```bash
python main.py
```

Click **Start** to begin listening. Say "shutdown" to stop the assistant.
The GUI now includes a loading screen, animated background and a live log of the conversation.

## License

This project is licensed under the MIT License.
