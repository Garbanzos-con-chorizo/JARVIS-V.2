"""Entry point for launching the JARVIS assistant GUI.

Example
-------
>>> python main.py
"""

from PyQt5.QtWidgets import QApplication

from jarvis.gui import JarvisGUI


def main() -> None:
    qt_app = QApplication([])
    window = JarvisGUI()
    window.show()
    qt_app.exec_()


if __name__ == "__main__":
    main()
