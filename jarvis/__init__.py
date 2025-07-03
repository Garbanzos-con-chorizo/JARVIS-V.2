"""JARVIS assistant package."""

__all__ = [
    "JarvisCore",
    "JarvisGUI",
    "LabModule",
    "ChatGPTModule",
    "ServerApp",
    "DataManager",
]


def __getattr__(name: str):
    """Lazily import modules to avoid circular dependencies."""
    if name == "JarvisCore":
        from jarvis_core import JarvisCore

        return JarvisCore
    if name == "ChatGPTModule":
        from jarvis_core import ChatGPTModule

        return ChatGPTModule
    if name == "JarvisGUI":
        from .gui import JarvisGUI

        return JarvisGUI
    if name == "LabModule":
        from .lab import LabModule

        return LabModule
    if name == "ServerApp":
        from .server import app as ServerApp

        return ServerApp
    if name == "DataManager":
        from .data import DataManager

        return DataManager
    raise AttributeError(name)

