"""Core package for the JARVIS assistant.

Example
-------
>>> from jarvis_core import JarvisCore
>>> JarvisCore().start()
"""

from .core import JarvisCore
from .chatgpt import ChatGPTModule

__all__ = ["JarvisCore", "ChatGPTModule"]
