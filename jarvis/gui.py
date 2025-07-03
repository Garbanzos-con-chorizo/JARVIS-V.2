from __future__ import annotations

import os
from PyQt5.QtCore import Qt, QTimer, QObject, QEvent
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jarvis_core import JarvisCore
from .lab import LabModule


class JarvisGUI(QMainWindow):
    """PyQt5 interface for the JARVIS assistant."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("JARVIS Assistant")
        self.resize(500, 400)

        self.log_text: QTextEdit | None = None
        self.loading_label: QLabel | None = None
        self.background_movie: QMovie | None = None
        self.bg_label: QLabel | None = None
        self.central: QWidget | None = None

        self._show_loading()
        self.core = JarvisCore(
            log_callback=self.log_message, speech_detected_callback=self.indicate_speech
        )
        self.lab_module: LabModule | None = None

    # --------------------------- UI Helpers ---------------------------
    def _show_loading(self) -> None:
        """Display a temporary loading screen."""
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        movie_path = os.path.join("jarvis", "assets", "loading.gif")
        if os.path.exists(movie_path):
            movie = QMovie(movie_path)
            self.loading_label.setMovie(movie)
            movie.start()
        else:
            self.loading_label.setText("Loading...")
            self.loading_label.setStyleSheet("color: cyan;")
        self.setCentralWidget(self.loading_label)
        QTimer.singleShot(2000, self._init_main_screen)

    def _init_main_screen(self) -> None:
        """Create the main interactive interface."""
        if self.loading_label:
            self.loading_label.deleteLater()
            self.loading_label = None

        self.central = QWidget()
        layout = QVBoxLayout(self.central)
        self.setCentralWidget(self.central)

        # Background animation
        bg_path = os.path.join("jarvis", "assets", "background.gif")
        if os.path.exists(bg_path):
            self.background_movie = QMovie(bg_path)
            self.bg_label = QLabel(self.central)
            self.bg_label.setMovie(self.background_movie)
            self.bg_label.setScaledContents(True)
            self.background_movie.start()
            self.bg_label.setGeometry(self.rect())
            self.bg_label.lower()
            self.central.installEventFilter(self)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: black; color: cyan;")
        layout.addWidget(self.log_text)

        # Control buttons
        controls = QHBoxLayout()
        layout.addLayout(controls)
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_listening)
        controls.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_listening)
        controls.addWidget(self.stop_button)
        self.lab_button = QPushButton("Lab")
        self.lab_button.clicked.connect(self.open_lab)
        controls.addWidget(self.lab_button)

    # --------------------------- Event Filter ---------------------------
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if source is self.central and self.bg_label and event.type() == event.Resize:
            self.bg_label.setGeometry(self.central.rect())
        return super().eventFilter(source, event)

    # --------------------------- Public API ---------------------------
    def log_message(self, message: str) -> None:
        """Append a message to the log view in a thread-safe manner."""
        if not self.log_text:
            return

        def append() -> None:
            self.log_text.append(message)

        QTimer.singleShot(0, append)

    def start_listening(self) -> None:
        """Start the JARVIS core."""
        self.core.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_listening(self) -> None:
        """Stop the JARVIS core."""
        self.core.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_message("JARVIS: Assistant stopped.")
        QMessageBox.information(self, "JARVIS", "Assistant stopped.")

    def open_lab(self) -> None:
        """Launch the Lab module window."""
        if not self.lab_module:
            self.lab_module = LabModule(self.core)
        self.lab_module.activate()

    def indicate_speech(self) -> None:
        """Provide a short cue when speech is detected."""
        QApplication.beep()
