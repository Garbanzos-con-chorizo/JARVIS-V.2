from __future__ import annotations

import json
import os
from urllib import request
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)


LAB_SERVER_URL = os.environ.get("LAB_SERVER_URL", "http://localhost:8000")


class LabModule(QWidget):
    """Interface for monitoring lab environment via a remote Raspberry Pi."""

    def __init__(self, core, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.core = core
        self.setWindowTitle("Lab Module")

        layout = QVBoxLayout(self)
        self.temp_label = QLabel("Temp: --°C")
        layout.addWidget(self.temp_label)
        self.humid_label = QLabel("Humidity: --%")
        layout.addWidget(self.humid_label)
        self.pump_button = QPushButton("Toggle Pump")
        self.pump_button.clicked.connect(self._toggle_pump)
        layout.addWidget(self.pump_button)
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self._alert_shown = False
        self._pump_state = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_environment)

    def activate(self) -> None:
        """Display the module and begin polling the server."""
        self.show()
        self.timer.start(2000)
        if hasattr(self.core, "_speak"):
            try:
                self.core._speak("Lab module online, sir.")
            except Exception:
                pass

    def closeEvent(self, event) -> None:
        self.timer.stop()
        super().closeEvent(event)

    def _update_environment(self) -> None:
        """Fetch environment data from the Raspberry Pi server."""
        try:
            with request.urlopen(f"{LAB_SERVER_URL}/data", timeout=1) as resp:
                data = json.load(resp)
        except Exception as exc:
            self.status_label.setText(f"Error: {exc}")
            return

        self.temp_label.setText(f"Temp: {data.get('temperature', '--')}°C")
        self.humid_label.setText(f"Humidity: {data.get('humidity', '--')}%")
        self._pump_state = bool(data.get('pump', False))
        self.pump_button.setText(
            "Pump ON" if self._pump_state else "Pump OFF"
        )
        if data.get('gas_alert') and not self._alert_shown:
            QMessageBox.warning(
                self,
                "Gas Alert",
                "Hazardous gas levels detected!",
            )
            self._alert_shown = True
        elif not data.get('gas_alert'):
            self._alert_shown = False

    def _toggle_pump(self) -> None:
        new_state = not self._pump_state
        state_str = "on" if new_state else "off"
        try:
            req = request.Request(
                f"{LAB_SERVER_URL}/pump?state={state_str}",
                method="POST",
            )
            request.urlopen(req, timeout=1)
            self._pump_state = new_state
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Failed to toggle pump: {exc}")
