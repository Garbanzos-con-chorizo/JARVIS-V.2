# JARVIS-V.2

A minimal voice assistant reminiscent of JARVIS from the Iron Man films. The project now integrates with OpenAI's ChatGPT API for more natural responses and features an enhanced Tkinter GUI.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

The assistant uses the default system microphone and speakers.

Configuration values such as `OPENAI_API_KEY` can be placed in `config.json` in the project root. The assistant will fall back to environment variables if the file is absent or keys are missing.

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
