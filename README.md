# JARVIS-V.2

A minimal voice assistant reminiscent of JARVIS from the Iron Man films. The project now integrates with OpenAI's ChatGPT API for more natural responses and features a PyQt5 GUI.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

PyQt5 provides the graphical interface. On some Linux distributions you may need
to install system Qt packages before installing the Python dependencies.

### Windows Setup

An automatic PowerShell script is provided for Windows users. Run it from a
PowerShell prompt to create a virtual environment and install all
dependencies:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
./install_windows.ps1
```

Use the optional `-InstallPython` flag if Python 3 is not already installed.

The assistant uses the default system microphone and speakers.

Configuration values such as `OPENAI_API_KEY` can be placed in `config.json` in the project root. The assistant will fall back to environment variables if the file is absent or keys are missing.
The `ChatGPTModule` wraps all OpenAI API calls and retries automatically on errors. Should the API be unreachable or the key missing, the assistant replies with a short apology instead of crashing.

Optionally place `loading.gif` and `background.gif` in `jarvis/assets/` to customize the loading screen and animated background. If these files are not present the GUI falls back to simple colors.

### Offline Speech Recognition

The assistant uses the [Vosk](https://alphacephei.com/vosk/) library for offline speech recognition. Download a model and unpack it into a folder named `model` in the project root. Set `VOSK_MODEL_PATH` to point elsewhere if needed. When the model is missing the assistant falls back to the online Google recognizer.

## Usage

Run the main application:

```bash
python main.py
```

Click **Start** to begin listening. Say "shutdown" to stop the assistant.
The GUI now includes a loading screen, animated background and a live log of the conversation.

### Lab Module

The **Lab** button in the GUI opens a module that connects to a Raspberry Pi for
environment readings. Run `raspi_lab_server.py` on the Pi to expose sensor data
over HTTP. The server is headless and simply responds to requests for data or
pump toggles. The module displays temperature, humidity and pump status, and
warns if the Pi reports hazardous gas levels. Set the `LAB_SERVER_URL`
environment variable on the GUI machine if the server is not on
`localhost:8000`.



### Mobile App Prototype

A small Kivy client in `mobile_app/` allows remote control of JARVIS. Start the companion Flask server with:

```bash
python -m jarvis.server
```

Run the mobile app to send commands or to start and stop listening remotely.

### Data Logging

`jarvis/data.py` provides the `DataManager` used to log conversation history
and lab readings to an SQLite database named `jarvis.db`. Helper methods such
as `average_temperature()` summarise logged data for future display or
analysis.


## Security

API keys in `config.json` are encrypted using the Fernet symmetric algorithm. Generate a key and set it in the `CONFIG_SECRET` environment variable:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Encrypt your OpenAI key with this secret and place the resulting token in `config.json` prefixed with `enc:`:

```bash
python - <<EOF
from cryptography.fernet import Fernet
import os
secret=os.environ['CONFIG_SECRET'].encode()
print(Fernet(secret).encrypt(b'YOUR_OPENAI_KEY').decode())
EOF
```

Set `PASSWORD` in `config.json` or the `JARVIS_PASSWORD` environment variable to require verification before shutdown.


## License

This project is licensed under the MIT License.
