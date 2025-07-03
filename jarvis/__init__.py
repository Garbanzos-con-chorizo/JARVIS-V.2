"""JARVIS assistant package.

Example
-------
>>> from jarvis import JarvisGUI
>>> JarvisGUI().show()
"""

from jarvis_core import JarvisCore, ChatGPTModule
from .gui import JarvisGUI
from .lab import LabModule

__all__ = ["JarvisCore", "JarvisGUI", "LabModule", "ChatGPTModule"]
