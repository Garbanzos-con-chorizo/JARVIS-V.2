import os
import sys
import json
import types
from io import StringIO
from urllib import request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QMessageBox

from jarvis.lab import LabModule


class FakeResponse(StringIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass



def test_update_environment(app, monkeypatch):
    module = LabModule(core=types.SimpleNamespace(_speak=lambda *a: None))

    data = {"temperature": 21.0, "humidity": 50, "pump": False, "gas_alert": False}
    resp = FakeResponse(json.dumps(data))
    monkeypatch.setattr(request, "urlopen", lambda *a, **k: resp)
    module._update_environment()
    assert module.temp_label.text() == "Temp: 21.0\u00B0C"
    assert module.humid_label.text() == "Humidity: 50%"
    assert module.pump_button.text() == "Pump OFF"


def test_toggle_pump(app, monkeypatch):
    module = LabModule(core=None)
    module._pump_state = False

    class Dummy:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    def fake_urlopen(req, timeout=1):
        assert "state=on" in req.full_url
        return Dummy()

    monkeypatch.setattr(request, "urlopen", fake_urlopen)
    module._toggle_pump()
    assert module._pump_state is True

